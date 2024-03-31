import secrets
import string


class Keygen:

    @classmethod
    def create_random_key(cls, length: int = 5) -> str:
        chars = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))
