from ia.clients import build_ia_client
from ia.exceptions import IAError


class IAService:
    """Application-level entry point for AI features."""

    def __init__(self, user=None, company=None, client=None):
        self.user = user
        self.company = company
        self.client = client or build_ia_client()

    def is_available(self):
        try:
            return self.client.health_check()
        except IAError:
            return False

    def chat(self, messages, **options):
        return self.client.chat(messages, **options)

    def stream_chat(self, messages, **options):
        return self.client.stream_chat(messages, **options)

    def generate_text(self, prompt, **options):
        return self.client.generate_text(prompt, **options)


def get_ia_service(user=None, company=None):
    return IAService(user=user, company=company)
