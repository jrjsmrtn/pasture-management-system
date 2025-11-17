#!/bin/bash
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

# Validate all Roundup templates by requesting them and checking for errors

set -e

TRACKER_URL="${TRACKER_URL:-http://localhost:9080/pms}"
FAILED=0

echo "Validating Roundup templates..."

# List of pages to check
PAGES=(
    "issue"
    "issue?@template=item"
    "change"
    "change?@template=item"
    "ci"
    "ci?@template=item"
)

for page in "${PAGES[@]}"; do
    echo -n "Checking $page... "
    response=$(curl -s "${TRACKER_URL}/${page}")

    if echo "$response" | grep -q "Templating Error"; then
        echo "❌ FAILED"
        echo "$response" | grep -A 3 "Templating Error"
        FAILED=$((FAILED + 1))
    else
        echo "✓"
    fi
done

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "❌ $FAILED template(s) have errors"
    exit 1
else
    echo ""
    echo "✅ All templates valid"
    exit 0
fi
