#!/usr/bin/env bash
# Convert submodules to subtrees. Run from repo root.
set -e

convert_submodule_to_subtree() {
    local RepoPath="$1"
    local RemoteUrl="$2"
    local Branch="$3"
    local remoteName="remote-$RepoPath"
    local branchToUse="$Branch"
    local symref

    echo "--- Converting $RepoPath to Subtree ---"

    # 1. Remove Submodule from Git index
    git rm --cached "$RepoPath"

    # Remove submodule entry from .gitmodules if present
    if [[ -f .gitmodules ]]; then
        local skip=0
        while IFS= read -r line; do
            if [[ "$line" =~ ^\[submodule\ \"$RepoPath\"\] ]]; then
                skip=1
                continue
            fi
            if [[ $skip -eq 1 ]]; then
                if [[ "$line" =~ ^\[submodule ]]; then
                    skip=0
                    printf '%s\n' "$line"
                fi
                continue
            fi
            printf '%s\n' "$line"
        done < .gitmodules > .gitmodules.tmp
        if [[ -s .gitmodules.tmp ]] && [[ -n "$(tr -d '[:space:]' < .gitmodules.tmp)" ]]; then
            mv .gitmodules.tmp .gitmodules
        else
            rm -f .gitmodules.tmp .gitmodules
        fi
    fi

    # 2. Clean up .git/config and .git/modules
    git config -f .git/config --remove-section "submodule.$RepoPath" 2>/dev/null || true
    if [[ -d ".git/modules/$RepoPath" ]]; then
        rm -rf ".git/modules/$RepoPath"
    fi

    # 3. Physically remove the folder to prepare for subtree injection
    if [[ -d "$RepoPath" ]]; then
        rm -rf "$RepoPath"
    fi

    # 4. Commit the removal of the submodule
    git add .
    git commit -m "Remove submodule: $RepoPath to prepare for subtree conversion"

    # 5. Add the Remote and Fetch
    git remote add "$remoteName" "$RemoteUrl"
    git fetch "$remoteName"

    # 6. Add as Subtree (using --squash to keep history clean)
    if [[ -z "$branchToUse" ]]; then
        symref=$(git ls-remote --symref "$RemoteUrl" HEAD 2>/dev/null) || true
        if [[ "$symref" =~ ref:[[:space:]]+refs/heads/([^[:space:]]+) ]]; then
            branchToUse="${BASH_REMATCH[1]}"
        fi
        [[ -z "$branchToUse" ]] && branchToUse="main"
    fi
    git subtree add --prefix="$RepoPath" "$remoteName" "$branchToUse" --squash

    echo "Successfully converted $RepoPath!"
}

# Execution list: RepoPath|RemoteUrl|Branch (empty = auto-detect from remote HEAD)
SUBMODULES=(
    "NeuroPy|https://github.com/CommanderPho/NeuroPy.git|feature/safe-advance"
    "pyPhoCoreHelpers|https://github.com/CommanderPho/pyPhoCoreHelpers.git|release/pho-diba-2025-paper"
    "pyPhoPlaceCellAnalysis|https://github.com/CommanderPho/pyPhoPlaceCellAnalysis.git|develop"
    "Spike3D|https://github.com/CommanderPho/Spike3D.git|master"
)

failed=()
for entry in "${SUBMODULES[@]}"; do
    name="${entry%%|*}"
    rest="${entry#*|}"
    url="${rest%%|*}"
    branch="${rest#*|}"
    ( convert_submodule_to_subtree "$name" "$url" "$branch" ) || failed+=("$name")
done
converted=$((${#SUBMODULES[@]} - ${#failed[@]}))
if [[ ${#failed[@]} -gt 0 ]]; then
    echo "Converted $converted; failed: ${failed[*]}"
    exit 1
fi
exit 0
