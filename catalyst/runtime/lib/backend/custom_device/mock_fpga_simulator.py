#!/usr/bin/env python3
"""
Mock FPGA Simulator for Hadamard Kernel Testing

This simulator mimics FPGA behavior to test the kernel integration
without requiring actual FPGA hardware or tools.
"""

import numpy as np
import time
import random

class MockFPGASimulator:
    """Simulates FPGA behavior for Hadamard kernel testing"""
    
    def __init__(self, xclbin_path="mock_libadf.xclbin"):
        self.xclbin_path = xclbin_path
        self.simulated_latency = 0.001  # 1ms simulation latency
        self.error_rate = 0.01  # 1% error rate for realism
        
    def simulate_fpga_execution(self, input_state, target_qubit, num_qubits):
        """
        Simulate FPGA execution of Hadamard kernel
        
        Args:
            input_state: Input quantum state vector
            target_qubit: Target qubit for Hadamard operation
            num_qubits: Number of qubits in system
            
        Returns:
            output_state: Transformed quantum state vector
            execution_time: Simulated execution time
            status: Success/failure status
        """
        
        print(f"🔧 Mock FPGA: Loading bitstream {self.xclbin_path}")
        print(f"🔧 Mock FPGA: Initializing AI Engine cores")
        
        # Simulate FPGA initialization time
        time.sleep(self.simulated_latency)
        
        # Simulate occasional FPGA errors
        if random.random() < self.error_rate:
            print("🔧 Mock FPGA: Simulated hardware error")
            return None, 0.0, -1
        
        # Perform actual Hadamard transformation (same as CPU)
        output_state = self._apply_hadamard_fpga(input_state, target_qubit, num_qubits)
        
        # Simulate FPGA execution time
        execution_time = self.simulated_latency + random.uniform(0.0001, 0.0005)
        
        print(f"🔧 Mock FPGA: Execution completed in {execution_time:.6f}s")
        print(f"🔧 Mock FPGA: AI Engine cores idle")
        
        return output_state, execution_time, 0
    
    def _apply_hadamard_fpga(self, state, target_qubit, num_qubits):
        """Simulate FPGA implementation of Hadamard gate"""
        
        # This is the same algorithm as CPU, but simulates FPGA execution
        result = state.copy()
        dim = 1 << num_qubits
        sqrt2_inv = 1.0 / np.sqrt(2.0)
        
        # Simulate parallel FPGA processing
        print(f"🔧 Mock FPGA: Processing {dim} state elements in parallel")
        
        for i in range(dim):
            idx0 = i
            idx1 = i ^ (1 << target_qubit)
            if idx0 < idx1:
                temp0 = result[idx0]
                temp1 = result[idx1]
                result[idx0] = sqrt2_inv * (temp0 + temp1)
                result[idx1] = sqrt2_inv * (temp0 - temp1)
        
        return result
    
    def get_fpga_status(self):
        """Simulate FPGA status check"""
        return {
            "device_count": 1,
            "device_name": "Mock FPGA Device",
            "memory_size": "8GB",
            "temperature": random.uniform(45, 65),
            "utilization": random.uniform(20, 80)
        }

def test_mock_fpga():
    """Test the mock FPGA simulator"""
    
    print("🧪 Testing Mock FPGA Simulator")
    print("=" * 50)
    
    # Create simulator
    fpga = MockFPGASimulator()
    
    # Test single qubit
    print("\n1. Single Qubit Test:")
    input_state = np.array([1.0, 0.0], dtype=np.complex128)
    output_state, exec_time, status = fpga.simulate_fpga_execution(input_state, 0, 1)
    
    if status == 0:
        print(f"Success: {output_state}")
        print(f"Execution time: {exec_time:.6f}s")
    else:
        print("Simulated FPGA error")
    
    # Test two qubit
    print("\n2. Two Qubit Test:")
    input_state = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128)
    output_state, exec_time, status = fpga.simulate_fpga_execution(input_state, 0, 2)
    
    if status == 0:
        print(f"Success: {output_state}")
        print(f"Execution time: {exec_time:.6f}s")
    else:
        print("Simulated FPGA error")
    
    # Show FPGA status
    print("\n3. FPGA Status:")
    status = fpga.get_fpga_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\nMock FPGA simulation completed!")

if __name__ == "__main__":
    test_mock_fpga() 