#include "hadamard_host.hpp"
#include <vector>
#include <iostream>

int main() {
    const std::string xclbin_path = "libadf.xclbin";
    const int num_qubits = 3;
    const int target = 1;
    const int size = 1 << num_qubits;

    std::vector<cfloat> input(size, {0.0f, 0.0f});
    std::vector<cfloat> output(size);

    input[0] = {1.0f, 0.0f};

    int status = hadamard_host_xrt(xclbin_path, input, output, target, num_qubits);
    if (status != 0) {
        std::cerr << "Execution failed with status " << status << "\n";
        return 1;
    }

    for (const auto& c : output) {
        std::cout << c.real << " + " << c.imag << "j\n";
    }

    return 0;
}

