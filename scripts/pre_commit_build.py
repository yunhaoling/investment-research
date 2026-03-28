#!/usr/bin/env python3
"""
pre-commit hook wrapper: run build.py and stage generated HTML files.
Called by pre-commit framework — do not run directly.
"""
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent.parent

# Run build.py using the same Python (pre-commit's managed venv)
result = subprocess.run([sys.executable, str(root / "build.py")], cwd=root)
if result.returncode != 0:
    sys.exit(result.returncode)

# Stage all generated HTML files so they're included in the commit
subprocess.run(["git", "add", "index.html"], cwd=root)
for html in sorted(root.glob("companies/**/*.html")):
    subprocess.run(["git", "add", str(html.relative_to(root))], cwd=root)
