#!/bin/bash
# Pixi wrapper script for Doculyze

set -e

# Check if pixi is installed
if ! command -v pixi &> /dev/null; then
    echo "Pixi is not installed. Installing..."
    curl -fsSL https://pixi.sh/install.sh | bash
    export PATH="$HOME/.pixi/bin:$PATH"
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [command] [args...]"
    echo ""
    echo "Commands:"
    echo "  install              Install dependencies"
    echo "  shell               Activate pixi shell"
    echo "  cli [args]          Run CLI with arguments" 
    echo "  analyze [args]      Run document analysis"
    echo "  preprocess [args]   Run document preprocessing"
    echo "  test                Run tests"
    echo "  clean               Clean environment"
    echo ""
    echo "Examples:"
    echo "  $0 install"
    echo "  $0 cli --help"
    echo "  $0 analyze documents/ --config configs/legal.yaml"
    echo "  $0 preprocess files/ --operation extract"
}

# Main command handling
case "${1:-}" in
    "install")
        echo "Installing dependencies with pixi..."
        pixi install
        ;;
    "shell")
        echo "Activating pixi shell..."
        pixi shell
        ;;
    "cli")
        shift
        pixi run cli "$@"
        ;;
    "analyze")
        shift
        pixi run analyze "$@"
        ;;
    "preprocess") 
        shift
        pixi run preprocess "$@"
        ;;
    "test")
        echo "Running tests..."
        pixi run cli test-extract sample_docs/sample_contract.txt
        pixi run cli list-configs
        ;;
    "clean")
        echo "Cleaning pixi environment..."
        rm -rf .pixi
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac