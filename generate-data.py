#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import io
import json
import os
import pathlib
import random
import socket
import time

import lorem
import requests

keystone_url_template = "http://{host}:{port}/v3".format
swift_url_template = "http://{host}:{port}/auth/v1.0".format


def wait_for_port(url, timeout=5.0, verbose=False, quiet=False):
    start_time = time.perf_counter()

    while True:
        try:
            r = requests.head(url)
            if verbose and not quiet:
                print()
                print(f"{url} seems to be accepting connections")
            break
        except Exception as ex:
            current = time.perf_counter() - start_time
            print(f"Waiting for {url} {current:.2f}s elapsed", end="\r")
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(
                    "Waited too long for {} to start accepting "
                    "connections.".format(url)
                ) from ex
            time.sleep(1)
    end = time.perf_counter() - start_time
    if end > 1 and not quiet:
        print(f"Waited {end} for {url}", end="\r")
        print()


def get_tempauth_token(
    host="localhost", port=8080, username="test:tester", password="testing"
) -> str:
    auth = requests.get(
        f"http://{host}:{port}/auth/v1.0",
        headers={
            "X-Storage-User": username,
            "X-Storage-Pass": password,
        },
    )
    swift_url = auth.headers["X-Storage-Url"]
    token = auth.headers["X-Auth-Token"]
    return swift_url, token


def get_keystone_token(
    host="localhost",
    port=5000,
    username="swift",
    password="veryfast",
    project="service",
) -> str:
    keystone_url = f"http://{host}:{port}/v3"

    auth_data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "domain": {"id": "default"},
                        "name": username,
                        "password": password,
                    }
                },
            },
            "scope": {"project": {"name": project, "domain": {"id": "default"}}},
        }
    }

    auth = requests.request("POST", f"{keystone_url}/auth/tokens", json=auth_data)
    result = auth.json()
    if("error" in result):
        raise Exception("Keystone auth failed: {}".format(result["error"]["message"]))
    swift_url = result["token"]["catalog"][1]["endpoints"][0]["url"]
    token = auth.headers["X-Subject-Token"]
    return swift_url, token


def get_account_obj_count(swift_url: str, token: str) -> int:
    obj_count = requests.head(
        swift_url, params={"format": "json"}, headers={"X-Auth-Token": token}
    )
    return int(obj_count.headers["X-Account-Object-Count"])


def get_all_containers_obj_count(swift_url: str, token: str) -> int:
    total = 0
    account_meta = requests.get(
        swift_url, params={"format": "json"}, headers={"X-Auth-Token": token}
    )
    for container in account_meta.json():
        container_meta = requests.get(
            swift_url + "/" + container["name"],
            params={"format": "json"},
            headers={"X-Auth-Token": token},
        )
        total += int(container_meta.headers["X-Container-Object-Count"])

    return total


def generate_data(
    swift_url: str, token: str, n_containers=5, n_objects=5, verbose=False, quiet=False
):
    if not quiet:
        start = time.perf_counter()
        print()
        print(f"Creating {n_containers} containers with {n_objects} objects each")
    for i in range(0, n_containers):
        container = f"bucket-{i:03d}"
        r = requests.put(f"{swift_url}/{container}", headers={"X-Auth-Token": token})
        if r.status_code not in {201, 202}:
            print(f"ERROR {r.status_code} {container}")
        if verbose and not quiet:
            print(f"{r.status_code} {container}")
        for _ in range(0, n_objects):
            filename = hashlib.sha1(os.urandom(256)).hexdigest() + ".txt"
            r = requests.put(
                f"{swift_url}/{container}/{filename}",
                headers={"X-Auth-Token": token, "Content-Type": "text/plain"},
                files={"files": (filename, lorem.get_paragraph())},
            )
            if r.status_code != 201:
                print(f"ERROR {r.status_code} {filename}")
            if verbose and not quiet:
                print(f"{r.status_code} {filename}")
        if verbose and not quiet:
            print()
    if not quiet:
        end = time.perf_counter() - start
        print(f"Done in {end:.2f} seconds.")


def populate_from_json(
    swift_url: str, token: str, data: dict, verbose=False, quiet=False
):
    if not quiet:
        start = time.perf_counter()
        print()
        n_containers = len(data)
        n_objects = sum( (len(cont["objects"]) for cont in data) )
        print(f"Creating {n_containers} containers with {n_objects} objects in total")

    for container in data:
        container_name = container["name"]
        headers = {
            f"X-Container-Meta-{key}": item for key, item in container["meta"].items()
        }
        headers["X-Auth-Token"] = token
        r = requests.put(f"{swift_url}/{container_name}", headers=headers)
        if r.status_code not in {201, 202}:
            print(f"ERROR {r.status_code} {container_name}")
        if verbose and not quiet:
            print(f"{r.status_code} {container_name}")
        for obj in container["objects"]:
            obj_name = obj["name"]
            headers = {
                f"X-Object-Meta-{key}": item for key, item in obj["meta"].items()
            }
            headers["X-Auth-Token"] = token
            headers["Content-Type"] = "text/plain"
            r = requests.put(
                f"{swift_url}/{container_name}/{obj_name}",
                headers=headers,
                files={"files": (obj["name"], obj["content"])},
            )
            if r.status_code != 201:
                print(f"ERROR {r.status_code} {obj_name}")
            if verbose and not quiet:
                print(f"{r.status_code} {obj_name}")
    if not quiet:
        end = time.perf_counter() - start
        print(f"Done in {end:.2f} seconds.")


