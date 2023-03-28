#!/usr/bin/env bash
# Sorts dictionary, converts to lower case, and remove duplicates

# Makes sorting consistent across machines
export LC_ALL=C

for file in ".github/config/.wordlist.txt" ".github/config/.finnishwords.txt"; do
  sort "${file}" | tr "[:upper:]" "[:lower:]" | sort -u -o "${file}"
done
