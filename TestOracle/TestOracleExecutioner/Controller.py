from abc import ABC, abstractmethod
from typing import List

class ControllerInterface(ABC):
    """The Controller Interface defines methods for managing features and UI views."""

    @abstractmethod
    def activate(self, deactivations: List[str], activations: List[str]) -> int:
        """
        The "activate" method is responsible for (de)activating features.
        A feature *must* be mentioned in the feature model (which can be updated), 
        and only features in the feature model can be (de)activated.
        
        :param deactivations: List of feature names to deactivate.
        :param activations: List of feature names to activate.
        :return: 0 if the (de)activations were successful, 
                or another integer indicating an issue (e.g. feature name not in the feature model).
        """
        pass

    @abstractmethod
    def enableUIView(self) -> bool:
        """
        The "enableUIView" method makes the UI View visible and usable.
        
        :return: True if the UI View was successfully established, 
                 or False if there was an issue.
        """
        pass

    @abstractmethod
    def disableUIView(self) -> bool:
        """
        The "disableUIView" method makes the UI invisible and unusable.
        The Controller methods should be non-blocking when the UI View is disabled.
        
        :return: True if the UI View was successfully disabled, 
                 or False if there was an issue.
        """
        pass

    @abstractmethod
    def getStateAsLog(self) -> List[str]:
        """
        The "getStateAsLog" method is used to get the system's state in the form of logs.
        It should only contain the description of the current state (not the previous states).
        
        :return: A list of strings representing the current state of the system in text.
        """
        pass
