from sqlalchemy.orm import Session
from starlette.datastructures import URL as ServerURL

from .models import URL
from .keygen import Keygen
from .config import get_settings
from .schemas import URLBase, URLInfo
from .schemas import URL as SchemaURL


class URLController:

    @staticmethod
    def get_url_by_key(db: Session, key: str) -> URL:
        return db.query(URL).filter(URL.key == key, URL.is_active).first()

    @staticmethod
    def create_url(db: Session, url: URLBase) -> URL:
        key = Keygen.create_unique_random_key(db)
        secret_key = f"{key}_{Keygen.create_random_key(length=8)}"
        db_url = URL(
            target_url=url.target_url, key=key, secret_key=secret_key
        )
        db.add(db_url)
        db.commit()
        db.refresh(db_url)
        return db_url

    @staticmethod
    def update_db_clicks(db: Session, db_url: SchemaURL) -> URL:
        db_url.clicks += 1
        db.commit()
        db.refresh(db_url)
        return db_url

    @staticmethod
    def get_url_by_secret_key(db: Session, secret_key: str) -> URL:
        return db.query(URL).filter(URL.secret_key == secret_key, URL.is_active).first()

    @staticmethod
    def get_admin_info(db_url: URL) -> URLInfo:
        base_url = ServerURL(get_settings().base_url)
        db_url.url = str(base_url.replace(path=db_url.key))
        db_url.admin_url = str(base_url.replace(path=f"/admin/{db_url.secret_key}"))
        return db_url

    @staticmethod
    def deactivate_url_by_secret_key(db: Session, secret_key: str) -> URL:
        db_url = URLController.get_url_by_secret_key(db, secret_key)
        if not db_url:
            return None
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
        return db_url
