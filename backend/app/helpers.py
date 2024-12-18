
from typing import Literal
from typing import List, Dict, AnyStr
from abc import ABC, abstractmethod


class LLMResponseManager(ABC):
    """
        Add history from LLM to the manager.
        
        :role: SYSTEM, USER, ASSITANT.
    """
    @abstractmethod
    def add_response(self, role: str, content: str) -> None:
        pass
    """
        Returns history of LLMs chat
    """
    
    @abstractmethod
    def get_responses(self) -> List[str]:
        pass
    
    """
        Allow indexing into the history list to retrieve an Interaction object.
        
        :param index: The index of the desired interaction.
        :return: The Interaction object at the specified index.
    """
    @abstractmethod
    def __getitem__(self, index:int) -> Dict[str, str]:
        pass

class InMemoryResponseManager(LLMResponseManager):
    def __init__(self):
        """Initialize an empty dict to store responses."""
        self.messages: List[Dict[str, str]] = []  # prompt and response pair, if multiple choices then a list  
        

    def add_response(self, role:str, content: Dict):
        if not role in ["system", "user", "assistant"]:
            raise ValueError(f"Role in correct type: VALID TYPES: [system, user, assistant] give {role}")

        self.messages.append({"role": role, "content": content})
    
    def get_responses(self) -> List[Dict[str, str]]:
        return self.messages
    
    def __getitem__(self, index):
        """Common method to retrieve a specific item by index."""
        if 0 <= index < len(self.messages):
            return self.messages[index]
        else:
            raise IndexError("Response index out of range.")
    
    
    