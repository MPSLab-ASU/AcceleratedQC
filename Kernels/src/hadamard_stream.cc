#include <aie_api/aie.hpp>
#include <adf.h>

#include "hadamard_stream.hpp"

using namespace adf;

void hadamard_stream(
	input_stream_cfloat *input_state,
	output_stream_cfloat *output_state,
	int32 qubit,
	int32 num_qubits
) {
	const int N = 1 << num_qubits;			// Size of state
	const int stride = 1 << qubit;	// Distance between Hadamard pairs

	const float norm = 1.0f / sqrtf(2.0f);

	cfloat state[N];
	for (int i = 0; i < N; ++i) {
		state[i] = readincr(input_state);
	}

	for (int i = 0; i < N; i += 2 * stride) chess_prepare_for_pipelining {
		for ( int j = 0; j < stride; ++j) {
			int idx0 = i + j;
			int idx1 = idx0 + stride;
	
			cfloat a = state[idx0];
			cfloat b = state[idx1];

			state[idx0] = norm * (a + b);
			state[idx1] = norm * (a - b);
		}
	}


	for (int i = 0; i < N; i++) {
		writeincr(output_state, state[i]);
	}
}
	
