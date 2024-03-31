from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request, HTTPException,Depends

from .models import URL
from .keygen import Keygen
from .schemas import URLBase, URLInfo
from .database import Base, engine, get_db

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.post("/create", response_model=URLInfo)
async def create_short_url(url: URLBase, db: Session = Depends(get_db)):
    key = Keygen.create_random_key()
    secret_key = Keygen.create_random_key(8)
    db_url = URL(
        target_url=url.target_url,
        key=key,
        secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    db_url.url = key
    db_url.admin_url = secret_key
    return db_url

@app.get("/{url_key}")
async def foward_to_target_url(url_key: str, request: Request, db: Session = Depends(get_db)):
    db_url = db.query(URL).filter(URL.key == url_key, URL.is_active).first()
    if not db_url:
        raise HTTPException(404, f"URL '{request.url}' doesn't exist")
    return RedirectResponse(db_url.target_url)
