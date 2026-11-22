#!/usr/bin/env bash
# Usage: bash scripts/set_handles.sh <ansh> <atharva> <yash> <anshuman> <kashish> <eshwari>   (GitHub usernames, no @)
set -euo pipefail
[ "$#" -eq 6 ] || { echo "Usage: $0 ansh atharva yash anshuman kashish eshwari"; exit 1; }
cat > scripts/handles.env << EOT
H_ANSH=$1
H_ATHARVA=$2
H_YASH=$3
H_ANSHUMAN=$4
H_KASHISH=$5
H_ESHWARI=$6
EOT
sed -i "s/HANDLE_ANSHUMAN/$4/g; s/HANDLE_ANSH/$1/g; s/HANDLE_ATHARVA/$2/g; s/HANDLE_YASH/$3/g; s/HANDLE_KASHISH/$5/g; s/HANDLE_ESHWARI/$6/g" .github/CODEOWNERS
echo "CODEOWNERS and scripts/handles.env updated. Commit them on a branch and open a PR."
