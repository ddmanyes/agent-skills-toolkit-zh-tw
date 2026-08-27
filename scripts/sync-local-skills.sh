#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/sync-local-skills.sh [--claude] [--agents] [--antigravity] [--all]

Copies active skills from this repository into the selected local skill directories.
Existing unrelated skills are preserved. The deprecated writing-great-skills directory
is moved to a recoverable skills-archive directory after writing-for-agents succeeds.
Set SKILLS_SYNC_HOME to an isolated home root when testing the script.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/skills"
skills_sync_home="${SKILLS_SYNC_HOME:-$HOME}"

if [[ ! -d "$source_dir" ]]; then
  echo "Missing source directory: $source_dir" >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required but was not found." >&2
  exit 1
fi

declare -a targets=()

add_target() {
  local candidate="$1"
  local existing
  for existing in "${targets[@]:-}"; do
    [[ "$existing" == "$candidate" ]] && return
  done
  targets+=("$candidate")
}

if [[ $# -eq 0 ]]; then
  usage
  exit 2
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude)
      add_target "$skills_sync_home/.claude/skills"
      ;;
    --agents)
      add_target "$skills_sync_home/.agents/skills"
      ;;
    --antigravity)
      add_target "$skills_sync_home/.gemini/config/skills"
      ;;
    --all)
      add_target "$skills_sync_home/.claude/skills"
      add_target "$skills_sync_home/.agents/skills"
      add_target "$skills_sync_home/.gemini/config/skills"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

timestamp="$(date +%Y%m%d-%H%M%S)"

for target in "${targets[@]}"; do
  mkdir -p "$target"
  echo "Syncing active skills to $target"

  for skill_dir in "$source_dir"/*; do
    [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]] || continue
    skill_name="$(basename "$skill_dir")"
    destination="$target/$skill_name"

    if [[ -L "$destination" ]]; then
      echo "  kept symlink: $skill_name"
      continue
    fi

    mkdir -p "$destination"
    rsync -a --exclude '.DS_Store' --exclude '._*' "$skill_dir/" "$destination/"
    echo "  updated: $skill_name"
  done

  legacy="$target/writing-great-skills"
  replacement="$target/writing-for-agents/SKILL.md"
  if [[ -d "$legacy" && ! -L "$legacy" && -f "$replacement" ]]; then
    archive_root="$(dirname "$target")/skills-archive"
    archive_target="$archive_root/writing-great-skills-$timestamp"
    mkdir -p "$archive_root"
    mv "$legacy" "$archive_target"
    echo "  archived deprecated skill: $archive_target"
  fi

  legacy_review="$target/code-review"
  replacement_review="$target/sp-code-review/SKILL.md"
  if [[ -d "$legacy_review" && ! -L "$legacy_review" && -f "$replacement_review" ]]; then
    archive_root="$(dirname "$target")/skills-archive"
    archive_target="$archive_root/code-review-$timestamp"
    mkdir -p "$archive_root"
    mv "$legacy_review" "$archive_target"
    echo "  archived renamed skill: $archive_target"
  fi
done

echo "Skill sync complete. Restart or open a new agent session to refresh discovery."
