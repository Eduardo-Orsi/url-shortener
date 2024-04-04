import secrets
import string

from sqlalchemy.orm import Session


class Keygen:

    @classmethod
    def create_random_key(cls, length: int = 5) -> str:
        chars = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    @classmethod
    def create_unique_random_key(cls, db: Session) -> str:
        from .controller import URLController
        key = Keygen.create_random_key()
        while URLController.get_url_by_key(db, key):
            key = Keygen.create_random_key()
        return key
