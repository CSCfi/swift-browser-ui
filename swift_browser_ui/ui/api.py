"""Project functions for handling API requests from front-end."""

import asyncio
import json
import ssl
import time
import typing
from datetime import datetime

import aioboto3
import aiohttp.web
import aiohttp_session
import botocore.exceptions
import certifi

from swift_browser_ui.common.vault_client import VaultClient
from swift_browser_ui.ui._convenience import (
    ldap_get_project_titles,
    open_upload_runner_session,
    sign,
)
from swift_browser_ui.ui.replicate import ObjectReplicator
from swift_browser_ui.ui.settings import setd
from swift_browser_ui.upload.common import VAULT_CLIENT

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


async def get_os_user(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Fetch the session owning OS user."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        f"API call for username from {request.remote}, sess: {session} :: {time.ctime()}"
    )
    return aiohttp.web.json_response(session["uname"])


async def os_list_projects(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Fetch the projects available for the open session."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    # Fetch project title information from ldap
    titles = await ldap_get_project_titles(session["projects"])
    # Filter out the tokens contained in session token
    return aiohttp.web.json_response(
        [
            {
                "name": v["name"],
                "title": titles.get(v["name"].split("_")[-1]),
                "id": v["id"],
                "tainted": v["tainted"],
            }
            for _, v in session["projects"].items()
        ]
    )


async def swift_list_containers(
    request: aiohttp.web.Request,
) -> aiohttp.web.StreamResponse:
    """Proxy Swift list buckets available to a project."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]

    project = request.match_info["project"]
    request.app["Log"].info(
        "API call for list buckets from "
        f"{request.remote}, session: {session} :: {time.ctime()}"
    )

    # as of v 3.9.1 the return type of query is "MultiMapping[str]"
    # however the actual function returns MultiDictProxy which has copy
    # https://github.com/aio-libs/multidict/blob/master/multidict/_multidict_py.py#L146-L163
    query = request.query.copy()  # type: ignore[attr-defined]
    query["format"] = "json"
    try:
        async with client.get(
            session["projects"][project]["endpoint"],
            headers={"X-Auth-Token": session["projects"][project]["token"]},
            params=query,
        ) as ret:
            resp = aiohttp.web.StreamResponse(status=ret.status)
            await resp.prepare(request)
            if ret.status == 200:
                async for chunk in ret.content.iter_chunked(65535):
                    tasks = [
                        _check_last_modified(request, container)
                        for container in json.loads(chunk)
                    ]
                    ret = await asyncio.gather(*tasks)
                    chunk = json.dumps(ret).encode()
                    await resp.write(chunk)
            await resp.write_eof()
        return resp
    except KeyError:
        raise aiohttp.web.HTTPForbidden(
            reason="Account does not have access to the project."
        )


async def aws_list_buckets(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Proxy bucket list request to a compatible AWS API."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    logger = request.app["Log"]
    project = request.match_info["project"]

    continuation_token = request.query.get("continuation_token", "")
    max_buckets = int(request.query.get("max_buckets", 1000))

    logger.info(
        f"API call to list buckets in {project} from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    logger.debug(
        f"Using {max_buckets} as max buckets and {continuation_token} "
        "as the continuation token."
    )

    creds = await _get_ec2_credentials(session, client, project)
    s3session = aioboto3.Session(
        aws_access_key_id=creds["access"],
        aws_secret_access_key=creds["secret"],
    )

    async with s3session.client(
        "s3",
        region_name="us-east-1",
        endpoint_url=setd["s3api_endpoint"],
        verify=setd["check_certificate"],
    ) as s3_client:
        try:
            bucket_page = await s3_client.list_buckets(
                MaxBuckets=max_buckets, ContinuationToken=continuation_token
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise aiohttp.web.HTTPNotFound(
                    text="Project doesn't have any buckets or storage access."
                )
            elif error_code == "401":
                raise aiohttp.web.HTTPUnauthorized(
                    text="Unauthorized. Credentials might be stale."
                )
            else:
                raise aiohttp.web.HTTPInternalServerError(
                    text="Coudln't retrieve the bucket page from storage."
                )

    bucket_page["Buckets"] = [
        {
            "Name": bucket["Name"],
            "CreationDate": bucket["CreationDate"].isoformat(),
        }
        for bucket in bucket_page["Buckets"]
    ]

    return aiohttp.web.json_response(bucket_page)


async def aws_create_bucket(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Proxy bucket creation request to a compatible AWS API."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    logger = request.app["Log"]
    project = request.match_info["project"]
    bucket = request.match_info["bucket"]

    logger.info(
        f"API call to create bucket {bucket} in {project} from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    creds = await _get_ec2_credentials(session, client, project)
    s3session = aioboto3.Session(
        aws_access_key_id=creds["access"],
        aws_secret_access_key=creds["secret"],
    )

    async with s3session.client(
        "s3",
        region_name="us-east-1",
        endpoint_url=setd["s3api_endpoint"],
        verify=setd["check_certificate"],
    ) as s3_client:
        try:
            await s3_client.create_bucket(Bucket=bucket)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == 403 or error_code == 409:
                raise aiohttp.web.HTTPConflict(text="Bucket already exists")
            if error_code == 400:
                raise aiohttp.web.HTTPClientError
            else:
                raise aiohttp.web.HTTPInternalServerError(
                    text="Could not create requested bucket."
                )

    # Add CORS entries for the newly created bucket to allow access via browser
    await _update_bucket_cors(logger, s3session, bucket)

    return aiohttp.web.Response(status=204, body="")


async def _update_bucket_cors(
    logger,
    s3session: aioboto3.Session,
    bucket: str,
):
    """Update single bucket cors entry."""
    async with s3session.client(
        "s3",
        region_name="us-east-1",
        endpoint_url=setd["s3api_endpoint"],
        verify=setd["check_certificate"],
    ) as s3_client:
        # Fetch the existing bucket CORS information
        cors_list = []
        try:
            cors_response = await s3_client.get_bucket_cors(Bucket=bucket)
            cors_list = cors_response.get("CORSRules", [])
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == 404 or error_code == "NoSuchCORSConfiguration":
                # 404 means there's no existing CORS
                logger.debug(f"No existing CORS in {bucket}, creating from scratch.")
                pass
            elif error_code == 400:
                raise aiohttp.web.HTTPClientError
            else:
                raise aiohttp.web.HTTPInternalServerError
        except botocore.exceptions.ParamValidationError:
            # We don't need to care about the bucket name validation errors for old buckets.
            return

        # Skip immediately if the required CORS entry already exists
        for cors in cors_list:
            if setd["web_app_cors_origin"] in cors["AllowedOrigins"]:
                return

        # Append the SD Connect UI to the CORS listing
        try:
            cors_list.append(
                {
                    "AllowedHeaders": [
                        "*",
                    ],
                    "AllowedMethods": [
                        "PUT",
                        "GET",
                        "DELETE",
                        "POST",
                        "HEAD",
                    ],
                    "AllowedOrigins": [
                        setd["web_app_cors_origin"],
                        f"{setd['web_app_cors_origin']}/",
                    ],
                    "ExposeHeaders": [
                        "*",
                    ],
                    "MaxAgeSeconds": 3600,
                }
            )
            await s3_client.put_bucket_cors(
                Bucket=bucket,
                CORSConfiguration={
                    "CORSRules": cors_list,
                },
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise aiohttp.web.HTTPInternalServerError(
                text=f"Could not add the CORS entry to bucket {bucket}, status {error_code}"
            )


async def aws_update_bucket_cors(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Update a bucket acl to allow access from the configured UI address."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    logger = request.app["Log"]
    project = request.match_info["project"]
    bucket = request.match_info["bucket"]

    logger.info(
        f"API call to update {bucket} CORS in {project} from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    creds = await _get_ec2_credentials(session, client, project)
    s3session = aioboto3.Session(
        aws_access_key_id=creds["access"],
        aws_secret_access_key=creds["secret"],
    )

    await _update_bucket_cors(logger, s3session, bucket)

    return aiohttp.web.Response(status=204, body="")


async def aws_bulk_update_bucket_cors(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Update project buckets with project UI cors."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    logger = request.app["Log"]
    project = request.match_info["project"]

    buckets = request.query.get("buckets", "").split(";")

    logger.info(
        f"API call to allow CORS for all buckets in {project} from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    creds = await _get_ec2_credentials(session, client, project)
    s3session = aioboto3.Session(
        aws_access_key_id=creds["access"],
        aws_secret_access_key=creds["secret"],
    )

    async with s3session.client(
        "s3",
        region_name="us-east-1",
        endpoint_url=setd["s3api_endpoint"],
        verify=setd["check_certificate"],
    ) as s3_client:
        # If we got a list of buckets, just use that instead of paging
        # through the whole project
        if buckets:
            for bucket in buckets:
                try:
                    await _update_bucket_cors(logger, s3session, bucket)
                except Exception as e:
                    request.app["Log"].error(
                        f"Failed to bulk add CORS to bucket {bucket} for reason {e}",
                    )

            return aiohttp.web.Response(status=204, body="")

        continuation_token = ""  # nosec
        try:
            # Using the anti-pattern while since we need to check the continuation token
            # in the end of loop execution, not start
            while True:
                bucket_page = await s3_client.list_buckets(
                    MaxBuckets=100, ContinuationToken=continuation_token
                )

                # Immediately apply new cors to the bucket
                for aws_bucket in bucket_page["Buckets"]:
                    try:
                        await _update_bucket_cors(logger, s3session, aws_bucket["Name"])
                    except Exception as e:
                        request.app["Log"].error(
                            f"Failed to bulk add CORS to bucket {bucket} for reason {e}",
                        )

                # End execution if API tells us there's no more pages
                if (
                    "ContinuationToken" in bucket_page
                    and bucket_page["ContinuationToken"]
                ):
                    continuation_token = bucket_page["ContinuationToken"]
                else:
                    break

        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise aiohttp.web.HTTPInternalServerError(
                text=f"Could not retrieve bucket page for {project}, status {error_code}"
            )

    return aiohttp.web.Response(status=204, body="")


async def _check_last_modified(
    request: aiohttp.web.Request, container: typing.Dict[str, typing.Any]
) -> typing.Dict[str, typing.Any]:
    """Ensure container data includes 'last_modified' key and value.

    :param request: A request instance
    :param data: Containers basic info
    """
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    request.app["Log"].info(
        "API call for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = request.match_info["project"]
    endpoint = session["projects"][project]["endpoint"]
    if "owner" in request.query:
        endpoint = endpoint.replace(project, request.query["owner"])

    # If last_modified is not part of container basic info,
    # head request is made to check container metadata
    # and add last modified data from there.
    if "last_modified" not in container.keys():
        try:
            name = container["name"]
            async with client.head(
                f"{endpoint}/{name}",
                headers={
                    "X-Auth-Token": session["projects"][project]["token"],
                },
            ) as ret:
                date_str = ret.headers["Last-Modified"]
                # Convert the date string to the ISO 8601 format
                date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                iso_8601_str = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")
                container["last_modified"] = iso_8601_str
        # we expect either the header Last Modified to be missing or
        # the value is not what we expect for str to date conversion
        except (KeyError, ValueError) as e:
            # If anything goes wrong, set last_modified key anyway with null value
            request.app["Log"].exception(
                f"something happened when retrieving last modified {e}"
            )
            container["last_modified"] = None
    return container


async def _get_ec2_credentials(session, client, project) -> dict:
    """Return access key and secret key for the given project."""
    # Return credentials from cache if they exist
    if "ec2" in session["projects"][project]:
        return session["projects"][project]["ec2"]

    # Check if there are existing credentials, use the first one
    async with client.get(
        f"{setd['auth_endpoint_url']}/users/{session['uid']}/credentials/OS-EC2",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
    ) as ret:
        creds = await ret.json()
        keys = list(filter(lambda key: key["tenant_id"] == project, creds["credentials"]))

    if len(keys) > 0:
        return keys[0]

    # Create new credentials if there are no existing ones
    async with client.post(
        f"{setd['auth_endpoint_url']}/users/{session['uid']}/credentials/OS-EC2",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
        json={
            "tenant_id": project,
        },
    ) as ret:
        session["projects"][project]["ec2"] = (await ret.json())["credential"]
        session.changed()
        return session["projects"][project]["ec2"]


async def keystone_gen_ec2(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Acquire and serve EC2 credentials for the given project."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]

    request.app["Log"].info(
        f"API call for fetching ec2 credentials from {request.remote}, sess {session}"
    )

    # Fetch the ec2 credentials if they're not already cached in the session.
    return aiohttp.web.json_response(await _get_ec2_credentials(session, client, project))


async def replicate_bucket(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Replicate bucket using ec2 credentials."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    logger = request.app["Log"]

    project = request.match_info["project"]
    bucket = request.match_info["bucket"]
    source_bucket = request.query["from_bucket"]
    source_project = request.query["from_project"]

    vault_client: VaultClient = request.app[VAULT_CLIENT]

    logger.info(
        f"API call to replicate bucket {source_bucket} to {bucket} from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    creds = await _get_ec2_credentials(session, client, project)

    s3session = aioboto3.Session(
        aws_access_key_id=creds["access"],
        aws_secret_access_key=creds["secret"],
    )

    async with s3session.client(
        "s3",
        region_name="us-east-1",
        endpoint_url=setd["s3api_endpoint"],
        verify=setd["check_certificate"],
    ) as s3_client:

        replicator = ObjectReplicator(
            s3_client,
            vault_client,
            project,
            bucket,
            source_project,
            source_bucket,
            request.query["project_name"] if "project_name" in request.query else "",
            (
                request.query["from_project_name"]
                if "from_project_name" in request.query
                else ""
            ),
        )

    # Create destination bucket
    await replicator.create_destination_bucket()
    # Add CORS entries for the newly created bucket to allow access via browser
    await _update_bucket_cors(logger, s3session, bucket)

    asyncio.create_task(replicator.replicate_objects())
    return aiohttp.web.HTTPAccepted(text="Replication started")


async def get_upload_session(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Return a pre-signed upload runner session for upload target."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for object upload runner info request from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = ""
    if "project" in request.query:
        project = request.query["project"]
    runner_id = await open_upload_runner_session(request, project=project)
    path = f"/{request.match_info['project']}/{request.match_info['container']}"
    signature = await sign(3600, path)
    return aiohttp.web.json_response(
        {
            "id": runner_id,
            "url": f"{setd['upload_external_endpoint']}{path}",
            "host": setd["upload_external_endpoint"],
            "signature": signature,
        }
    )


async def get_crypted_upload_session(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Return a pre-signed upload runner session for upload target."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for object upload runner info request from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = ""
    if "project" in request.query:
        project = request.query["project"]
    runner_id = await open_upload_runner_session(request, project=project)
    path = (
        f"/cryptic/{request.match_info['project']}/{request.match_info['container']}"
        + f"/{request.match_info['object_name']}"
    )
    signature = await sign(3600, path)
    ws_path = (
        f"/cryptic/{request.match_info['project']}/{request.match_info['container']}"
        + f"/{request.match_info['object_name']}"
    )
    ws_sign_path = (
        f"/cryptic/{request.match_info['project']}/{request.match_info['container']}"
        + f"/{request.match_info['object_name']}"
    )
    ws_signature = await sign(3600, ws_sign_path)
    return aiohttp.web.json_response(
        {
            "id": runner_id,
            "url": f"{setd['upload_external_endpoint']}{path}",
            "wsurl": f"{setd['upload_external_endpoint']}{ws_path}".replace(
                "https", "wss"
            ),
            "host": setd["upload_external_endpoint"],
            "signature": signature,
            "wssignature": ws_signature,
        }
    )


async def close_upload_session(
    request: aiohttp.web.Request,
    project: str = "",
) -> aiohttp.web.Response:
    """Close the upload session opened for the token."""
    session = await aiohttp_session.get_session(request)
    status = 204
    if not project:
        project = request.match_info["project"]
    if "runner" in session["projects"][project]:
        runner = session["projects"][project]["runner"]
        client = request.app["api_client"]
        path = f"{setd['upload_internal_endpoint']}/{project}"
        signature = await sign(3600, f"/{project}")
        async with client.delete(
            path,
            cookies={"RUNNER_SESSION_ID": runner},
            params=signature,
            ssl=ssl_context,
        ) as resp:
            status = resp.status
        session["projects"][project].pop("runner")
        session.changed()
    return aiohttp.web.Response(status=status)
