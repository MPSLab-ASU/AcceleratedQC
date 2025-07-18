import pennylane as qml
from pennylane import numpy as np
import pathlib

class CustomDevice(qml.devices.Device):
    config_filepath = pathlib.Path(__file__).parent / "custom_device.toml"

    @staticmethod
    def get_c_interface():
        return "CustomDevice", "/catalyst/runtime/build/lib/librtd_custom_device.so"

    def __init__(self, shots=None, wires=None):
        super().__init__(wires=wires, shots=shots)

    @property
    def operations(self):
        return {"Hadamard"}

    @property
    def observables(self):
        return {"State"}

    def execute(self, circuits, execution_config=None):
        return np.array([1.0, 0.0], dtype=np.complex128)  # Dummy state

# Create a simple circuit without qjit for development
@qml.qnode(CustomDevice(wires=1))
def circuit():
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=0)
    return qml.state()

print("Circuit result:", circuit())
