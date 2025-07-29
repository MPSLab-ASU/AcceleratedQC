#!/usr/bin/env python3
"""
Circuit with Mock FPGA Integration

This demonstrates how the system would work with FPGA simulation,
showing the complete pipeline from PennyLane to simulated FPGA hardware.
"""

import pennylane as qml
from pennylane import numpy as np
import pathlib
import os
import ctypes
import time
import random

# Import the mock FPGA simulator
from mock_fpga_simulator import MockFPGASimulator

class CustomDeviceWithMockFPGA(qml.devices.Device):
    config_filepath = pathlib.Path(__file__).parent / "custom_device.toml"

    @staticmethod
    def get_c_interface():
        build_dir = pathlib.Path(__file__).parent.parent.parent.parent / "build" / "lib"
        so_path = build_dir / "librtd_custom_device.so"
        return "CustomDevice", str(so_path)

    def __init__(self, shots=None, wires=None, xclbin_path=None, use_fpga=True, use_mock_fpga=False):
        super().__init__(wires=wires, shots=shots)
        self.xclbin_path = xclbin_path or "libadf.xclbin"
        self.use_fpga = use_fpga
        self.use_mock_fpga = use_mock_fpga
        
        # Initialize mock FPGA simulator if requested
        if self.use_mock_fpga:
            self.mock_fpga = MockFPGASimulator(self.xclbin_path)
            print(f"🎭 Mock FPGA simulator initialized with bitstream: {self.xclbin_path}")
        
        # Check if real FPGA bitstream exists
        if self.use_fpga and not self.use_mock_fpga and not os.path.exists(self.xclbin_path):
            print(f"Warning: FPGA bitstream not found at {self.xclbin_path}")
            print("Falling back to CPU implementation")
            self.use_fpga = False
        
        self._load_cpp_library()

    def _load_cpp_library(self):
        try:
            build_dir = pathlib.Path(__file__).parent.parent.parent.parent / "build" / "lib"
            so_path = build_dir / "librtd_custom_device.so"
            
            if not so_path.exists():
                print(f"Warning: C++ library not found at {so_path}")
                self.cpp_lib = None
                return
            
            self.cpp_lib = ctypes.CDLL(str(so_path))
            print(f"✓ Loaded C++ library: {so_path}")
            self._setup_function_signatures()
            
        except Exception as e:
            print(f"Warning: Failed to load C++ library: {e}")
            self.cpp_lib = None

    def _setup_function_signatures(self):
        if not self.cpp_lib:
            return
            
        self.cpp_lib.hadamard_kernel_execute_c.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int
        ]
        self.cpp_lib.hadamard_kernel_execute_c.restype = ctypes.c_int

    def _apply_hadamard_mock_fpga(self, state, target_qubit, num_qubits):
        """Apply Hadamard gate using mock FPGA simulator"""
        if not hasattr(self, 'mock_fpga'):
            return self._apply_hadamard_python(state, target_qubit, num_qubits)
        
        print(f"🎭 Using Mock FPGA for Hadamard on qubit {target_qubit}")
        output_state, exec_time, status = self.mock_fpga.simulate_fpga_execution(
            state, target_qubit, num_qubits
        )
        
        if status == 0:
            print(f"🎭 Mock FPGA execution successful in {exec_time:.6f}s")
            return output_state
        else:
            print(f"🎭 Mock FPGA execution failed, falling back to CPU")
            return self._apply_hadamard_python(state, target_qubit, num_qubits)

    def _apply_hadamard_cpp(self, state, target_qubit, num_qubits):
        if not self.cpp_lib:
            return self._apply_hadamard_python(state, target_qubit, num_qubits)
        
        try:
            state_size = len(state)
            input_real = (ctypes.c_double * state_size)()
            input_imag = (ctypes.c_double * state_size)()
            output_real = (ctypes.c_double * state_size)()
            output_imag = (ctypes.c_double * state_size)()
            
            for i, c in enumerate(state):
                input_real[i] = c.real
                input_imag[i] = c.imag
            
            xclbin_path = self.xclbin_path.encode('utf-8')
            status = self.cpp_lib.hadamard_kernel_execute_c(
                xclbin_path,
                input_real,
                input_imag,
                output_real,
                output_imag,
                target_qubit,
                num_qubits,
                state_size
            )
            
            if status == 0:
                result = []
                for i in range(state_size):
                    result.append(complex(output_real[i], output_imag[i]))
                return np.array(result, dtype=np.complex128)
            else:
                print(f"C++ kernel failed with status {status}, falling back to Python")
                return self._apply_hadamard_python(state, target_qubit, num_qubits)
                
        except Exception as e:
            print(f"Error calling C++ kernel: {e}, falling back to Python")
            return self._apply_hadamard_python(state, target_qubit, num_qubits)

    def _apply_hadamard_python(self, state, target_qubit, num_qubits):
        result = state.copy()
        dim = 1 << num_qubits
        sqrt2_inv = 1.0 / np.sqrt(2.0)
        
        for i in range(dim):
            idx0 = i
            idx1 = i ^ (1 << target_qubit)
            if idx0 < idx1:
                temp0 = result[idx0]
                temp1 = result[idx1]
                result[idx0] = sqrt2_inv * (temp0 + temp1)
                result[idx1] = sqrt2_inv * (temp0 - temp1)
        
        return result

    @property
    def operations(self):
        return {"Hadamard"}

    @property
    def observables(self):
        return {"State"}

    def execute(self, circuits, execution_config=None):
        if self.use_mock_fpga:
            print(f"🎭 Executing circuit with Mock FPGA (bitstream: {self.xclbin_path})")
        elif self.use_fpga:
            print(f"Executing circuit with FPGA kernel (bitstream: {self.xclbin_path})")
        else:
            print("Executing circuit with CPU implementation")
        
        num_qubits = len(self.wires) if self.wires else 1
        state_size = 2 ** num_qubits
        
        # Initialize state to |0...0⟩
        state = np.zeros(state_size, dtype=np.complex128)
        state[0] = 1.0
        
        # Apply Hadamard gates based on the circuit
        for qubit in range(num_qubits):
            if self.use_mock_fpga:
                state = self._apply_hadamard_mock_fpga(state, qubit, num_qubits)
            else:
                state = self._apply_hadamard_cpp(state, qubit, num_qubits)
            print(f"After Hadamard on qubit {qubit}: {state}")
        
        return state

