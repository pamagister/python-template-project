#!/usr/bin/env bash
set -euo pipefail

previous_tag=$(git tag --sort=-creatordate | sed -n 2p)

if [ -z "$previous_tag" ]; then
  # Erster Tag im Repository: Es gibt noch keinen Vorgänger-Tag,
  # daher alle Commits in den Changelog einbeziehen.
  git shortlog | sed 's/^./    &/'
else
  git shortlog "${previous_tag}.." | sed 's/^./    &/'
fi
