#pragma once

#include <adf/stream/types.h>

void hadamard_stream(
	input_stream_cfloat *input_state,
	output_stream_cfloat *output_state,
	int32 qubit,
	int32 num_qubits
);
