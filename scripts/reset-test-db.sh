#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

#
# Reset Test Database Script
#
# This script provides a one-command database reset for the Pasture Management System.
# It replaces the manual 5-step process with a single command.
#
# Usage:
#   ./scripts/reset-test-db.sh [admin_password] [--no-server]
#
# Arguments:
#   admin_password  Optional. Admin password for database initialization (default: "admin")
#   --no-server     Optional. Skip server restart (useful for BDD test setup)
#
# Examples:
#   ./scripts/reset-test-db.sh                 # Use default password, restart server
#   ./scripts/reset-test-db.sh mysecret        # Use custom password, restart server
#   ./scripts/reset-test-db.sh admin --no-server  # Skip server restart
#

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Configuration
TRACKER_DIR="${TRACKER_DIR:-tracker}"
DB_DIR="${TRACKER_DIR}/db"
ADMIN_PASSWORD="${1:-admin}"
SKIP_SERVER=false
SERVER_PORT="${ROUNDUP_PORT:-9080}"
TRACKER_NAME="${TRACKER_NAME:-pms}"
BASE_URL="http://localhost:${SERVER_PORT}/${TRACKER_NAME}/"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
for arg in "$@"; do
    if [ "$arg" = "--no-server" ]; then
        SKIP_SERVER=true
    fi
done

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v uv &> /dev/null; then
        log_error "uv is not installed. Please install uv first."
        exit 1
    fi

    if [ ! -d "$TRACKER_DIR" ]; then
        log_error "Tracker directory '$TRACKER_DIR' not found."
        log_info "Are you running this script from the project root?"
        exit 1
    fi

    log_success "Dependencies OK"
}

stop_roundup_servers() {
    log_info "Stopping any running Roundup servers..."

    # Find all roundup-server processes
    PIDS=$(pgrep -f "roundup-server" || true)

    if [ -z "$PIDS" ]; then
        log_info "No Roundup servers running"
        return 0
    fi

    # Kill processes
    echo "$PIDS" | xargs kill 2>/dev/null || true

    # Wait for processes to terminate
    sleep 2

    # Verify they're gone
    REMAINING=$(pgrep -f "roundup-server" || true)
    if [ -n "$REMAINING" ]; then
        log_warning "Some servers still running, force killing..."
        echo "$REMAINING" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    log_success "Roundup servers stopped"
}

clean_database() {
    log_info "Cleaning database directory..."

    if [ -d "$DB_DIR" ]; then
        rm -rf "$DB_DIR"
        log_success "Database directory cleaned"
    else
        log_info "Database directory doesn't exist (already clean)"
    fi
}

initialize_database() {
    log_info "Initializing fresh database..."
    log_info "  Tracker: $TRACKER_DIR"
    log_info "  Admin password: $(echo "$ADMIN_PASSWORD" | sed 's/./*/g')"

    # Run roundup-admin initialise with password piped in
    cd "$TRACKER_DIR"
    if echo -e "${ADMIN_PASSWORD}\n${ADMIN_PASSWORD}" | uv run roundup-admin -i . initialise > /dev/null 2>&1; then
        cd - > /dev/null
        log_success "Database initialized"
        return 0
    else
        cd - > /dev/null
        log_error "Database initialization failed"
        return 1
    fi
}

start_roundup_server() {
    if [ "$SKIP_SERVER" = true ]; then
        log_info "Skipping server start (--no-server flag)"
        return 0
    fi

    log_info "Starting Roundup server..."
    log_info "  Port: $SERVER_PORT"
    log_info "  Tracker name: $TRACKER_NAME"

    # Start server in background, redirect output to /dev/null
    uv run roundup-server -p "$SERVER_PORT" "${TRACKER_NAME}=${TRACKER_DIR}" > /dev/null 2>&1 &
    SERVER_PID=$!

    # Wait a moment for server to start
    sleep 2

    # Verify server is running
    if ! ps -p $SERVER_PID > /dev/null 2>&1; then
        log_error "Server failed to start"
        return 1
    fi

    log_success "Server started (PID: $SERVER_PID)"
}

verify_server() {
    if [ "$SKIP_SERVER" = true ]; then
        return 0
    fi

    log_info "Verifying server is responding..."

    # Try to fetch the homepage
    if curl -s -f "$BASE_URL" > /dev/null 2>&1; then
        log_success "Server is responding"
        return 0
    else
        log_warning "Server not responding yet (may need more time)"
        return 0  # Don't fail - server might just need more startup time
    fi
}

display_info() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✓ Database Reset Complete${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  📂 Database: $DB_DIR"
    echo "  👤 Admin user: admin"
    echo "  🔑 Password: $ADMIN_PASSWORD"

    if [ "$SKIP_SERVER" = false ]; then
        echo "  🌐 URL: $BASE_URL"
        echo ""
        echo "To stop the server:"
        echo "  pkill -f roundup-server"
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Roundup Test Database Reset"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_dependencies
    stop_roundup_servers
    clean_database
    initialize_database
    start_roundup_server
    verify_server
    display_info
}

# Run main function
main

exit 0
