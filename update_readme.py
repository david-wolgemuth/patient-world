#!/usr/bin/env python3
"""Update README with snapshot"""
import re
from pathlib import Path

snapshot = Path("snapshot.md").read_text()
readme_path = Path("README.md")
readme = readme_path.read_text()

pattern = r'<!-- SNAPSHOT START -->.*?<!-- SNAPSHOT END -->'
replacement = f"<!-- SNAPSHOT START -->\n{snapshot}\n<!-- SNAPSHOT END -->"
new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

readme_path.write_text(new_readme)
print("✓ README updated")
