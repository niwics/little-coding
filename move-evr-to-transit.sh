#!/usr/bin/env zsh

# Set the source and destination directories
src="/Users/miroslav.kvasnica/PhoneDocs/EVR"
dst="/Users/miroslav.kvasnica/Documents/EVR-transit"

# Calculate the timestamp for 30 days ago
timestamp=$(date -v-30d +%s)

# Loop through each file in the source directory
for file in $src/*; do
  # Check if the file is older than 30 days
  if [[ $(stat -f "%m" "$file") -lt $timestamp ]]; then
    # Move the file to the destination directory
    mv "$file" "$dst"
  fi
done