#!/usr/bin/env python3
import argparse
import sys
from getpass import getpass

from app import database
from app.auth import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a DiaLab user.")
    parser.add_argument("--username", help="Username for the new account")
    parser.add_argument("--role", default="user", help="Role label (default: user)")
    args = parser.parse_args()

    username = args.username or input("Username: ").strip()
    if not username:
        print("Username cannot be empty.", file=sys.stderr)
        sys.exit(1)

    password = getpass("Password: ")
    confirm = getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        sys.exit(1)
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        sys.exit(1)

    database.init_db()
    existing = database.get_user_by_username(username)
    if existing:
        print("User already exists.", file=sys.stderr)
        sys.exit(1)

    password_hash = hash_password(password)
    user_id = database.create_user(username=username, password_hash=password_hash, role=args.role)

    print(f"Created user '{username}' with id {user_id}.")


if __name__ == "__main__":
    main()
