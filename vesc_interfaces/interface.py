from abc import ABC, abstractmethod


class VescInterface(ABC):
    type: int = 0

    T_DEV = 1
    T_TCP = 2
    T_GPIO = 3

    connected: bool = False

    full_path: str = ""
    receive_timeout_ms: int = 0

    @abstractmethod
    def __init__(self):
        pass

    def __del__(self):
        try: self.disconnect()
        except: pass

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def receive(self) -> bytes:
        pass

    @abstractmethod
    def send(self, data: bytes):
        pass

    @abstractmethod
    def disconnect(self):
        pass