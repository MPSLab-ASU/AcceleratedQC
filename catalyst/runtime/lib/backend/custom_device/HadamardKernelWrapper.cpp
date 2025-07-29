#include "CustomDevice.hpp"
#include <vector>
#include <complex>
#include <string>
#include <iostream>

// Try to include the Hadamard kernel interface
#ifdef HAS_HADAMARD_KERNEL
#include "../../../../Kernels/src/hadamard_host.hpp"
#endif

namespace Catalyst::Runtime::Devices {

int hadamard_kernel_execute(
    const std::string& xclbin_path,
    const std::vector<std::complex<double>>& input_state, 
    std::vector<std::complex<double>>& output_state, 
    int target, 
    int num_qubits
) {
#ifdef HAS_HADAMARD_KERNEL
    try {
        // Convert from std::complex<double> to cfloat (complex float)
        std::vector<cfloat> input_cfloat;
        std::vector<cfloat> output_cfloat;
        
        input_cfloat.reserve(input_state.size());
        for (const auto& c : input_state) {
            input_cfloat.push_back({static_cast<float>(c.real()), static_cast<float>(c.imag())});
        }
        
        output_cfloat.resize(input_state.size());
        
        // Call the XRT Hadamard kernel
        int status = hadamard_host_xrt(xclbin_path, input_cfloat, output_cfloat, target, num_qubits);
        
        if (status == 0) {
            // Convert back from cfloat to std::complex<double>
            output_state.clear();
            output_state.reserve(output_cfloat.size());
            for (const auto& c : output_cfloat) {
                output_state.push_back({static_cast<double>(c.real), static_cast<double>(c.imag)});
            }
            return 0;
        } else {
            std::cerr << "Hadamard kernel execution failed with status: " << status << std::endl;
            return status;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Exception in hadamard_kernel_execute: " << e.what() << std::endl;
        return -1;
    }
#else
    // Fallback implementation when kernel is not available
    std::cerr << "FPGA kernel not available, using CPU fallback" << std::endl;
    
    // Simple CPU implementation of Hadamard
    output_state = input_state;
    size_t dim = 1ULL << num_qubits;
    double sqrt2_inv = 1.0 / sqrt(2.0);
    
    for (size_t i = 0; i < dim; ++i) {
        size_t idx0 = i;
        size_t idx1 = i ^ (1ULL << target);
        if (idx0 < idx1) {
            auto temp0 = output_state[idx0];
            auto temp1 = output_state[idx1];
            output_state[idx0] = sqrt2_inv * (temp0 + temp1);
            output_state[idx1] = sqrt2_inv * (temp0 - temp1);
        }
    }
    
    return 0;
#endif
}

} // namespace Catalyst::Runtime::Devices

// C-style wrapper for Python ctypes
extern "C" {
    int hadamard_kernel_execute_c(const char* xclbin_path,
                                  const double* input_real, const double* input_imag,
                                  double* output_real, double* output_imag,
                                  int target, int num_qubits, int state_size) {
        try {
            // Convert C arrays to C++ vectors
            std::string xclbin_str(xclbin_path);
            std::vector<std::complex<double>> input_state;
            std::vector<std::complex<double>> output_state;
            
            input_state.reserve(state_size);
            for (int i = 0; i < state_size; ++i) {
                input_state.push_back({input_real[i], input_imag[i]});
            }
            
            // Call the C++ function
            int status = Catalyst::Runtime::Devices::hadamard_kernel_execute(
                xclbin_str, input_state, output_state, target, num_qubits);
            
            if (status == 0) {
                // Copy results back to C arrays
                for (int i = 0; i < state_size; ++i) {
                    output_real[i] = output_state[i].real();
                    output_imag[i] = output_state[i].imag();
                }
            }
            
            return status;
        } catch (const std::exception& e) {
            std::cerr << "Exception in C wrapper: " << e.what() << std::endl;
            return -1;
        }
    }
} 