function Convert-SubmoduleToSubtree {
    param (
        [Parameter(Mandatory=$true)]
        [string]$RepoPath,    # The local folder name (e.g., "NeuroPy")
        [Parameter(Mandatory=$true)]
        [string]$RemoteUrl,   # The git URL (e.g., "https://github.com/phohale/NeuroPy.git")
        [Parameter(Mandatory=$false)]
        [string]$Branch = ''  # Default branch (e.g. main); if empty, detected from remote HEAD
    )

    Process {
        Write-Host "--- Converting $RepoPath to Subtree ---" -ForegroundColor Cyan

        # 1. Remove Submodule from Git index
        git rm --cached $RepoPath
        if ($LASTEXITCODE -ne 0) { throw "git rm --cached failed for $RepoPath" }

        # Remove submodule entry from .gitmodules if present
        $gitmodulesPath = ".gitmodules"
        if (Test-Path $gitmodulesPath) {
            $lines = Get-Content $gitmodulesPath
            $newLines = @()
            $skip = $false
            foreach ($line in $lines) {
                if ($line -match '^\[submodule ') {
                    if ($line -eq "[submodule `"$RepoPath`"]") { $skip = $true; continue }
                    $skip = $false
                }
                if (-not $skip) { $newLines += $line }
            }
            $newContent = ($newLines | ForEach-Object { $_.TrimEnd() }) -join "`n"
            if ([string]::IsNullOrWhiteSpace($newContent)) {
                Remove-Item $gitmodulesPath -Force
            } else {
                Set-Content -Path $gitmodulesPath -Value $newContent.TrimEnd() -NoNewline
            }
        }

        # 2. Clean up .git/config and .git/modules
        git config -f .git/config --remove-section "submodule.$RepoPath" 2>$null
        $submoduleGitDir = ".git/modules/$RepoPath"
        if (Test-Path $submoduleGitDir) {
            Remove-Item -Recurse -Force $submoduleGitDir
        }

        # 3. Physically remove the folder to prepare for subtree injection
        if (Test-Path $RepoPath) {
            Remove-Item -Recurse -Force $RepoPath
        }

        # 4. Commit the removal of the submodule
        git add .
        if ($LASTEXITCODE -ne 0) { throw "git add failed for $RepoPath" }
        git commit -m "Remove submodule: $RepoPath to prepare for subtree conversion"
        if ($LASTEXITCODE -ne 0) { throw "git commit failed for $RepoPath" }

        # 5. Add the Remote and Fetch
        $remoteName = "remote-$RepoPath"
        git remote add $remoteName $RemoteUrl
        if ($LASTEXITCODE -ne 0) { throw "git remote add failed for $RepoPath" }
        git fetch $remoteName
        if ($LASTEXITCODE -ne 0) { throw "git fetch failed for $RepoPath" }

        # 6. Add as Subtree (using --squash to keep history clean)
        $branchToUse = $Branch
        if ([string]::IsNullOrWhiteSpace($branchToUse)) {
            $symref = git ls-remote --symref $RemoteUrl HEAD 2>$null
            if ($symref -match 'ref:\s+refs/heads/([^\s\t]+)') { $branchToUse = $Matches[1] }
            if ([string]::IsNullOrWhiteSpace($branchToUse)) { $branchToUse = 'main' }
        }
        git subtree add --prefix=$RepoPath $remoteName $branchToUse --squash
        if ($LASTEXITCODE -ne 0) { throw "git subtree add failed for $RepoPath" }

        Write-Host "Successfully converted $RepoPath!" -ForegroundColor Green
    }
}

# Execution List
# Replace the URLs below with your actual repository URLs
# Optional: set $defaultBranch (e.g. 'main' or 'master') to force branch; otherwise detected per remote
$defaultBranch = ''
$submodules = @{
    "NeuroPy"                = "https://github.com/CommanderPho/NeuroPy.git"
    "pyPhoCoreHelpers"       = "https://github.com/CommanderPho/pyPhoCoreHelpers.git"
    "pyPhoPlaceCellAnalysis" = "https://github.com/CommanderPho/pyPhoPlaceCellAnalysis.git"
    "Spike3D"                = "https://github.com/CommanderPho/Spike3D.git"
}

$failed = @()
foreach ($name in $submodules.Keys) {
    try {
        Convert-SubmoduleToSubtree -RepoPath $name -RemoteUrl $submodules[$name] -Branch $defaultBranch
    } catch {
        Write-Error "Convert-SubmoduleToSubtree failed for $name : $_"
        $failed += $name
    }
}
$converted = ($submodules.Keys.Count) - $failed.Count
if ($failed.Count -gt 0) {
    Write-Host "Converted $converted; failed: $($failed -join ', ')" -ForegroundColor Red
    exit 1
}
exit 0