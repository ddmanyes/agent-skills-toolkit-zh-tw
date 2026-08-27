[CmdletBinding()]
param(
    [switch]$Claude,
    [switch]$Agents,
    [switch]$Antigravity,
    [switch]$All,
    [string]$SkillsHome = $HOME
)

$ErrorActionPreference = "Stop"

if (-not ($Claude -or $Agents -or $Antigravity -or $All)) {
    Write-Host "Usage: .\scripts\sync-local-skills.ps1 [-Claude] [-Agents] [-Antigravity] [-All] [-SkillsHome <path>]"
    exit 2
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SourceDir = Join-Path $RepoRoot "skills"
if (-not (Test-Path -LiteralPath $SourceDir -PathType Container)) {
    throw "Missing source directory: $SourceDir"
}

$Targets = [System.Collections.Generic.List[string]]::new()
function Add-Target([string]$Path) {
    if (-not $Targets.Contains($Path)) {
        $Targets.Add($Path)
    }
}

if ($Claude -or $All) { Add-Target (Join-Path $SkillsHome ".claude\skills") }
if ($Agents -or $All) { Add-Target (Join-Path $SkillsHome ".agents\skills") }
if ($Antigravity -or $All) { Add-Target (Join-Path $SkillsHome ".gemini\config\skills") }

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

foreach ($Target in $Targets) {
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    Write-Host "Syncing active skills to $Target"

    foreach ($SkillDir in Get-ChildItem -LiteralPath $SourceDir -Directory) {
        if (-not (Test-Path -LiteralPath (Join-Path $SkillDir.FullName "SKILL.md") -PathType Leaf)) {
            continue
        }

        $Destination = Join-Path $Target $SkillDir.Name
        if (Test-Path -LiteralPath $Destination) {
            $Item = Get-Item -LiteralPath $Destination -Force
            if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                Write-Host "  kept link: $($SkillDir.Name)"
                continue
            }
        }

        New-Item -ItemType Directory -Force -Path $Destination | Out-Null
        Copy-Item -Path (Join-Path $SkillDir.FullName "*") -Destination $Destination -Recurse -Force
        Write-Host "  updated: $($SkillDir.Name)"
    }

    $Legacy = Join-Path $Target "writing-great-skills"
    $Replacement = Join-Path $Target "writing-for-agents\SKILL.md"
    if ((Test-Path -LiteralPath $Legacy -PathType Container) -and
        (Test-Path -LiteralPath $Replacement -PathType Leaf)) {
        $LegacyItem = Get-Item -LiteralPath $Legacy -Force
        if (-not ($LegacyItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            $ArchiveRoot = Join-Path (Split-Path -Parent $Target) "skills-archive"
            $ArchiveTarget = Join-Path $ArchiveRoot "writing-great-skills-$Timestamp"
            New-Item -ItemType Directory -Force -Path $ArchiveRoot | Out-Null
            Move-Item -LiteralPath $Legacy -Destination $ArchiveTarget
            Write-Host "  archived deprecated skill: $ArchiveTarget"
        }
    }

    $LegacyReview = Join-Path $Target "code-review"
    $ReplacementReview = Join-Path $Target "sp-code-review\SKILL.md"
    if ((Test-Path -LiteralPath $LegacyReview -PathType Container) -and
        (Test-Path -LiteralPath $ReplacementReview -PathType Leaf)) {
        $LegacyReviewItem = Get-Item -LiteralPath $LegacyReview -Force
        if (-not ($LegacyReviewItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            $ArchiveRoot = Join-Path (Split-Path -Parent $Target) "skills-archive"
            $ArchiveTarget = Join-Path $ArchiveRoot "code-review-$Timestamp"
            New-Item -ItemType Directory -Force -Path $ArchiveRoot | Out-Null
            Move-Item -LiteralPath $LegacyReview -Destination $ArchiveTarget
            Write-Host "  archived renamed skill: $ArchiveTarget"
        }
    }
}

Write-Host "Skill sync complete. Restart or open a new agent session to refresh discovery."
