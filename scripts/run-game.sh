#!/usr/bin/env bash
set -euo pipefail

# Run Game Script
# Launches the Snatchernauts framework game using the RENPY_SDK environment variable
#
# Usage:
#   scripts/run-game.sh              # run the game normally
#   scripts/run-game.sh --debug      # run with debug output
#   scripts/run-game.sh --lint       # run lint only (no game launch)
#   scripts/run-game.sh --compile    # compile and run the game
#   scripts/run-game.sh --help       # show this help

# Default RENPY_SDK if not provided
RENPY_SDK="${RENPY_SDK:-$HOME/renpy-8.4.1-sdk}"

# Function to display help
show_help() {
    echo "Run Game Script - Snatchernauts Framework"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --debug      Enable debug output and keep console open"
    echo "  --lint       Run lint check only (does not start game)"
    echo "  --compile    Force recompilation and run the game"
    echo "  --help       Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  RENPY_SDK    Path to Ren'Py SDK (default: ~/renpy-8.4.1-sdk)"
    echo "               Current: $RENPY_SDK"
    echo ""
    echo "Examples:"
    echo "  $0                    # Normal game launch"
    echo "  $0 --debug           # Debug mode"
    echo "  $0 --lint            # Lint only"
    echo "  $0 --compile         # Compile and run"
    echo "  RENPY_SDK=/path/to/sdk $0  # Custom SDK path"
}

# Validate RENPY_SDK
validate_sdk() {
    if [[ ! -d "$RENPY_SDK" ]]; then
        echo "ERROR: RENPY_SDK directory not found: $RENPY_SDK" >&2
        echo "Set RENPY_SDK to your Ren'Py 8.4.x SDK directory or install at ~/renpy-8.4.1-sdk" >&2
        exit 1
    fi

    if [[ ! -x "$RENPY_SDK/renpy.sh" ]]; then
        echo "ERROR: renpy.sh not found or not executable in: $RENPY_SDK" >&2
        echo "Make sure RENPY_SDK points to a valid Ren'Py SDK installation" >&2
        exit 1
    fi
}

# Run lint check
run_lint() {
    echo "Running lint check..."
    if [[ -x "scripts/lint.sh" ]]; then
        ./scripts/lint.sh
    else
        "$RENPY_SDK/renpy.sh" . --lint
    fi
    echo "Lint check completed."
}

# Main function
main() {
    local debug=false
    local run_lint_first=false
    local compile_first=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug)
                debug=true
                shift
                ;;
            --lint)
                run_lint_first=true
                shift
                ;;
            --compile)
                compile_first=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                echo "Use --help for usage information" >&2
                exit 1
                ;;
        esac
    done
    
    # Validate SDK
    validate_sdk
    
    echo "Starting Snatchernauts Framework..."
    echo "Using Ren'Py SDK: $RENPY_SDK"
    echo "Project directory: $(pwd)"
    
    # Run lint if requested
    if [[ "$run_lint_first" == true ]]; then
        run_lint
        echo ""
        # Exit after linting - don't start the game
        exit 0
    fi
    
    # Compile if requested
    if [[ "$compile_first" == true ]]; then
        echo "Compiling game..."
        "$RENPY_SDK/renpy.sh" . --compile
        echo "Compilation completed."
        echo ""
    fi
    
    # Show debug info if requested
    if [[ "$debug" == true ]]; then
        echo "Debug mode enabled"
        echo "Game will launch with console output visible"
        echo ""
    fi
    
    # Launch the game
    echo "Launching game..."
    if [[ "$debug" == true ]]; then
        # Debug mode - keep output visible
        "$RENPY_SDK/renpy.sh" . --debug
    else
        # Normal mode
        "$RENPY_SDK/renpy.sh" .
    fi
    
    echo "Game session ended."
}

main "$@"
