# AcceleratedQC

This repository contains the main codebase for the AcceleratedQC project, including the `catalyst` component, quantum kernels, and a submodule reference to the official LLVM project.

## Repository Structure

- `catalyst/` — Main project code and scripts
- `Kernels/` — Quantum computing kernels (Hadamard, etc.)
- `llvm-project/` — LLVM project (added as a submodule)


### Hadamard Kernel Integration

The project includes a functional Hadamard kernel integration that enables FPGA-accelerated quantum computing through PennyLane. This integration provides:

- **Real Quantum Transformations**: Produces correct quantum superposition states
- **FPGA Acceleration**: Uses AMD/Xilinx AI Engine for high-performance operations
- **CPU Fallback**: Automatic fallback when FPGA hardware unavailable
- **PennyLane Integration**: Integration with quantum computing framework
- **Multi-qubit Support**: Handles 1, 2, 3+ qubit systems

#### Example Output

```python
# Single Qubit Hadamard
Input:  |0⟩ = [1, 0]
Output: |+⟩ = [0.70710678+0j, 0.70710678+0j]

# Two Qubit Hadamard  
Input:  |00⟩ = [1, 0, 0, 0]
Output: |++⟩ = [0.5+0j, 0.5+0j, 0.5+0j, 0.5+0j]
```

## Setup Instructions

### 1. Clone the Repository

Clone this repository and initialize submodules:

```bash
git clone --recurse-submodules https://github.com/MPSLab-ASU/AcceleratedQC.git
cd AcceleratedQC
```

If you already cloned without `--recurse-submodules`, run:

```bash
git submodule update --init --recursive
```

### 2. Install Dependencies

Navigate to the `catalyst` directory and install Python dependencies:

```bash
cd catalyst
pip install -r requirements.txt
```

### 3. Building LLVM (Optional)

If you need to build LLVM from source, follow the instructions in `llvm-project/README.md`.

## Hadamard Kernel Integration - Step-by-Step Execution

### Prerequisites

1. **Python Environment**: Python 3.8+ with PennyLane
2. **C++ Compiler**: Clang/GCC for building the custom device
3. **XRT (Optional)**: For FPGA acceleration (set `XILINX_XRT` environment variable)
4. **Vitis (Optional)**: For AIE tools (set `XILINX_VITIS` environment variable)

### Step 1: Build the Custom Device

Navigate to the custom device directory and build the integration:

```bash
cd catalyst/runtime/lib/backend/custom_device
./build.sh
```

This will:
- Check for XRT/Vitis availability
- Compile the custom device with kernel integration
- Create the shared library `librtd_custom_device.so`

**Expected Output:**
```
Building Custom Device with Hadamard Kernel Integration...
✓ Custom device library built successfully
```

### Step 2: Test Basic Integration

Run the basic test to verify the integration:

```bash
python3 circuit.py
```

**Expected Output:**
```
Warning: FPGA bitstream not found at libadf.xclbin
Falling back to CPU implementation
✓ Loaded C++ library: /path/to/librtd_custom_device.so
Testing CustomDevice with real Hadamard kernel...
After Hadamard on qubit 0: [0.70710678+0j, 0.70710678+0j]
Circuit result: (0.7071067811865475+0j)
Expected for 1 qubit: [0.70710678+0j, 0.70710678+0j]
Results match expected: True
```

### Step 3: Run Comprehensive Tests

Execute the comprehensive test suite:

```bash
python3 test_hadamard_output.py
```

**Expected Output:**
```
REAL HADAMARD KERNEL OUTPUT DEMONSTRATION
============================================================
SINGLE QUBIT HADAMARD TRANSFORMATION
Input state: |0⟩ = [1, 0]
Expected output: |+⟩ = [0.70710678, 0.70710678]
Actual output: [0.70710678+0j, 0.70710678+0j]
Matches expected: True

TWO QUBIT HADAMARD TRANSFORMATION
Input state: |00⟩ = [1, 0, 0, 0]
Expected output: |++⟩ = [0.5, 0.5, 0.5, 0.5]
Actual output: [0.5+0j, 0.5+0j, 0.5+0j, 0.5+0j]
Matches expected: True
```

### Step 4: Use with PennyLane (Optional)

Create your own quantum circuits using the custom device:

```python
import pennylane as qml
from pennylane import numpy as np

# Create custom device
dev = CustomDevice(wires=2, use_fpga=True)

# Define quantum circuit
@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    return qml.state()

# Execute circuit
result = circuit()
print(f"Quantum state: {result}")
```

## Architecture Overview

The Hadamard integration uses a multi-layer architecture:

```
┌─────────────────┐
│   PennyLane     │ ← Python quantum computing interface
├─────────────────┤
│  Custom Device  │ ← C++ device implementation
├─────────────────┤
│ Kernel Wrapper  │ ← C++/Python interface
├─────────────────┤
│  FPGA Kernel    │ ← XRT-based FPGA communication
└─────────────────┘
```

### Key Components

1. **Python Layer** (`circuit.py`): PennyLane device interface
2. **C++ Layer** (`CustomDevice.cpp`): Device implementation with FPGA/CPU switching
3. **Kernel Layer** (`HadamardKernelWrapper.cpp`): Interface to FPGA kernel
4. **Hardware Layer** (`Kernels/src/`): XRT-based FPGA communication

## Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Check if LLVM is properly built
   cd catalyst/runtime
   make clean && make runtime
   ```

2. **Library Not Found**:
   ```bash
   # Verify shared library exists
   ls -la catalyst/runtime/build/lib/librtd_custom_device.so
   ```

3. **FPGA Kernel Unavailable**:
   - This is expected if XRT is not installed
   - System will automatically fall back to CPU implementation
   - Check environment variables: `echo $XILINX_XRT`

4. **Python Import Errors**:
   ```bash
   # Install PennyLane if not available
   pip install pennylane
   ```

### Debug Information

The system provides verbose output showing:
- FPGA vs CPU mode selection
- Kernel execution status
- State vector transformations
- Error messages and fallback information

## Advanced Usage

### FPGA Acceleration

To enable FPGA acceleration:

1. **Install XRT**:
   ```bash
   export XILINX_XRT=/path/to/xrt
   ```

2. **Compile FPGA Bitstream**:
   ```bash
   cd Kernels
   # Follow FPGA compilation instructions
   ```

3. **Test with FPGA**:
   ```bash
   python3 circuit.py  # Will use FPGA if available
   ```

### Custom Quantum Circuits

Extend the system to support additional quantum gates:

1. **Add New Gates**: Modify `CustomDevice.cpp` to support new operations
2. **Update Kernel**: Add corresponding FPGA kernel implementations
3. **Test Integration**: Create test cases for new functionality

## Performance Characteristics

- **CPU Mode**: Optimized C++ implementation with O(2^n) complexity
- **FPGA Mode**: Parallel FPGA implementation with hardware acceleration
- **Memory Usage**: State vector scales as O(2^n) for n qubits
- **Precision**: Machine precision (typically 1e-15 for double precision)

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-gate`
3. **Implement your changes**
4. **Add tests**: Create comprehensive test cases
5. **Submit a pull request**

## Documentation

- **Integration Details**: See `catalyst/runtime/lib/backend/custom_device/README.md`
- **Worklog**: See `catalyst/runtime/lib/backend/custom_device/worklog2.txt`
- **Kernel Documentation**: See `Kernels/README.md`

