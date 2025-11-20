#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

#
# Parallel BDD Test Execution Script
#
# This script runs Behave BDD tests in parallel by distributing feature files
# across multiple workers. Each worker gets its own database and server port.
#
# Usage: ./scripts/run-tests-parallel.sh [workers] [feature_dir]
#
# Examples:
#   ./scripts/run-tests-parallel.sh 4                    # 4 workers, all features
#   ./scripts/run-tests-parallel.sh 2 features/cmdb      # 2 workers, cmdb only
#

set -e

# Configuration
WORKERS=${1:-4}
FEATURE_DIR=${2:-features}
BASE_PORT=9080
TRACKER_TEMPLATE="tracker"

echo "================================================"
echo "Parallel BDD Test Execution"
echo "================================================"
echo "Workers: $WORKERS"
echo "Feature directory: $FEATURE_DIR"
echo "Base port: $BASE_PORT"
echo ""

# Export environment for all workers
export CLEANUP_TEST_DATA="false"  # Share database within each worker
export HEADLESS="true"

# Find all feature files
echo "Finding feature files..."
FEATURE_FILES=$(find "$FEATURE_DIR" -name "*.feature" -type f | sort)
FEATURE_COUNT=$(echo "$FEATURE_FILES" | wc -l | tr -d ' ')

if [ "$FEATURE_COUNT" -eq 0 ]; then
    echo "Error: No feature files found in $FEATURE_DIR"
    exit 1
fi

echo "Found $FEATURE_COUNT feature files"
echo ""

# Function to run a single feature file in a worker
run_feature() {
    local feature_file=$1
    local worker_id=$2
    local port=$((BASE_PORT + worker_id))
    local tracker_dir="tracker-worker-$worker_id"
    local log_file="reports/worker-$worker_id.log"

    # Create worker-specific tracker if it doesn't exist
    if [ ! -d "$tracker_dir/db" ]; then
        mkdir -p "$tracker_dir"
        cp -r "$TRACKER_TEMPLATE"/* "$tracker_dir/" 2>/dev/null || true
        printf "admin\nadmin\n" | uv run roundup-admin -i "$tracker_dir" initialise > /dev/null 2>&1
    fi

    # Start worker-specific server if not running
    if ! curl -s -f "http://localhost:$port/pms/" > /dev/null 2>&1; then
        uv run roundup-server -p "$port" "pms=$tracker_dir" > "/tmp/roundup-worker-$worker_id.log" 2>&1 &
        sleep 2
    fi

    # Run the feature file
    TRACKER_URL="http://localhost:$port/pms/" \
        uv run behave "$feature_file" \
        --no-capture \
        --format=progress \
        >> "$log_file" 2>&1

    local status=$?

    # Report result
    if [ $status -eq 0 ]; then
        echo "[Worker $worker_id] ✓ $(basename "$feature_file")"
    else
        echo "[Worker $worker_id] ✗ $(basename "$feature_file")"
    fi

    return $status
}

export -f run_feature
export BASE_PORT TRACKER_TEMPLATE

# Create reports directory
mkdir -p reports

# Clean up old worker files
rm -f reports/worker-*.log
rm -rf tracker-worker-*

# Run features in parallel using GNU parallel
echo "Running tests in parallel..."
echo ""
START_TIME=$(date +%s)

# Use GNU parallel to distribute features across workers
echo "$FEATURE_FILES" | parallel --will-cite -j "$WORKERS" --line-buffer --tagstring '{#}' \
    run_feature {} {#} || true

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "================================================"
echo "Parallel execution completed in $DURATION seconds"
echo "================================================"

# Cleanup worker servers
echo "Stopping worker servers..."
for ((i=1; i<=WORKERS; i++)); do
    port=$((BASE_PORT + i))
    lsof -ti tcp:$port | xargs kill 2>/dev/null || true
done

# Clean up worker trackers
rm -rf tracker-worker-*

echo "Done!"
