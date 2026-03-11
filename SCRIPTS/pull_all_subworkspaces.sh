#!/usr/bin/env bash
# Pull all subtree subworkspaces. Ensures remotes exist and are fetched, then runs subtree pull (fetch+merge) only; does not push.
# Safe to run from any subdirectory; changes to repo root. Non-interactive for autonomous use (e.g. Cursor Cloud Agent).
set -e
set -u

# --- Preamble: deps and repo root ---
if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not in PATH." >&2
  exit 1
fi
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || true
if [[ -z "${ROOT:-}" ]]; then
  echo "Error: Not inside a git repository." >&2
  exit 1
fi
cd "$ROOT"
export GIT_TERMINAL_PROMPT=0

# --- Canonical remotes (name, URL, branch). LFS skip-smudge applied later for pyPhoCoreHelpers and pyPhoPlaceCellAnalysis. ---
ensure_remote() {
  local name="$1"
  local url="$2"
  local current_url
  current_url=$(git remote get-url "$name" 2>/dev/null) || true
  if [[ -z "${current_url:-}" ]]; then
    echo "Ensuring remotes: adding $name..."
    git remote add "$name" "$url"
  elif [[ "$current_url" != "$url" ]]; then
    echo "Ensuring remotes: setting URL for $name..."
    git remote set-url "$name" "$url"
  fi
  echo "Fetching $name..."
  git fetch "$name"
}

echo "Ensuring remotes and fetching..."
ensure_remote "remote-NeuroPy" "https://github.com/CommanderPho/NeuroPy.git"
ensure_remote "remote-pyPhoCoreHelpers" "https://github.com/CommanderPho/pyPhoCoreHelpers.git"
ensure_remote "remote-pyPhoPlaceCellAnalysis" "https://github.com/CommanderPho/pyPhoPlaceCellAnalysis.git"
ensure_remote "remote-Spike3D" "https://github.com/CommanderPho/Spike3D.git"

# --- Subtree pull (continue-and-report: one failure does not block others) ---
failed=()
pull_one() {
  local prefix="$1"
  local remote="$2"
  local branch="$3"
  local use_lfs_skip="${4:-0}"
  echo "Pulling subtree $prefix..."
  if [[ "$use_lfs_skip" == "1" ]]; then
    if ! GIT_LFS_SKIP_SMUDGE=1 git subtree pull --prefix="$prefix" "$remote" "$branch" --squash; then
      failed+=("$prefix")
    fi
  else
    if ! git subtree pull --prefix="$prefix" "$remote" "$branch" --squash; then
      failed+=("$prefix")
    fi
  fi
}

pull_one "NeuroPy" "remote-NeuroPy" "feature/safe-advance" "0"
pull_one "pyPhoCoreHelpers" "remote-pyPhoCoreHelpers" "release/pho-diba-2025-paper" "1"
pull_one "pyPhoPlaceCellAnalysis" "remote-pyPhoPlaceCellAnalysis" "develop" "1"
pull_one "Spike3D" "remote-Spike3D" "master" "0"

if [[ ${#failed[@]} -gt 0 ]]; then
  echo "Failed subtrees: ${failed[*]}" >&2
  exit 1
fi
echo "All subtree pulls completed."
exit 0
