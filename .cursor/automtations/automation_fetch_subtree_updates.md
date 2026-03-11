<!-- Cursor Cloud Automation: Fetch subtree updates.
  Purpose: When any of the four upstream repos (pyPhoPlaceCellAnalysis, NeuroPy, pyPhoCoreHelpers, Spike3D) receives a push, run the subtree update script so Spike3DWorkEnv stays in sync.
  Script: SCRIPTS/pull_all_subworkspaces.sh (ensures remotes, fetches, then git subtree pull --squash for each).
  gitConfig.branch: Update when your codespace or target branch changes (e.g. to main or a dedicated automation branch).
-->
{
  "name": "Spike3DWorkspaceEnv Update Workspaces",
  "triggers": [
    {
      "git": {
        "push": {
          "repo": "CommanderPho/pyPhoPlaceCellAnalysis",
          "branch": "develop"
        },
        "userAllowlist": [
          "CommanderPho"
        ]
      }
    },
    {
      "git": {
        "push": {
          "repo": "CommanderPho/NeuroPy",
          "branch": "feature/safe-advance"
        },
        "userAllowlist": [
          "CommanderPho"
        ]
      }
    },
    {
      "git": {
        "push": {
          "repo": "CommanderPho/pyPhoCoreHelpers",
          "branch": "release/pho-diba-2025-paper"
        },
        "userAllowlist": [
          "CommanderPho"
        ]
      }
    },
    {
      "git": {
        "push": {
          "repo": "CommanderPho/Spike3D",
          "branch": "master"
        },
        "userAllowlist": [
          "CommanderPho"
        ]
      }
    }
  ],
  "actions": [],
  "prompts": [
    {
      "prompt": "From the repository root, run: bash SCRIPTS/pull_all_subworkspaces.sh\nThis fetches and merges the four subtree repos (NeuroPy, pyPhoCoreHelpers, pyPhoPlaceCellAnalysis, Spike3D) into this repo. Do not push. Report whether all pulls completed or list any failed subtrees."
    }
  ],
  "model": "claude-4.6-sonnet-high-thinking",
  "memoryEnabled": false,
  "scope": "private",
  "gitConfig": {
    "repo": "CommanderPho/Spike3DWorkEnv",
    "branch": "codespace-commanderpho-redesigned-capybara-q7vpp6gjgj39vp7"
  }
}
