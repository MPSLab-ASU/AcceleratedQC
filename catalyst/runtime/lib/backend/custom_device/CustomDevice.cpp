#include "CustomDevice.hpp"
#include <complex>
#include <vector>
#include <string>
#include <optional>
#include <iostream>
#include <cmath>
#include <stdexcept>
#include <filesystem>

using std::vector;
using std::string;
using std::optional;
using std::complex;
using std::cout;
using std::cerr;
using std::runtime_error;

// Helper function to print the state vector
void printState(const vector<complex<double>>& state, const string& label) {
    cout << label << ": [";
    for (size_t i = 0; i < state.size(); ++i) {
        cout << state[i].real() << "+" << state[i].imag() << "j";
        if (i < state.size() - 1) cout << ", ";
    }
    cout << "]\n";
}

namespace Catalyst::Runtime::Devices {

CustomDevice::CustomDevice([[maybe_unused]] const string &kwargs) {
    cout << "Constructor: CustomDevice\n";
    cout << "kwargs: " << kwargs << '\n';
    
    // Check if FPGA kernel is available
    if (use_fpga_) {
        std::filesystem::path xclbin_file(xclbin_path_);
        if (!std::filesystem::exists(xclbin_file)) {
            cout << "Warning: FPGA bitstream not found at " << xclbin_path_ 
                 << ", falling back to CPU implementation\n";
            use_fpga_ = false;
        } else {
            cout << "FPGA kernel enabled, using bitstream: " << xclbin_path_ << '\n';
        }
    }
    
    printState(state_, "State after constructor");
}

CustomDevice::~CustomDevice() = default;

bool CustomDevice::useFPGAKernel() const {
    return use_fpga_;
}

void CustomDevice::applyHadamard(QubitIdType wire) {
    if (useFPGAKernel()) {
        // Use FPGA kernel
        cout << "Applying Hadamard on wire " << wire << " using FPGA kernel\n";
        
        vector<complex<double>> output_state(state_.size());
        int status = hadamard_kernel_execute(xclbin_path_, state_, output_state, wire, num_qubits_);
        
        if (status == 0) {
            state_ = std::move(output_state);
            printState(state_, "State after FPGA Hadamard on wire " + std::to_string(wire));
        } else {
            cerr << "FPGA kernel execution failed with status " << status 
                 << ", falling back to CPU implementation\n";
            // Fall back to CPU implementation
            applyHadamardCPU(wire);
        }
    } else {
        // Use CPU implementation
        applyHadamardCPU(wire);
    }
}

void CustomDevice::applyHadamardCPU(QubitIdType wire) {
    cout << "Applying Hadamard on wire " << wire << " using CPU implementation\n";
    size_t dim = 1ULL << num_qubits_;
    vector<complex<double>> new_state(dim, 0.0);
    double sqrt2_inv = 1.0 / sqrt(2.0);

    for (size_t i = 0; i < dim; ++i) {
        size_t idx0 = i;
        size_t idx1 = i ^ (1ULL << wire);
        if (idx0 < idx1) {
            new_state[idx0] = sqrt2_inv * (state_[idx0] + state_[idx1]);
            new_state[idx1] = sqrt2_inv * (state_[idx0] - state_[idx1]);
        }
    }

    state_ = std::move(new_state);
    printState(state_, "State after CPU Hadamard on wire " + std::to_string(wire));
}

void CustomDevice::getState(DataView<complex<double>, 1> &state) {
    if (state.size() != state_.size()) {
        throw runtime_error("State vector size mismatch");
    }
    copy(state_.begin(), state_.end(), state.begin());
}

auto CustomDevice::AllocateQubit() -> QubitIdType {
    cout << "Called: AllocateQubit\n";
    size_t new_num_qubits = num_qubits_ + 1;
    size_t dim = 1ULL << new_num_qubits;
    state_.resize(dim, 0.0);
    state_[0] = 1.0; // Initialize to |0...0>
    num_qubits_ = new_num_qubits;
    printState(state_, "State after AllocateQubit");
    return static_cast<QubitIdType>(new_num_qubits - 1);
}

auto CustomDevice::AllocateQubits(size_t num_qubits) -> vector<QubitIdType> {
    cout << "Called: AllocateQubits\n";
    if (num_qubits == 0) {
        return {};
    }
    size_t current_num_qubits = num_qubits_;
    size_t new_num_qubits = current_num_qubits + num_qubits;
    size_t dim = 1ULL << new_num_qubits;
    state_.resize(dim, 0.0);
    state_[0] = 1.0; // Initialize to |0...0>
    num_qubits_ = new_num_qubits;
    printState(state_, "State after AllocateQubits");

    vector<QubitIdType> qubits(num_qubits);
    for (size_t i = 0; i < num_qubits; ++i) {
        qubits[i] = static_cast<QubitIdType>(current_num_qubits + i);
    }
    return qubits;
}

void CustomDevice::ReleaseQubit(QubitIdType) {
    cout << "Called: ReleaseQubit\n";
    if (num_qubits_ > 0) {
        size_t new_num_qubits = num_qubits_ - 1;
        size_t dim = 1ULL << new_num_qubits;
        state_.resize(dim, 0.0);
        state_[0] = 1.0; // Initialize to |0...0>
        num_qubits_ = new_num_qubits;
        printState(state_, "State after ReleaseQubit");
    }
}

void CustomDevice::ReleaseAllQubits() {
    cout << "Called: ReleaseAllQubits\n";
    num_qubits_ = 0;
    state_.clear();
    printState(state_, "State after ReleaseAllQubits");
}

auto CustomDevice::GetNumQubits() const -> size_t {
    cout << "Called: GetNumQubits\n";
    return num_qubits_;
}

void CustomDevice::SetDeviceShots(size_t shots) {
    cout << "Called: SetDeviceShots with shots: " << shots << '\n';
    // Shots not used in state vector simulation
}

auto CustomDevice::GetDeviceShots() const -> size_t {
    cout << "Called: GetDeviceShots\n";
    return 0; // State vector simulation doesn't use shots
}

void CustomDevice::NamedOperation(const string &name,
                                 const vector<double> &params,
                                 const vector<QubitIdType> &wires,
                                 bool inverse,
                                 const vector<QubitIdType> &ctrl_wires,
                                 const vector<bool> &ctrl_values) {
    if (name == "Hadamard" && wires.size() == 1 && params.empty() && ctrl_wires.empty() && !inverse) {
        cout << "Applying Hadamard gate on wire " << wires[0] << '\n';
        applyHadamard(wires[0]);
    } else {
        cerr << "Unsupported operation: " << name << '\n';
        throw runtime_error("Unsupported operation: " + name);
    }
}

auto CustomDevice::Measure(QubitIdType wire, optional<int32_t> postselect) -> Result {
    cout << "Called: Measure on wire " << wire << '\n';
    bool *result = new bool(true); // Dummy result for |0>
    return result;
}

void CustomDevice::StartTapeRecording() {
    cout << "Called: StartTapeRecording\n";
}

void CustomDevice::StopTapeRecording() {
    cout << "Called: StopTapeRecording\n";
}

void CustomDevice::State(DataView<complex<double>, 1> &state) {
    cout << "Called: State\n";
    getState(state);
}

} // namespace Catalyst::Runtime::Devices

GENERATE_DEVICE_FACTORY(CustomDevice, Catalyst::Runtime::Devices::CustomDevice)