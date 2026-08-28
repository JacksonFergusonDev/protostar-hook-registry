"""Compiles and validates the Renovate-managed hooks.yaml into a static JSON registry."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Stricter URL regex to ensure clean https git targets
URL_REGEX = re.compile(r"^https://[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")
# Reject commit hashes and prerelease tags (rc, alpha, beta, dev)
PRERELEASE_REGEX = re.compile(
    r"[-._]?(rc|alpha|beta|dev|pre|preview)\d*", re.IGNORECASE
)


def validate_and_compile(source: Path, destination: Path) -> None:
    """Parses hooks.yaml, enforces defensive constraints, and emits registry.json."""
    if not source.is_file():
        print(f"ERROR: Source file '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        with source.open("r", encoding="utf-8") as f:
            data: Any = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(f"ERROR: Malformed YAML in '{source}': {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        print(
            f"ERROR: Root YAML document must be a dictionary, got {type(data).__name__}.",
            file=sys.stderr,
        )
        sys.exit(1)

    repos = data.get("repos")
    if not isinstance(repos, list) or not repos:
        print("ERROR: 'repos' key in YAML must be a non-empty list.", file=sys.stderr)
        sys.exit(1)

    hooks_mapping: dict[str, str] = {}

    for idx, entry in enumerate(repos):
        if not isinstance(entry, dict):
            print(f"ERROR: Entry at index {idx} is not a valid map.", file=sys.stderr)
            sys.exit(1)

        repo_url = entry.get("repo")
        rev = entry.get("rev")

        # 1. Structural Checks
        if not repo_url or not isinstance(repo_url, str):
            print(
                f"ERROR: Invalid or missing 'repo' URL at index {idx}: {repo_url!r}",
                file=sys.stderr,
            )
            sys.exit(1)

        if not rev or not isinstance(rev, str):
            print(
                f"ERROR: Invalid or missing 'rev' for repo '{repo_url}': {rev!r}",
                file=sys.stderr,
            )
            sys.exit(1)

        repo_url = repo_url.strip()
        rev = rev.strip()

        # 2. Protocol and URL Sanitization
        if not repo_url.startswith("https://"):
            print(
                f"ERROR: Insecure or invalid protocol for '{repo_url}'. Must start with https://",
                file=sys.stderr,
            )
            sys.exit(1)

        if not URL_REGEX.match(repo_url):
            print(
                f"ERROR: Repository URL failed structure validation: '{repo_url}'",
                file=sys.stderr,
            )
            sys.exit(1)

        # 3. Revision Hygiene
        if PRERELEASE_REGEX.search(rev):
            print(
                f"ERROR: Unstable/prerelease version detected for '{repo_url}': {rev}",
                file=sys.stderr,
            )
            sys.exit(1)

        if repo_url in hooks_mapping:
            print(f"ERROR: Duplicate repo URL detected: '{repo_url}'", file=sys.stderr)
            sys.exit(1)

        hooks_mapping[repo_url] = rev

    # 4. Final Payload Assembly
    registry = {
        "schema_version": 1,
        "hooks": hooks_mapping,
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_destination = destination.with_suffix(".tmp")

    try:
        with temp_destination.open("w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, sort_keys=True)
            f.write("\n")

        temp_destination.replace(destination)
    except Exception:
        temp_destination.unlink(missing_ok=True)
        raise

    print(
        f"Verified & compiled {len(hooks_mapping)} hook revisions to '{destination}'."
    )


if __name__ == "__main__":
    validate_and_compile(Path("hooks.yaml"), Path("public/registry.json"))
