#!/usr/bin/env bash
# Run INSIDE the CERCOS repo folder (the one that contains TEAM.md) BEFORE the first push.
# It moves the six Word guides out of the repo and prints what is left to do. It does not push anything.
set -euo pipefail
[ -f TEAM.md ] || { echo "TEAM.md not found. cd into the CERCOS repo folder first."; exit 1; }
mkdir -p ../_guides_docx
shopt -s nullglob
for f in *Step-by-Step*.docx; do mv -v "$f" ../_guides_docx/; done
echo
echo "Repo root now contains:"; ls
echo
echo "Checks:"
n=$(find . -name AGENTS.md -not -path './node_modules/*' | wc -l); echo "AGENTS.md files: $n (must be 1)"
grep -c "HANDLE_" .github/CODEOWNERS | xargs echo "CODEOWNERS placeholders left:"
echo
echo "Next: git init && git add . && git commit -m 'chore: bootstrap team pack' && git branch -M main && git remote add origin https://github.com/anshere0/CERCOS.git && git push -u origin main"
