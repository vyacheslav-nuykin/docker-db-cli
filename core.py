#!/usr/bin/env python3
# Copyright 2025 Vyacheslav Nuykin. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Enterprise-grade CLI tool for launching database containers via Docker.

Supports PostgreSQL, MySQL, Redis, MongoDB, and custom containers.
Designed for automation, CI/CD, and clean integration with GUI wrappers.

Usage:
  python db.py postgres --name mydb --user admin --password secret --db myapp --port 5432 --image postgres:16
  python db.py stop --name mydb
"""

import argparse
import sys
from pathlib import Path
import subprocess

# Supported Docker executable paths (Linux and Windows)
DOCKER_PATHS = [
    "/usr/bin/docker",
    "/usr/local/bin/docker",
    "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe",
]


def find_docker() -> str:
    """Locate Docker executable. Exit if not found."""
    for path in DOCKER_PATHS:
        if Path(path).exists():
            return path
    print("❌ Docker not found. Please install Docker and ensure it's in your PATH.", file=sys.stderr)
    sys.exit(1)


def run_docker_command(args: list[str]) -> subprocess.CompletedProcess:
    """Execute Docker command safely without shell injection."""
    docker_bin = find_docker()
    cmd = [docker_bin] + args
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as e:
        print(f"Failed to run Docker command: {e}", file=sys.stderr)
        sys.exit(1)


def container_exists(name: str) -> bool:
    """Check if a container with the given name already exists."""
    result = run_docker_command(["ps", "-a", "--format", "{{.Names}}"])
    return name in result.stdout.splitlines()


def stop_and_remove_container(name: str) -> None:
    """Stop and remove container by name."""
    print(f"Stopping and removing container '{name}'...")
    run_docker_command(["stop", name])
    result = run_docker_command(["rm", name])
    if result.returncode == 0:
        print(f"Container '{name}' removed successfully.")
    else:
        print(f"Container '{name}' may not exist or could not be removed.")


def run_container(
    name: str,
    image: str,
    env_vars: list[str] | None = None,
    port_mapping: str | None = None,
) -> None:
    """
    Launch a Docker container with idempotent behavior.

    If container exists, it is stopped and removed before launch.
    """
    if container_exists(name):
        print(f"Container '{name}' already exists. Replacing it...")
        stop_and_remove_container(name)

    cmd = ["run", "--name", name]
    if env_vars:
        for var in env_vars:
            cmd.extend(["-e", var])
    if port_mapping:
        cmd.extend(["-p", port_mapping])
    cmd.extend(["-d", image])

    print(f"Starting container '{name}' from image '{image}'...")
    result = run_docker_command(cmd)
    if result.returncode == 0:
        print(f"Container '{name}' is now running.")
    else:
        print(f"Failed to start container:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)


def validate_port(value: str) -> int:
    """Validate and convert port string to integer."""
    try:
        port = int(value)
        if 1 <= port <= 65535:
            return port
        raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid port: {value}. Must be 1-65535.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Launch and manage database containers via Docker.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # === STOP command ===
    stop_parser = subparsers.add_parser("stop", help="Stop and remove a container")
    stop_parser.add_argument("--name", required=True, help="Container name")

    # === POSTGRES command ===
    pg_parser = subparsers.add_parser("postgres", help="Launch PostgreSQL container")
    pg_parser.add_argument("--name", required=True, help="Container name")
    pg_parser.add_argument("--user", required=True, help="PostgreSQL user")
    pg_parser.add_argument("--password", required=True, help="PostgreSQL password")
    pg_parser.add_argument("--db", required=True, help="Database name")
    pg_parser.add_argument("--port", required=True, type=validate_port, help="Host port to bind")
    pg_parser.add_argument("--image", default="postgres:16", help="Docker image (default: postgres:16)")

    # === MYSQL command ===
    mysql_parser = subparsers.add_parser("mysql", help="Launch MySQL container")
    mysql_parser.add_argument("--name", required=True, help="Container name")
    mysql_parser.add_argument("--user", required=True, help="MySQL user")
    mysql_parser.add_argument("--password", required=True, help="MySQL password (also used as root password)")
    mysql_parser.add_argument("--db", required=True, help="Database name")
    mysql_parser.add_argument("--port", required=True, type=validate_port, help="Host port to bind")
    mysql_parser.add_argument("--image", default="mysql:8", help="Docker image (default: mysql:8)")

    # === REDIS command ===
    redis_parser = subparsers.add_parser("redis", help="Launch Redis container")
    redis_parser.add_argument("--name", required=True, help="Container name")
    redis_parser.add_argument("--port", required=True, type=validate_port, help="Host port to bind")
    redis_parser.add_argument("--image", default="redis:7", help="Docker image (default: redis:7)")

    # === MONGODB command ===
    mongo_parser = subparsers.add_parser("mongo", help="Launch MongoDB container")
    mongo_parser.add_argument("--name", required=True, help="Container name")
    mongo_parser.add_argument("--user", required=True, help="MongoDB root user")
    mongo_parser.add_argument("--password", required=True, help="MongoDB root password")
    mongo_parser.add_argument("--db", required=True, help="Initial database name")
    mongo_parser.add_argument("--port", required=True, type=validate_port, help="Host port to bind")
    mongo_parser.add_argument("--image", default="mongo:7", help="Docker image (default: mongo:7)")

    # === CUSTOM command ===
    custom_parser = subparsers.add_parser("custom", help="Launch custom container")
    custom_parser.add_argument("--name", required=True, help="Container name")
    custom_parser.add_argument("--image", required=True, help="Docker image")
    custom_parser.add_argument("--port", type=validate_port, help="Host port to bind (optional)")
    custom_parser.add_argument("--env", nargs="*", help="Environment variables (e.g., KEY=VALUE)")

    args = parser.parse_args()

    if args.command == "stop":
        stop_and_remove_container(args.name)

    elif args.command == "postgres":
        env = [
            f"POSTGRES_USER={args.user}",
            f"POSTGRES_PASSWORD={args.password}",
            f"POSTGRES_DB={args.db}",
        ]
        run_container(
            name=args.name,
            image=args.image,
            env_vars=env,
            port_mapping=f"{args.port}:5432",
        )

    elif args.command == "mysql":
        env = [
            f"MYSQL_ROOT_PASSWORD={args.password}",
            f"MYSQL_DATABASE={args.db}",
            f"MYSQL_USER={args.user}",
            f"MYSQL_PASSWORD={args.password}",
        ]
        run_container(
            name=args.name,
            image=args.image,
            env_vars=env,
            port_mapping=f"{args.port}:3306",
        )

    elif args.command == "redis":
        run_container(
            name=args.name,
            image=args.image,
            port_mapping=f"{args.port}:6379",
        )

    elif args.command == "mongo":
        env = [
            f"MONGO_INITDB_ROOT_USERNAME={args.user}",
            f"MONGO_INITDB_ROOT_PASSWORD={args.password}",
            f"MONGO_INITDB_DATABASE={args.db}",
        ]
        run_container(
            name=args.name,
            image=args.image,
            env_vars=env,
            port_mapping=f"{args.port}:27017",
        )

    elif args.command == "custom":
        run_container(
            name=args.name,
            image=args.image,
            env_vars=args.env,
            port_mapping=f"{args.port}:{args.port}" if args.port else None,
        )


if __name__ == "__main__":
    main()
