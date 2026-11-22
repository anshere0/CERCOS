#!/usr/bin/env bash
# One-time setup of labels, milestones and issues. Requires GitHub CLI (gh auth login) and scripts/handles.env (see set_handles.sh).
# Run from the repo root AFTER the first push. Safe to re-run: existing labels/milestones are skipped; issues are NOT deduplicated, so run once.
set -euo pipefail
source scripts/handles.env
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Repo: $REPO"
for l in P0 P1 P2 P3 P4 Report task blocked needs-review; do gh label create "$l" --force >/dev/null 2>&1 || true; done
for p in ansh atharva yash anshuman kashish eshwari; do gh label create "owner:$p" --force >/dev/null 2>&1 || true; done
mk() { gh api "repos/$REPO/milestones" -f title="$1" -f due_on="$2" >/dev/null 2>&1 || true; }
mk "M1 Foundation + Bonafide" "2026-12-06T00:00:00Z"
mk "M2 Engine + Data" "2026-12-20T00:00:00Z"
mk "M3 MVP + Field data" "2027-01-03T00:00:00Z"
mk "M4 Phase-I final" "2027-01-10T00:00:00Z"
ms() { # due date -> milestone title
  if [[ "$1" < "2026-12-07" ]]; then echo "M1 Foundation + Bonafide"
  elif [[ "$1" < "2026-12-21" ]]; then echo "M2 Engine + Data"
  elif [[ "$1" < "2027-01-04" ]]; then echo "M3 MVP + Field data"
  else echo "M4 Phase-I final"; fi
}
while IFS=$'\t' read -r who phase due title; do
  [ -z "$who" ] && continue
  var="H_$(echo "$who" | tr a-z A-Z)"; handle="${!var}"
  gh issue create --title "[$phase] $title" --assignee "$handle" \
    --label "$phase" --label task --label "owner:$who" --milestone "$(ms "$due")" \
    --body "Owner: @$handle  |  Phase: $phase  |  Due: $due

Definition of done: merged PR linked with 'Closes #', tests green, peer reviewer approved after running the branch, documented in docs/PHASE_REPORT.md." >/dev/null
  echo "created: $who - $title"
done < scripts/issues.tsv
echo "Done. Project board: create a GitHub Project (Board) and add all issues."
