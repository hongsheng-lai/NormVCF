#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 -r <reference_fasta> -i <input_vcf> [-d <decomposed_output>] [-f <filled_output>] [-n <normalized_output>]"
    echo "Options:"
    echo "  -r Reference FASTA file (required)"
    echo "  -i Input VCF file (required)"
    echo "  -d Output file for decomposed VCF (optional)"
    echo "  -f Output file for filled VCF (optional)"
    echo "  -n Output file for normalized VCF (optional)"
    exit 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Initialize variables
REFERENCE_FASTA=""
INPUT_VCF=""
DECOMPOSED_OUTPUT=""
FILLED_OUTPUT=""
NORMALIZED_OUTPUT=""
REHEADERED_VCF=""

# Parse command line options
while getopts "r:i:d:f:n:" opt; do
    case $opt in
        r) REFERENCE_FASTA="$OPTARG" ;;
        i) INPUT_VCF="$OPTARG" ;;
        d) DECOMPOSED_OUTPUT="$OPTARG" ;;
        f) FILLED_OUTPUT="$OPTARG" ;;
        n) NORMALIZED_OUTPUT="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if required arguments are provided
if [ -z "$REFERENCE_FASTA" ] || [ -z "$INPUT_VCF" ]; then
    echo "Error: Reference FASTA and Input VCF are required"
    usage
fi

# Check if required commands exist
for cmd in python3 bcftools; do
    if ! command_exists "$cmd"; then
        echo "Error: $cmd is not installed or not in PATH"
        exit 1
    fi
done

# Check if input files exist
if [ ! -f "$INPUT_VCF" ] || [ ! -f "$REFERENCE_FASTA" ]; then
    echo "Error: Input VCF or reference FASTA file not found"
    usage
fi

# Perform reheadering
REHEADERED_VCF="${INPUT_VCF%.vcf}.reheader.vcf"
echo "Running bcftools reheader..."
if ! bcftools reheader -f "${REFERENCE_FASTA}.fai" -o "$REHEADERED_VCF" "$INPUT_VCF"; then
    echo "Error: bcftools reheader failed"
    exit 1
fi
echo "Reheadered VCF: $REHEADERED_VCF"
CURRENT_INPUT="$REHEADERED_VCF"

# Run decompose.py if output is specified
if [ -n "$DECOMPOSED_OUTPUT" ]; then
    echo "Running decompose.py..."
    if ! python3 "$SCRIPT_DIR/scripts/decompose.py" -i "$CURRENT_INPUT" -o "$DECOMPOSED_OUTPUT"; then
        echo "Error: decompose.py failed"
        exit 1
    fi
    echo "Decomposed VCF: $DECOMPOSED_OUTPUT"
    CURRENT_INPUT="$DECOMPOSED_OUTPUT"
fi

# Run fill_indels.py if output is specified
if [ -n "$FILLED_OUTPUT" ]; then
    echo "Running fill_indels.py..."
    if ! python3 "$SCRIPT_DIR/scripts/fill_indels.py" -r "$REFERENCE_FASTA" -i "$CURRENT_INPUT" -o "$FILLED_OUTPUT"; then
        echo "Error: fill_indels.py failed"
        exit 1
    fi
    echo "Filled VCF: $FILLED_OUTPUT"
    CURRENT_INPUT="$FILLED_OUTPUT"
fi

# Run bcftools normalization if output is specified
if [ -n "$NORMALIZED_OUTPUT" ]; then
    echo "Running bcftools normalization..."
    if ! bcftools norm -f "$REFERENCE_FASTA" -o "$NORMALIZED_OUTPUT" "$CURRENT_INPUT"; then
        echo "Error: bcftools normalization failed"
        exit 1
    fi
    echo "Normalized VCF: $NORMALIZED_OUTPUT"
fi

echo "Processing complete."
