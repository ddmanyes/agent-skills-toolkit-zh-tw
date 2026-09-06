#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/sync-local-skills.sh [--claude] [--agents] [--antigravity] [--all]
       [--skill NAME ...] [--include-disabled] [--include-transitional] [--archive-legacy] [--skills-home PATH]

Copy active skills, or only the repeated --skill names, to selected local directories.
--include-disabled requires explicit names and only updates disabled skills already
installed at each target. Changed originals go to the sibling skills-backups directory.
Existing transitional skills are preserved; missing targets receive the public fallback.
--include-transitional requires explicit --skill names to replace existing copies.
Extra local files and legacy skill directories remain unless --archive-legacy is set.
Set SKILLS_SYNC_HOME or --skills-home to an isolated home root when testing.
On Windows, use the PowerShell script for junction/reparse-point protection.
EOF
}
die() { echo "$*" >&2; exit 1; }
assert_name() {
  [[ "$1" =~ ^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$ ]] || die "Invalid Skill name: $1"
}
assert_no_links() {
  local current="$1"
  [[ "$current" == /* ]] || die "Expected an absolute path: $current"
  case "$current/" in */../*|*/./*) die "Unresolved path component: $current" ;; esac
  while [[ "$current" != / && -n "$current" ]]; do
    [[ ! -L "$current" ]] || die "Refusing symbolic link: $current"
    current="$(dirname "$current")"
  done
}
assert_tree() {
  local root="$1" unsafe
  assert_no_links "$root"
  [[ ! -e "$root" || -d "$root" ]] || die "Expected directory: $root"
  [[ -d "$root" ]] || return 0
  unsafe="$(find "$root" ! -type d ! -type f -print -quit)"
  [[ -z "$unsafe" ]] || die "Refusing link or special file: $unsafe"
}
assert_within() {
  [[ "$1" == "$2/"* ]] || die "Path escapes intended directory: $1 (root: $2)"
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
source_dir="$repo_root/skills"
disabled_dir="$repo_root/disabled_skills"
skills_sync_home="${SKILLS_SYNC_HOME:-$HOME}"
include_disabled=false
include_transitional=false
explicit_selection=false
archive_legacy=false
declare -a selections=() target_suffixes=() targets=() sources=() source_disabled=()

add_target() {
  local candidate="$1" existing
  for existing in "${target_suffixes[@]:-}"; do
    [[ "$existing" == "$candidate" ]] && return 0
  done
  target_suffixes+=("$candidate")
}
if [[ $# -eq 0 ]]; then usage; exit 2; fi
while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) add_target '.claude/skills' ;;
    --agents) add_target '.agents/skills' ;;
    --antigravity) add_target '.gemini/config/skills' ;;
    --all) add_target '.claude/skills'; add_target '.agents/skills'; add_target '.gemini/config/skills' ;;
    --skill)
      explicit_selection=true
      [[ $# -ge 2 && -n "$2" ]] || die '--skill requires a name'
      assert_name "$2"
      duplicate=false
      for existing in "${selections[@]:-}"; do [[ "$existing" != "$2" ]] || duplicate=true; done
      if ! $duplicate; then selections+=("$2"); fi
      shift ;;
    --include-disabled) include_disabled=true ;;
    --include-transitional) include_transitional=true ;;
    --archive-legacy) archive_legacy=true ;;
    --skills-home)
      [[ $# -ge 2 && -n "$2" ]] || die '--skills-home requires a path'
      skills_sync_home="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; die "Unknown option: $1" ;;
  esac
  shift
done
[[ ${#target_suffixes[@]} -gt 0 ]] || die 'Select at least one target'
if $include_disabled && [[ ${#selections[@]} -eq 0 ]]; then
  die '--include-disabled requires explicit --skill names'
fi
if $include_transitional && [[ ${#selections[@]} -eq 0 ]]; then
  die '--include-transitional requires explicit --skill names'
fi
[[ "$skills_sync_home" == /* ]] || skills_sync_home="$PWD/$skills_sync_home"
skills_sync_home="${skills_sync_home%/}"
assert_no_links "$skills_sync_home"
assert_no_links "$source_dir"
[[ -d "$source_dir" ]] || die "Missing source directory: $source_dir"
case "${OSTYPE:-}" in msys*|cygwin*) die 'Use sync-local-skills.ps1 on Windows so reparse points are checked.' ;; esac
command -v rsync >/dev/null 2>&1 || die 'rsync is required but was not found.'

transitional_list="$repo_root/scripts/transitional-skills.txt"
assert_no_links "$transitional_list"
[[ -f "$transitional_list" ]] || die 'Missing transitional Skill list'
declare -a transitional_names=()
while IFS= read -r name || [[ -n "$name" ]]; do
  name="${name%$'\r'}"
  [[ -n "$name" ]] || continue
  assert_name "$name"
  for existing in "${transitional_names[@]:-}"; do [[ "$existing" != "$name" ]] || die "Duplicate transitional Skill: $name"; done
  transitional_names+=("$name")
done < "$transitional_list"
[[ ${#transitional_names[@]} -gt 0 ]] || die 'Empty transitional Skill list'
is_transitional() {
  local candidate="$1" existing
  for existing in "${transitional_names[@]}"; do
    [[ "$existing" != "$candidate" ]] || return 0
  done
  return 1
}

if [[ ${#selections[@]} -eq 0 ]]; then
  for skill_dir in "$source_dir"/*; do
    [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]] || continue
    selections+=("$(basename "$skill_dir")")
  done
fi
for name in "${selections[@]}"; do
  assert_name "$name"
  active="$source_dir/$name"
  disabled="$disabled_dir/$name"
  if $include_disabled && [[ -f "$active/SKILL.md" && -f "$disabled/SKILL.md" ]]; then
    die "Ambiguous active/disabled Skill name: $name"
  fi
  if [[ -f "$active/SKILL.md" ]]; then
    sources+=("$active"); source_disabled+=(false)
  elif $include_disabled && [[ -f "$disabled/SKILL.md" ]]; then
    sources+=("$disabled"); source_disabled+=(true)
  else
    die "Skill not found in selected source scope: $name"
  fi
  assert_tree "${sources[${#sources[@]}-1]}"
done

# Check every selected destination before rsync can mutate any target.
for suffix in "${target_suffixes[@]}"; do
  target="$skills_sync_home/$suffix"
  assert_no_links "$target"
  targets+=("$target")
  for index in "${!selections[@]}"; do
    name="${selections[$index]}"
    destination="$target/$name"
    assert_within "$destination" "$target"
    assert_tree "$destination"
    if ${source_disabled[$index]} && [[ ! -f "$destination/SKILL.md" ]]; then
      die "Disabled Skill is not already installed at this target: $destination"
    fi
    if is_transitional "$name" && [[ -e "$destination" ]] && ! $include_transitional; then
      if $explicit_selection; then
        die "Installed transitional Skill is protected: $name. Add --include-transitional with explicit --skill names to restore the public fallback."
      fi
      continue
    fi
    while IFS= read -r -d '' entry; do
      relative="${entry#"${sources[$index]}/"}"
      file_target="$destination/$relative"
      assert_within "$file_target" "$destination"
      assert_no_links "$file_target"
      if [[ -e "$file_target" ]]; then
        if [[ -d "$entry" ]]; then [[ -d "$file_target" ]] || die "Expected directory: $file_target"
        else [[ -f "$file_target" ]] || die "Cannot replace directory with file: $file_target"; fi
      fi
    done < <(find "${sources[$index]}" -mindepth 1 -print0)
  done
done

run_id="$(date +%Y%m%d-%H%M%S)-$$-$RANDOM"
current_backup='(no backup path selected)'
trap 'echo "Sync stopped. Completed writes remain; recover changed originals from $current_backup or earlier reported backup paths. No rollback was attempted." >&2' ERR
for target in "${targets[@]}"; do
  backup_base="$(dirname "$target")/skills-backups"
  current_backup="$backup_base/$run_id"
  assert_within "$current_backup" "$backup_base"
  assert_no_links "$current_backup"
  assert_no_links "$target"
  mkdir -p "$target"
  echo "Syncing selected skills to $target; changed originals: $current_backup"
  for index in "${!selections[@]}"; do
    name="${selections[$index]}"
    skill_dir="${sources[$index]}"
    destination="$target/$name"
    assert_tree "$skill_dir"
    assert_tree "$destination"
    if is_transitional "$name" && [[ -e "$destination" ]] && ! $include_transitional; then
      if $explicit_selection; then die "Installed transitional Skill appeared after preflight: $name"; fi
      echo "SKIP transitional/external: $destination (existing content preserved)"
      continue
    fi
    assert_no_links "$current_backup"
    mkdir -p "$destination"
    rsync -a --checksum --backup --backup-dir="$current_backup/$name" \
      --itemize-changes \
      --exclude '.DS_Store' --exclude '._*' --exclude '.Rhistory' \
      --exclude '__pycache__' --exclude '*.py[cod]' \
      "$skill_dir/" "$destination/"
  done
  if $archive_legacy; then
    for pair in 'writing-great-skills:writing-for-agents' 'code-review:sp-code-review'; do
      legacy_name="${pair%%:*}"; replacement_name="${pair#*:}"
      selected=false
      for name in "${selections[@]}"; do [[ "$name" != "$replacement_name" ]] || selected=true; done
      $selected || continue
      legacy="$target/$legacy_name"
      replacement="$target/$replacement_name/SKILL.md"
      if [[ -d "$legacy" && -f "$replacement" ]]; then
        archive_root="$(dirname "$target")/skills-archive"
        archive_target="$archive_root/$legacy_name-$run_id"
        assert_within "$legacy" "$target"
        assert_within "$archive_target" "$archive_root"
        assert_tree "$legacy"
        assert_no_links "$archive_target"
        [[ ! -e "$archive_target" ]] || die "Archive already exists: $archive_target"
        mkdir -p "$archive_root"
        mv "$legacy" "$archive_target"
        echo "  archived: $archive_target"
      fi
    done
  fi
done

echo 'Skill sync complete. Extra local files and legacy directories were preserved unless --archive-legacy was specified.'
echo 'Backup files mirror target-relative Skill paths; copy an original back to the same path to restore it. Open a new agent session to refresh discovery.'
