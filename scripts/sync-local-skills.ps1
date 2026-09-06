[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$Claude,
    [switch]$Agents,
    [switch]$Antigravity,
    [switch]$All,
    [string]$SkillsHome = $HOME,
    [string[]]$SkillNames = @(),
    [switch]$IncludeDisabled,
    [switch]$IncludeTransitional,
    [switch]$ArchiveLegacy
)

$ErrorActionPreference = 'Stop'

if (-not ($Claude -or $Agents -or $Antigravity -or $All)) {
    Write-Host 'Usage: sync-local-skills.ps1 [-Claude] [-Agents] [-Antigravity] [-All] [-SkillsHome <path>] [-SkillNames <name,...>] [-IncludeDisabled] [-IncludeTransitional] [-ArchiveLegacy] [-WhatIf]'
    exit 2
}
if ($IncludeDisabled -and $SkillNames.Count -eq 0) {
    throw '-IncludeDisabled requires an explicit -SkillNames list. Disabled skills must already be installed at each target.'
}

if ($IncludeTransitional -and $SkillNames.Count -eq 0) {
    throw '-IncludeTransitional requires an explicit -SkillNames list to replace installed transition copies.'
}

function Get-FullPath([string]$Path) {
    return [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
}
function Assert-Within([string]$Path, [string]$Root) {
    $Full = Get-FullPath $Path
    $Prefix = (Get-FullPath $Root) + [IO.Path]::DirectorySeparatorChar
    if (-not $Full.StartsWith($Prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes its intended directory: $Full (root: $Root)"
    }
}
function Assert-NoLinks([string]$Path) {
    $Current = [IO.Path]::GetFullPath($Path)
    while ($Current) {
        $Item = Get-Item -LiteralPath $Current -Force -ErrorAction SilentlyContinue
        if ($null -ne $Item -and ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing a symbolic link or reparse point: $Current"
        }
        $Parent = Split-Path -Parent $Current
        if ($Parent -eq $Current) { break }
        $Current = $Parent
    }
}
function Get-SafeFiles([string]$Directory, [string]$Relative = '') {
    Assert-NoLinks $Directory
    foreach ($Item in Get-ChildItem -LiteralPath $Directory -Force) {
        if ($Item.Name -in @('.DS_Store', '.Rhistory', '__pycache__') -or
            $Item.Name.StartsWith('._') -or $Item.Name -match '\.py[cod]$') { continue }
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Refusing a symbolic link or reparse point: $($Item.FullName)"
        }
        $ChildRelative = if ($Relative) { Join-Path $Relative $Item.Name } else { $Item.Name }
        if ($Item.PSIsContainer) {
            Get-SafeFiles $Item.FullName $ChildRelative
        } else {
            [PSCustomObject]@{ Source = $Item.FullName; Relative = $ChildRelative }
        }
    }
}
function Ensure-Directory([string]$Directory) {
    Assert-NoLinks $Directory
    if (Test-Path -LiteralPath $Directory) {
        if (-not (Test-Path -LiteralPath $Directory -PathType Container)) {
            throw "Expected a directory: $Directory"
        }
    } else {
        New-Item -ItemType Directory -Path $Directory -Force | Out-Null
    }
}

$RepoRoot = Get-FullPath (Split-Path -Parent $PSScriptRoot)
$SourceDir = Join-Path $RepoRoot 'skills'
$DisabledDir = Join-Path $RepoRoot 'disabled_skills'
Assert-NoLinks $SourceDir
if (-not (Test-Path -LiteralPath $SourceDir -PathType Container)) {
    throw "Missing source directory: $SourceDir"
}
$TransitionalList = Join-Path $PSScriptRoot 'transitional-skills.txt'
Assert-NoLinks $TransitionalList
$TransitionalNames = @(Get-Content -LiteralPath $TransitionalList -Encoding UTF8 | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if (-not $TransitionalNames.Count -or @($TransitionalNames | Select-Object -Unique).Count -ne $TransitionalNames.Count) {
    throw 'The transitional Skill list must be nonempty and contain unique names.'
}
foreach ($Name in $TransitionalNames) {
    if ($Name -notmatch '^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$') { throw "Invalid transitional Skill name: $Name" }
}
$Names = if ($SkillNames.Count) { @($SkillNames | Select-Object -Unique) } else {
    @(Get-ChildItem -LiteralPath $SourceDir -Directory | Where-Object {
        Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf
    } | Select-Object -ExpandProperty Name | Sort-Object)
}
$Selected = foreach ($Name in $Names) {
    if ($Name -notmatch '^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$') { throw "Invalid Skill name: $Name" }
    $ActivePath = Join-Path $SourceDir $Name
    $DisabledPath = Join-Path $DisabledDir $Name
    $Active = Test-Path -LiteralPath (Join-Path $ActivePath 'SKILL.md') -PathType Leaf
    $Disabled = Test-Path -LiteralPath (Join-Path $DisabledPath 'SKILL.md') -PathType Leaf
    if ($Active -and $Disabled -and $IncludeDisabled) { throw "Ambiguous active/disabled Skill name: $Name" }
    if ($Active) { $Path = $ActivePath; $IsDisabled = $false }
    elseif ($IncludeDisabled -and $Disabled) { $Path = $DisabledPath; $IsDisabled = $true }
    else { throw "Skill not found in the selected source scope: $Name" }
    Assert-Within $Path $RepoRoot
    Assert-NoLinks $Path
    [PSCustomObject]@{ Name = $Name; Disabled = $IsDisabled; Files = @(Get-SafeFiles $Path) }
}
$Selected = @($Selected)
$Targets = [System.Collections.Generic.List[string]]::new()
$HomeRoot = [IO.Path]::GetFullPath($SkillsHome)
function Add-Target([string]$Relative) {
    $Path = Get-FullPath (Join-Path $HomeRoot $Relative)
    Assert-Within $Path $HomeRoot
    Assert-NoLinks $Path
    if (-not $Targets.Contains($Path)) { $Targets.Add($Path) }
}
if ($Claude -or $All) { Add-Target '.claude/skills' }
if ($Agents -or $All) { Add-Target '.agents/skills' }
if ($Antigravity -or $All) { Add-Target '.gemini/config/skills' }

# Preflight every selected source and destination before any file is changed.
$Plan = [System.Collections.Generic.List[object]]::new()
foreach ($Target in $Targets) {
    foreach ($Skill in $Selected) {
        $Destination = Join-Path $Target $Skill.Name
        Assert-Within $Destination $Target
        Assert-NoLinks $Destination
        if ($Skill.Disabled -and -not (Test-Path -LiteralPath (Join-Path $Destination 'SKILL.md') -PathType Leaf)) {
            throw "Disabled Skill is not already installed at this target: $Destination"
        }
        if (Test-Path -LiteralPath $Destination) {
            if (-not (Test-Path -LiteralPath $Destination -PathType Container)) { throw "Expected a Skill directory: $Destination" }
            $null = @(Get-SafeFiles $Destination)
        }
        if ($Skill.Name -in $TransitionalNames -and (Test-Path -LiteralPath $Destination) -and -not $IncludeTransitional) {
            if ($SkillNames.Count) {
                throw "Installed transitional Skill is protected: $($Skill.Name). Add -IncludeTransitional with explicit -SkillNames to restore the public fallback."
            }
            Write-Host "SKIP transitional/external: $Destination (existing content preserved)"
            continue
        }
        foreach ($File in $Skill.Files) {
            $FileTarget = Join-Path $Destination $File.Relative
            Assert-Within $FileTarget $Destination
            Assert-NoLinks $FileTarget
            $Parent = Split-Path -Parent $FileTarget
            while ($Parent -and $Parent -ne $Target) {
                if ((Test-Path -LiteralPath $Parent) -and -not (Test-Path -LiteralPath $Parent -PathType Container)) {
                    throw "Expected a directory: $Parent"
                }
                $Parent = Split-Path -Parent $Parent
            }
            $Exists = Test-Path -LiteralPath $FileTarget
            if ($Exists -and -not (Test-Path -LiteralPath $FileTarget -PathType Leaf)) {
                throw "Cannot replace a directory with a file: $FileTarget"
            }
            $SourceHash = (Get-FileHash -LiteralPath $File.Source -Algorithm SHA256).Hash
            $OldHash = if ($Exists) { (Get-FileHash -LiteralPath $FileTarget -Algorithm SHA256).Hash } else { $null }
            if ($SourceHash -eq $OldHash) { continue }
            $Plan.Add([PSCustomObject]@{
                Target = $Target; Skill = $Skill.Name; Relative = $File.Relative
                Source = $File.Source; Destination = $FileTarget
                SourceHash = $SourceHash; OldHash = $OldHash
            })
        }
    }
}
$RunId = (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$BackupRoots = @{}
foreach ($Target in $Targets) {
    $BackupBase = Join-Path (Split-Path -Parent $Target) 'skills-backups'
    $BackupRoots[$Target] = Join-Path $BackupBase $RunId
    Assert-Within $BackupRoots[$Target] $BackupBase
    Assert-NoLinks $BackupRoots[$Target]
}
$Updated = 0
try {
    foreach ($Change in $Plan) {
        if (-not $PSCmdlet.ShouldProcess($Change.Destination, 'Back up changed content and sync Skill file')) { continue }
        Assert-NoLinks $Change.Source
        Assert-NoLinks $Change.Destination
        $CurrentHash = if (Test-Path -LiteralPath $Change.Destination -PathType Leaf) {
            (Get-FileHash -LiteralPath $Change.Destination -Algorithm SHA256).Hash
        } else { $null }
        if ($CurrentHash -ne $Change.OldHash) { throw "Destination changed since preflight: $($Change.Destination)" }
        if ((Get-FileHash -LiteralPath $Change.Source -Algorithm SHA256).Hash -ne $Change.SourceHash) {
            throw "Source changed since preflight: $($Change.Source)"
        }
        if ($null -ne $Change.OldHash) {
            $BackupRoot = $BackupRoots[$Change.Target]
            $Backup = Join-Path (Join-Path $BackupRoot $Change.Skill) $Change.Relative
            Assert-Within $Backup $BackupRoot
            Ensure-Directory (Split-Path -Parent $Backup)
            Copy-Item -LiteralPath $Change.Destination -Destination $Backup
            if ((Get-FileHash -LiteralPath $Backup -Algorithm SHA256).Hash -ne $Change.OldHash) {
                throw "Backup verification failed: $Backup"
            }
            Write-Host "  backup: $Backup"
        }
        Ensure-Directory (Split-Path -Parent $Change.Destination)
        Copy-Item -LiteralPath $Change.Source -Destination $Change.Destination -Force
        if ((Get-FileHash -LiteralPath $Change.Destination -Algorithm SHA256).Hash -ne $Change.SourceHash) {
            throw "Copy verification failed: $($Change.Destination)"
        }
        $Updated++
        Write-Host "  updated: $($Change.Destination)"
    }
    if ($ArchiveLegacy) {
        $Pairs = @(@('writing-great-skills', 'writing-for-agents'), @('code-review', 'sp-code-review'))
        foreach ($Target in $Targets) {
            foreach ($Pair in $Pairs) {
                if ($Pair[1] -notin $Names) { continue }
                $Legacy = Join-Path $Target $Pair[0]
                $Replacement = Join-Path (Join-Path $Target $Pair[1]) 'SKILL.md'
                if ((Test-Path -LiteralPath $Legacy -PathType Container) -and (Test-Path -LiteralPath $Replacement -PathType Leaf)) {
                    $ArchiveRoot = Join-Path (Split-Path -Parent $Target) 'skills-archive'
                    $ArchiveTarget = Join-Path $ArchiveRoot ($Pair[0] + '-' + $RunId)
                    Assert-Within $Legacy $Target
                    Assert-Within $ArchiveTarget $ArchiveRoot
                    Assert-NoLinks $Legacy
                    Assert-NoLinks $ArchiveTarget
                    $null = @(Get-SafeFiles $Legacy)
                    if ($PSCmdlet.ShouldProcess($Legacy, "Archive explicitly requested legacy Skill to $ArchiveTarget")) {
                        Ensure-Directory $ArchiveRoot
                        Move-Item -LiteralPath $Legacy -Destination $ArchiveTarget
                        Write-Host "  archived: $ArchiveTarget"
                    }
                }
            }
        }
    }
} catch {
    Write-Warning "Sync stopped after $Updated file(s). Completed writes remain; original overwritten files are recoverable under: $($BackupRoots.Values -join ', '). No rollback was attempted."
    throw
}
Write-Host "Skill sync complete: $Updated file(s) changed. Unrelated files and legacy directories were preserved unless -ArchiveLegacy was specified."
Write-Host 'Backup files mirror the target-relative Skill paths; copy an original back to that same path to restore it. Open a new agent session to refresh discovery.'
