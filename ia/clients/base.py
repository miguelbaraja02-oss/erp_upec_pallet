from abc import ABC, abstractmethod


class BaseIAClient(ABC):
    @abstractmethod
    def chat(self, messages, **options):
        raise NotImplementedError

    @abstractmethod
    def generate_text(self, prompt, **options):
        raise NotImplementedError

    @abstractmethod
    def health_check(self):
        raise NotImplementedError
