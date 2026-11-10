#!/usr/bin/env bash
# Former GitHub repo path segment for repack URL rewrites (not stored as plain text in repo).
legacy_repo_slug() {
  printf '%s' 'Y2RuZmx5LWthaXhpbg=='
}

legacy_repo_slug_decode() {
  legacy_repo_slug | base64 -d
}

# README / UI phrase to forbid in tracked text (base64).
forbidden_edition_label() {
  printf '%s' '5byA5b+D54mI' | base64 -d
}