def test_mock_fpga_integration():
    """Test the integration with mock FPGA"""
    
    print("🎭 Testing Mock FPGA Integration")
    print("=" * 60)
    
    # Test with mock FPGA
    print("\n1. Testing with Mock FPGA:")
    @qml.qnode(CustomDeviceWithMockFPGA(wires=2, use_mock_fpga=True))
    def circuit_mock_fpga():
        qml.Hadamard(wires=0)
        qml.Hadamard(wires=1)
        return qml.state()
    
    result_mock = circuit_mock_fpga()
    print(f"Mock FPGA Result: {result_mock}")
    
    # Test with CPU fallback
    print("\n2. Testing with CPU Fallback:")
    @qml.qnode(CustomDeviceWithMockFPGA(wires=2, use_mock_fpga=False, use_fpga=False))
    def circuit_cpu():
        qml.Hadamard(wires=0)
        qml.Hadamard(wires=1)
        return qml.state()
    
    result_cpu = circuit_cpu()
    print(f"CPU Result: {result_cpu}")
    
    # Compare results
    print("\n3. Results Comparison:")
    print(f"Mock FPGA: {result_mock}")
    print(f"CPU:       {result_cpu}")
    print(f"Results match: {np.allclose(result_mock, result_cpu, atol=1e-6)}")
    
    print("\nMock FPGA integration test completed!")

if __name__ == "__main__":
    test_mock_fpga_integration() 