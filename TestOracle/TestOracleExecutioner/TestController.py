from TestOracle.TestOracleExecutioner.ControllerFramework import ControllerInterface
from typing import List
from abc import ABC, abstractmethod


class EmergencyController(ControllerInterface):
    def __init__(self):
        self.emergency_level = 0
        self.features = {"High", "Low"}

    def activate(self, deactivations: List[str], activations: List[str]) -> int:
        # Validate input
        if not all(feature in self.features for feature in deactivations + activations):
            return -1  # Invalid feature name

        # Process deactivations first
        for feature in deactivations:
            if feature == "Low" and self.emergency_level == 1:
                self.emergency_level = 0
            elif feature == "High":
                # High deactivation depends on the final Low state
                if "Low" in activations:
                    self.emergency_level = 1
                else:
                    self.emergency_level = 0

        # Process activations
        for feature in activations:
            if feature == "Low" and self.emergency_level < 2:
                self.emergency_level += 1
            elif feature == "High":
                self.emergency_level = 2

        return 0

    def enable_UI_view(self) -> bool:
        return True  # No actual UI, but function must work

    def disable_UI_view(self) -> bool:
        return True  # No actual UI, but function must work

    def get_state_as_log(self) -> List[str]:
        return [f"Emergency level: {self.emergency_level}"]
