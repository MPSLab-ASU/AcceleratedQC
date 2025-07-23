#pragma once

#include <vector>
#include <string>
#include <adf.h>
#include "gmio_graph.hpp"

int hadamard_host_xrt(
	const std::string& xclbin_path,
	const std::vector<cfloat>& input_state, 
	std::vector<cfloat>& output_state, 
	int target, 
	int num_qubits
);	
