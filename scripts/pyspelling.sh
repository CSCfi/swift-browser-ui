#!/usr/bin/env bash

if ! command -v pyspelling > /dev/null 2>&1; then
    echo "pyspelling not installed, not running as pre-commit hook"
    exit 0
elif ! aspell -v > /dev/null 2>&1; then
    echo "aspell is not installed, not running as pre-commit hook"
    exit 0
fi

check_files=""
for arg in "${@:2:$#}"
do
    check_files+="--source $arg "
done

pyspelling -v --name $1 ${check_files}
