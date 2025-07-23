#include "hadamard_host.hpp"
#include <xrt/xrt_device.h>
#include <xrt/xrt_kernel.h>
#include <xrt/xrt_graph.h>
#include <xrt/xrt_bo.h>

#include <vector>
#include <iostream>

int hadamard_host_xrt(
    const std::string& xclbin_path,
    const std::vector<cfloat>& input_state,
    std::vector<cfloat>& output_state,
    int target,
    int num_qubits
) {
    const int size = 1 << num_qubits;
    if (input_state.size() != size) return -1;

    try {
        // Load device and xclbin
        auto device = xrt::device(0);
        auto uuid = device.load_xclbin(xclbin_path);

        // Open GMIO kernels
        auto gm2aie = xrt::kernel(device, uuid, "in_stream");
        auto aie2gm = xrt::kernel(device, uuid, "out_stream");

        // Open graph
        xrt::graph graph(device, uuid, "hadamardGraph");

        // Allocate buffers
        auto input_bo  = xrt::bo(device, size * sizeof(cfloat), xrt::bo::flags::normal, gm2aie.group_id(0));
        auto output_bo = xrt::bo(device, size * sizeof(cfloat), xrt::bo::flags::normal, aie2gm.group_id(0));

        auto input_ptr  = input_bo.map<cfloat*>();
        auto output_ptr = output_bo.map<cfloat*>();

        std::copy(input_state.begin(), input_state.end(), input_ptr);
        input_bo.sync(XCL_BO_SYNC_BO_TO_DEVICE);

        // Update graph parameters
        graph.update("qubit", target);
        graph.update("num_qubits", num_qubits);

        // Start graph
        graph.run(1);

        // Run GMIO transfers
        auto run_in = gm2aie(input_bo, nullptr, size * sizeof(cfloat));
        auto run_out = aie2gm(output_bo, nullptr, size * sizeof(cfloat));

        run_in.wait();
        run_out.wait();

        output_bo.sync(XCL_BO_SYNC_BO_FROM_DEVICE);
        std::copy(output_ptr, output_ptr + size, output_state.begin());

        graph.end();
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "XRT Error: " << e.what() << "\n";
        return -2;
    }
}

