#!/usr/bin/env python3
"""Update README with the snapshot for a given world (defaults to prod)."""
import argparse
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Inject a world's snapshot into README.md")
    parser.add_argument("world", nargs="?", default="prod", help="World name to display")
    args = parser.parse_args()

    snapshot_path = Path("worlds") / args.world / "snapshot.md"
    if not snapshot_path.exists():
        raise SystemExit(f"Snapshot not found for world '{args.world}' at {snapshot_path}")

    snapshot = snapshot_path.read_text()
    readme_path = Path("README.md")
    readme = readme_path.read_text()

    pattern = r'<!-- SNAPSHOT START -->.*?<!-- SNAPSHOT END -->'
    replacement = f"<!-- SNAPSHOT START -->\n{snapshot}\n<!-- SNAPSHOT END -->"
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    readme_path.write_text(new_readme)
    print(f"✓ README updated using '{args.world}' snapshot")


if __name__ == "__main__":
    main()
