"""Common resources for swift-upload-runner."""


import typing


import aiohttp.web
import keystoneauth1.session


import swift_upload_runner.upload as upload


def generate_download_url(
    host: str,
    container: typing.Union[str, None] = None,
    object_name: typing.Union[str, None] = None,
) -> str:
    """Generate the download URL to use."""
    if not container and not object_name:
        return host
    elif not object_name:
        return f"{host}/{container}"
    # The object_name based URL works fine with prefixes as well
    return f"{host}/{container}/{object_name}"


def get_download_host(auth: keystoneauth1.session.Session, project: str) -> str:
    """Get the actual download host with shared container support."""
    ret = auth.get_endpoint(service_type="object-store")

    if project not in ret:
        ret = ret.replace(ret.split("/")[-1], project)

    return ret


def get_session_id(request: aiohttp.web.Request) -> str:
    """Return the session id from request."""
    try:
        return request.cookies["RUNNER_SESSION_ID"]
    except KeyError:
        try:
            return request.query["session"]
        except KeyError:
            raise aiohttp.web.HTTPUnauthorized(reason="Missing runner session ID")


def get_auth_instance(request: aiohttp.web.Request) -> keystoneauth1.session.Session:
    """Return the session specific keystone auth instance."""
    return request.app[get_session_id(request)]["auth"]


async def parse_multipart_in(
    request: aiohttp.web.Request,
) -> typing.Tuple[typing.Dict[str, typing.Any], aiohttp.MultipartReader]:
    """Parse the form headers into a dictionary and chunk data as reader."""
    reader = await request.multipart()

    ret_d = {}

    while True:
        field = await reader.next()
        if field.name == "file":  # type: ignore
            ret_d["filename"] = field.filename  # type: ignore
            return ret_d, field  # type: ignore
        if field.name == "resumableChunkNumber":  # type: ignore
            ret_d["resumableChunkNumber"] = int(await field.text())  # type: ignore
        else:
            ret_d[
                str(field.name)  # type: ignore
            ] = await field.text()  # type: ignore


async def get_upload_instance(
    request: aiohttp.web.Request,
    pro: str,
    cont: str,
    p_query: typing.Optional[dict] = None,
) -> upload.ResumableFileUploadProxy:
    """Return the specific upload proxy for the resumable upload."""
    session = get_session_id(request)

    if p_query:
        query: dict = p_query
    else:
        query = request.query  # type: ignore

    # Check the existence of the dictionary structure
    try:
        request.app[session]["uploads"][pro]
    except KeyError:
        request.app[session]["uploads"][pro] = {}

    try:
        request.app[session]["uploads"][pro][cont]
    except KeyError:
        request.app[session]["uploads"][pro][cont] = {}

    try:
        ident = query["resumableIdentifier"]
    except KeyError:
        raise aiohttp.web.HTTPBadRequest(reason="Malformed query string")
    try:
        upload_session = request.app[session]["uploads"][pro][cont][ident]
    except KeyError:
        auth = get_auth_instance(request)
        upload_session = upload.ResumableFileUploadProxy(
            auth, query, request.match_info, request.app["client"]
        )
        await upload_session.a_check_container()
        request.app[session]["uploads"][pro][cont][ident] = upload_session

    return upload_session


def get_path_from_list(to_parse: typing.List[str], path_prefix: str) -> str:
    """Parse a path from a list of path parts."""
    ret = path_prefix

    for i in to_parse:
        ret += f"/{i}"

    return ret.lstrip("/").rstrip("/")


async def handle_delete_preflight(
    _: typing.Union[aiohttp.web.Request, None]
) -> aiohttp.web.Response:
    """Serve correct response headers to allowed DELETE preflight query."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS, DELETE",
            "Access-Control-Max-Age": "84600",
        }
    )
    return resp
