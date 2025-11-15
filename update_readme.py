#!/usr/bin/env python3
"""Update README with the snapshot for a given world (defaults to prod)."""
import argparse
import re
from pathlib import Path

PROD_MARKERS = ("<!-- SNAPSHOT START -->", "<!-- SNAPSHOT END -->")
STAGING_MARKERS = ("<!-- STAGING SNAPSHOT START -->", "<!-- STAGING SNAPSHOT END -->")


def replace_section(content: str, markers: tuple[str, str], snapshot: str) -> str:
    start, end = markers
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), flags=re.DOTALL)
    replacement = f"{start}\n{snapshot}\n{end}"
    if not pattern.search(content):
        raise SystemExit(f"Marker pair {start}/{end} not found in README.md")
    return pattern.sub(replacement, content)


def main():
    parser = argparse.ArgumentParser(description="Inject a world's snapshot into README.md")
    parser.add_argument("world", nargs="?", default="prod", help="World name to display")
    parser.add_argument(
        "--staging",
        action="store_true",
        help="Update the staging snapshot block instead of the main prod block",
    )
    args = parser.parse_args()

    snapshot_path = Path("worlds") / args.world / "snapshot.md"
    if not snapshot_path.exists():
        raise SystemExit(f"Snapshot not found for world '{args.world}' at {snapshot_path}")

    snapshot = snapshot_path.read_text()
    readme_path = Path("README.md")
    readme = readme_path.read_text()

    markers = STAGING_MARKERS if args.staging else PROD_MARKERS
    new_readme = replace_section(readme, markers, snapshot)

    readme_path.write_text(new_readme)
    target = "staging" if args.staging else "prod"
    print(f"✓ README {target} block updated using '{args.world}' snapshot")


if __name__ == "__main__":
    main()
