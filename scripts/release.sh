#!/usr/bin/env bash
# Release discipline, Boston Dynamics style: one VERSION source, one tag,
# one changelog entry. Usage: scripts/release.sh [major|minor|patch]
set -euo pipefail

PART="${1:-patch}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 1. Tests must pass before anything moves.
python -m pytest -q

# 2. Single source of truth: interlock.__version__.
CURRENT=$(python -c "import interlock; print(interlock.__version__)")
NEXT=$(python - "$PART" "$CURRENT" <<'EOF'
import sys
part, current = sys.argv[1], sys.argv[2]
major, minor, patch = (int(x) for x in current.split("."))
if part == "major": major, minor, patch = major + 1, 0, 0
elif part == "minor": minor, patch = minor + 1, 0
else: patch += 1
print(f"{major}.{minor}.{patch}")
EOF
)

# 3. Bump the source, mirror to VERSION.
sed -i "s/__version__ = \".*\"/__version__ = \"$NEXT\"/" src/interlock/__init__.py
echo "$NEXT" > VERSION

# 4. Tag. Push and GitHub Release are deliberate human steps, not scripted.
git add src/interlock/__init__.py VERSION
git commit -m "Release v$NEXT" -q
git tag "v$NEXT"
echo "Tagged v$NEXT. Next: update CHANGELOG.md, git push, cut the GitHub Release."
