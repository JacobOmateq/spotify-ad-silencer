#!/bin/bash
set -e

# Extract version from version.py
VERSION=$(grep '__version__' version.py | cut -d '"' -f2)

if [ -z "$VERSION" ]; then
  echo "Could not find version in version.py!"
  exit 1
fi

echo "Releasing version v$VERSION..."

git add version.py
if ! git diff --cached --quiet; then
  git commit -m "Bump version to v$VERSION"
fi

git tag "v$VERSION"
git push origin main --tags

echo "Tagged and pushed v$VERSION successfully!" 