#pragma once

#include <algorithm>
#include <complex>
#include <memory>
#include <optional>
#include <random>
#include <vector>
#include <string>

#include "DataView.hpp"
#include "QuantumDevice.hpp"
#include "QubitManager.hpp"
#include "Types.h"

namespace Catalyst::Runtime::Devices {

struct CustomDevice : public QuantumDevice {
    explicit CustomDevice(const std::string &kwargs);
    ~CustomDevice() override;

    auto AllocateQubit() -> QubitIdType override;
    auto AllocateQubits(size_t num_qubits) -> std::vector<QubitIdType> override;
    void ReleaseQubit(QubitIdType) override;
    void ReleaseAllQubits() override;

    auto GetNumQubits() const -> size_t override;
    void SetDeviceShots(size_t shots) override;
    auto GetDeviceShots() const -> size_t override;

    void NamedOperation(const std::string &name,
                        const std::vector<double> &params,
                        const std::vector<QubitIdType> &wires,
                        bool inverse,
                        const std::vector<QubitIdType> &ctrl_wires,
                        const std::vector<bool> &ctrl_values) override;

    auto Measure(QubitIdType wire, std::optional<int32_t> postselect) -> Result override;

    void StartTapeRecording() override;
    void StopTapeRecording() override;

    void State(DataView<std::complex<double>, 1> &state) override;

private:
    void applyHadamard(QubitIdType wire);
    void getState(DataView<std::complex<double>, 1> &state);

    size_t num_qubits_{0};
    std::vector<std::complex<double>> state_;
};

} // namespace Catalyst::Runtime::Devices