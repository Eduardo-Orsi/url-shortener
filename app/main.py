from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request, HTTPException,Depends

from .schemas import URLBase, URLInfo
from .controller import URLController
from .database import Base, engine, get_db

app = FastAPI(title="URL Shortener")
Base.metadata.create_all(bind=engine)

@app.post("/create", response_model=URLInfo)
async def create_short_url(url: URLBase, db: Session = Depends(get_db)):
    db_url = URLController.create_url(db=db, url=url)
    return URLController.get_admin_info(db_url)

@app.get("/{url_key}")
async def foward_to_target_url(url_key: str, request: Request, db: Session = Depends(get_db)):
    db_url = URLController.get_url_by_key(db, url_key)
    if not db_url:
        raise HTTPException(404, f"URL '{request.url}' doesn't exist")
    URLController.update_db_clicks(db, db_url)
    return RedirectResponse(db_url.target_url)

@app.get("/admin/{secret_key}", name="Administration info", response_model=URLInfo)
def get_url_info(secret_key: str, db: Session = Depends(get_db)):
    url = URLController.get_url_by_secret_key(db, secret_key=secret_key)
    if not url:
        raise HTTPException(404, "screct key does not exist")
    return URLController.get_admin_info(url)

@app.delete("/admin/{secret_key}")
def delete_url(secret_key: str, db: Session = Depends(get_db)):
    db_url = URLController.deactivate_url_by_secret_key(db, secret_key)
    if not db_url:
        raise HTTPException(404, "The incorrect secret key")
    message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
    return {"detail": message}
