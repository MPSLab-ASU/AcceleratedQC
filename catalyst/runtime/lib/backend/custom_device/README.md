# Custom Device with Hadamard Kernel Integration

This directory contains a custom device backend for the AMD Catalyst runtime that integrates the Hadamard kernel from the `Kernels/` directory for FPGA acceleration.

## Overview

The custom device provides:
- **FPGA Acceleration**: Uses AMD/Xilinx AI Engine (AIE) for Hadamard gate operations
- **CPU Fallback**: Automatic fallback to CPU implementation when FPGA is unavailable
- **PennyLane Integration**: Seamless integration with PennyLane quantum computing framework
- **XRT Support**: Uses Xilinx Runtime (XRT) for host-FPGA communication

## Files

- `CustomDevice.hpp/cpp`: Main device implementation with FPGA/CPU switching
- `HadamardKernelWrapper.cpp`: Interface to the Hadamard kernel from `Kernels/`
- `circuit.py`: Python interface for PennyLane integration
- `custom_device.toml`: Device configuration for PennyLane
- `CMakeLists.txt`: Build configuration with XRT dependencies
- `build.sh`: Build script for easy compilation

## Building

### Prerequisites

1. **XRT Installation**: Set `XILINX_XRT` environment variable
2. **Vitis Installation**: Set `XILINX_VITIS` environment variable (optional)
3. **AMD Catalyst Runtime**: Built and available

### Build Steps

```bash
# Navigate to the custom device directory
cd catalyst/runtime/lib/backend/custom_device

# Run the build script
./build.sh
```

The build script will:
1. Check for XRT/Vitis availability
2. Compile the custom device with kernel integration
3. Create the shared library `librtd_custom_device.so`

## Usage

### Python Interface

```python
import pennylane as qml

# Create device with FPGA kernel
dev = CustomDevice(wires=2, use_fpga=True, xclbin_path="libadf.xclbin")

# Create quantum circuit
@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    return qml.state()

# Execute circuit
result = circuit()
print(result)
```

### C++ Interface

The device automatically switches between FPGA and CPU implementations:

- **FPGA Mode**: Uses the Hadamard kernel from `Kernels/src/`
- **CPU Mode**: Uses optimized CPU implementation as fallback

## Kernel Integration

The integration works as follows:

1. **Python Layer**: `circuit.py` provides PennyLane device interface
2. **C++ Layer**: `CustomDevice.cpp` manages state and operation dispatch
3. **Kernel Layer**: `HadamardKernelWrapper.cpp` interfaces with FPGA kernel
4. **FPGA Layer**: `Kernels/src/hadamard_host_xrt.cpp` handles XRT communication

## Configuration

### Environment Variables

- `XILINX_XRT`: Path to XRT installation
- `XILINX_VITIS`: Path to Vitis installation (for AIE tools)

### Device Parameters

- `use_fpga`: Enable/disable FPGA kernel usage (default: true)
- `xclbin_path`: Path to FPGA bitstream file (default: "libadf.xclbin")

## Testing

```bash
# Test the custom device
python3 circuit.py
```

This will test both FPGA and CPU implementations.

## Troubleshooting

### Common Issues

1. **XRT not found**: Set `XILINX_XRT` environment variable
2. **Bitstream not found**: Ensure `libadf.xclbin` exists or specify correct path
3. **Build failures**: Check that AMD Catalyst runtime is properly built

### Debug Information

The device provides verbose output showing:
- FPGA vs CPU mode selection
- Kernel execution status
- State vector transformations

## Next Steps

1. **Add More Gates**: Extend to support other quantum gates
2. **Optimize Performance**: Improve kernel efficiency
3. **Add Error Correction**: Implement quantum error correction
4. **Multi-Device Support**: Support multiple FPGA devices 