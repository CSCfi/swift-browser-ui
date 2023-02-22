#!/usr/bin/env bash
# eslint for pre-commit. Skips run if `pnpm` or eslint are not installed

if ! command -v pnpm > /dev/null 2>&1; then
  echo "pnpm not installed, not running eslint as pre-commit hook"
  exit 0
fi

if ! test -f swift_browser_ui_frontend/node_modules/.bin/eslint; then
  echo "eslint is not installed, not running eslint as pre-commit hook"
  exit 0
fi

pnpm --prefix swift_browser_ui_frontend run lint