def run(
    swift_url: str,
    token: str,
    json_path=None,
    n_containers=5,
    n_objects=3,
    timeout=60,
    runs=2,
    verbose=False,
    quiet=False,
):
    for _ in range(0, runs):
        start_timeout = time.perf_counter()
        existing_objs = get_account_obj_count(swift_url, token)
        containers_obj_count = 0
        if json_path and os.path.isfile(json_path):
            with open(json_path, "r") as fp:
                data = json.load(fp)
            if not quiet:
                print(f"Populating data from {json_path}")
            for container in data:
                containers_obj_count += len(container["objects"])
            n_containers = len(data)
            n_objects = sum( (len(cont["objects"]) for cont in data) )
            populate_from_json(swift_url, token, data, verbose, quiet)
        else:
            containers_obj_count = get_all_containers_obj_count(swift_url, token)
            generate_data(swift_url, token, n_containers, n_objects, verbose, quiet)

        if verbose and not quiet:
            print()
            print("Wait until metadata updates")

        expected = existing_objs + n_objects

        print()
        obj = get_account_obj_count(swift_url, token)
        start = time.perf_counter()
        while True:
            obj = get_account_obj_count(swift_url, token)
            containers_obj_count = get_all_containers_obj_count(swift_url, token)
            # print(obj, containers_obj_count, expected, containers_obj_count - existing_objs)
            if obj == containers_obj_count:
                break
            current = time.perf_counter() - start
            if not quiet:
                print(
                    f"Current: {obj}, expected: {expected}, started with {existing_objs}. Created {containers_obj_count - existing_objs} new objects. Waited for {current:.2f} seconds",
                    end="\r",
                )
            if time.perf_counter() - start_timeout >= timeout:
                raise TimeoutError("Waited too long for metadata to update")
            time.sleep(1)
        end = time.perf_counter() - start
        if not quiet:
            print(
                f"We got {obj} objects, expected: {expected}, started with {existing_objs}. Created {containers_obj_count - existing_objs} new objects. Done in {end:.2f} seconds", end="\r"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate containers and objects in swift object storage, and wait for metadata to be updated.",
        epilog="By default, runs with a Swift TempAuth account. use '--keystone' to authenticate agains keystone.",
    )
    parser.add_argument(
        "--host", default="localhost", help="Target swift backend host to run against"
    )
    parser.add_argument(
        "--keystone-port",
        type=int,
        default=5000,
        help="Target keystone backend port to run against",
    )
    parser.add_argument(
        "--swift-port",
        type=int,
        default=8080,
        help="Target swift backend port to run against",
    )
    parser.add_argument(
        "--keystone",
        action="store_true",
        help="Authenticate against keystone. This option changes the default username (swift) and password (veryfast)",
    )

    parser.add_argument(
        "--username",
        default="test:tester",
        help="Defaults to a swift test username (test:tester)",
    )
    parser.add_argument(
        "--password",
        default="testing",
        help="Defaults to a swift test password (testing)",
    )
    parser.add_argument(
        "--project", default="service", help="Keystone project. Defaults to (service)"
    )

    parser.add_argument(
        "--containers", type=int, default=10, help="Number of containers to create"
    )
    parser.add_argument(
        "--objects",
        type=int,
        default=15,
        help="Number of objects per container to create",
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of times to repeat the operations. Useful to watch and benchmark the backend",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Maximum time to wait before data is generated and metadata is updated, for each run",
    )

    parser.add_argument(
        "--from-json",
        type=pathlib.Path,
        default=None,
        help="Generate data from a pre-existing json structure",
    )

    outtput_group = parser.add_mutually_exclusive_group()
    outtput_group.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )
    outtput_group.add_argument(
        "-q", "--quiet", action="store_true", help="Don't print to console"
    )

    args = parser.parse_args()

    if not args.quiet:
        total_start = time.perf_counter()

    if args.keystone:
        wait_for_port(
            keystone_url_template(host=args.host, port=args.keystone_port),
            timeout=args.timeout,
            verbose=args.verbose,
            quiet=args.quiet,
        )
        wait_for_port(
            swift_url_template(host=args.host, port=args.swift_port),
            timeout=args.timeout,
            verbose=args.verbose,
            quiet=args.quiet,
        )
        swift_url, token = get_keystone_token(
            args.host, args.keystone_port, args.username, args.password, args.project
        )
    else:
        wait_for_port(
            swift_url_template(host=args.host, port=args.swift_port),
            timeout=args.timeout,
            verbose=args.verbose,
            quiet=args.quiet,
        )
        swift_url, token = get_tempauth_token(
            args.host, args.swift_port, args.username, args.password
        )

    if args.verbose and not args.quiet:
        print(f"Got token: {token}. Swift url: {swift_url}")
        print(f"Generating data ...")

    run(
        swift_url,
        token,
        args.from_json,
        args.containers,
        args.objects,
        args.timeout,
        args.runs,
        verbose=args.verbose,
        quiet=args.quiet,
    )

    if not args.quiet:
        total_end = time.perf_counter() - total_start
        print()
        print(f"Completed in {total_end:.2f} seconds")
