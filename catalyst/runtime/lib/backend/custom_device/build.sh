#!/bin/bash

# Build script for Custom Device with Hadamard Kernel Integration
# This script compiles the custom device backend with FPGA kernel support

set -e

echo "Building Custom Device with Hadamard Kernel Integration..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
BUILD_DIR="$RUNTIME_DIR/build"

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Check if XRT is available
if [ -z "$XILINX_XRT" ]; then
    echo "Warning: XILINX_XRT environment variable not set"
    echo "FPGA kernel functionality will be disabled"
fi

if [ -z "$XILINX_VITIS" ]; then
    echo "Warning: XILINX_VITIS environment variable not set"
    echo "AIE tools may not be available"
fi

# Change to the runtime directory
cd "$RUNTIME_DIR"

# Build the runtime with custom device
echo "Building runtime with custom device..."
make runtime

echo "Build completed successfully!"
echo "Custom device library should be available at: $BUILD_DIR/lib/librtd_custom_device.so"

# Test if the library was built
if [ -f "$BUILD_DIR/lib/librtd_custom_device.so" ]; then
    echo "✓ Custom device library built successfully"
else
    echo "✗ Custom device library not found"
    exit 1
fi

echo ""
echo "To test the custom device, run:"
echo "cd $SCRIPT_DIR"
echo "python3 circuit.py" 