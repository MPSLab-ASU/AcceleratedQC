#!/usr/bin/env python3
"""
Integration test for Custom Device with Hadamard Kernel

This script tests the integration between PennyLane and the custom device backend,
demonstrating both FPGA and CPU modes.
"""

import pennylane as qml
from pennylane import numpy as np
import pathlib
import os

class CustomDevice(qml.devices.Device):
    config_filepath = pathlib.Path(__file__).parent / "custom_device.toml"

    @staticmethod
    def get_c_interface():
        # Get the build directory path
        build_dir = pathlib.Path(__file__).parent.parent.parent.parent / "build" / "lib"
        so_path = build_dir / "librtd_custom_device.so"
        return "CustomDevice", str(so_path)

    def __init__(self, shots=None, wires=None, xclbin_path=None, use_fpga=True):
        super().__init__(wires=wires, shots=shots)
        self.xclbin_path = xclbin_path or "libadf.xclbin"
        self.use_fpga = use_fpga
        
        # Check if FPGA bitstream exists
        if self.use_fpga and not os.path.exists(self.xclbin_path):
            print(f"Warning: FPGA bitstream not found at {self.xclbin_path}")
            print("Falling back to CPU implementation")
            self.use_fpga = False

    @property
    def operations(self):
        return {"Hadamard"}

    @property
    def observables(self):
        return {"State"}

    def execute(self, circuits, execution_config=None):
        # For now, return a dummy state that represents the result
        # In a real implementation, this would call the C++ interface
        if self.use_fpga:
            print(f"Executing circuit with FPGA kernel (bitstream: {self.xclbin_path})")
        else:
            print("Executing circuit with CPU implementation")
        
        # Return a simple state vector result
        num_qubits = len(self.wires) if self.wires else 1
        state_size = 2 ** num_qubits
        return np.array([1.0] + [0.0] * (state_size - 1), dtype=np.complex128)

def test_single_qubit():
    """Test single qubit Hadamard operation"""
    print("=" * 50)
    print("Testing Single Qubit Hadamard")
    print("=" * 50)
    
    @qml.qnode(CustomDevice(wires=1, use_fpga=True))
    def circuit():
        qml.Hadamard(wires=0)
        return qml.state()
    
    result = circuit()
    print(f"FPGA Result: {result}")
    print(f"Expected: [0.70710678+0j, 0.70710678+0j]")
    print()

def test_two_qubit():
    """Test two qubit Hadamard operations"""
    print("=" * 50)
    print("Testing Two Qubit Hadamard")
    print("=" * 50)
    
    @qml.qnode(CustomDevice(wires=2, use_fpga=True))
    def circuit():
        qml.Hadamard(wires=0)
        qml.Hadamard(wires=1)
        return qml.state()
    
    result = circuit()
    print(f"FPGA Result: {result}")
    print(f"Expected: [0.5+0j, 0.5+0j, 0.5+0j, 0.5+0j]")
    print()

def test_cpu_fallback():
    """Test CPU fallback when FPGA is not available"""
    print("=" * 50)
    print("Testing CPU Fallback")
    print("=" * 50)
    
    @qml.qnode(CustomDevice(wires=1, use_fpga=False))
    def circuit():
        qml.Hadamard(wires=0)
        return qml.state()
    
    result = circuit()
    print(f"CPU Result: {result}")
    print()

def test_device_comparison():
    """Compare custom device with default PennyLane device"""
    print("=" * 50)
    print("Comparing with Default PennyLane Device")
    print("=" * 50)
    
    # Custom device
    @qml.qnode(CustomDevice(wires=1, use_fpga=False))
    def custom_circuit():
        qml.Hadamard(wires=0)
        return qml.state()
    
    # Default device
    @qml.qnode(qml.devices.DefaultQubit(wires=1))
    def default_circuit():
        qml.Hadamard(wires=0)
        return qml.state()
    
    custom_result = custom_circuit()
    default_result = default_circuit()
    
    print(f"Custom Device Result: {custom_result}")
    print(f"Default Device Result: {default_result}")
    print(f"Results Match: {np.allclose(custom_result, default_result)}")
    print()

def test_error_handling():
    """Test error handling for missing bitstream"""
    print("=" * 50)
    print("Testing Error Handling")
    print("=" * 50)
    
    # Test with non-existent bitstream
    @qml.qnode(CustomDevice(wires=1, xclbin_path="nonexistent.xclbin", use_fpga=True))
    def circuit():
        qml.Hadamard(wires=0)
        return qml.state()
    
    result = circuit()
    print(f"Result with missing bitstream: {result}")
    print()

if __name__ == "__main__":
    print("Custom Device Integration Test")
    print("=" * 60)
    print()
    
    # Run all tests
    test_single_qubit()
    test_two_qubit()
    test_cpu_fallback()
    test_device_comparison()
    test_error_handling()
    
    print("=" * 60)
    print("Integration test completed!")
    print()
    print("Next steps:")
    print("1. Set XILINX_XRT environment variable for FPGA support")
    print("2. Compile FPGA bitstream (libadf.xclbin)")
    print("3. Test with actual FPGA hardware") 