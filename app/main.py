from typing import Annotated

from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .user import User
from .token import Token
from .controller import URLController
from .database import Base, engine, get_db
from .schemas import URLBase, URLInfo, UserSchema, TokenSchema

app = FastAPI(title="URL Shortener")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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
async def get_url_info(secret_key: str, db: Session = Depends(get_db)):
    url = URLController.get_url_by_secret_key(db, secret_key=secret_key)
    if not url:
        raise HTTPException(404, "screct key does not exist")
    return URLController.get_admin_info(url)

@app.delete("/admin/{secret_key}")
async def delete_url(secret_key: str, db: Session = Depends(get_db)):
    db_url = URLController.deactivate_url_by_secret_key(db, secret_key)
    if not db_url:
        raise HTTPException(404, "The incorrect secret key")
    message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
    return {"detail": message}

@app.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: Annotated[UserSchema, Depends(User.get_current_active_user)]):
    return current_user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenSchema:
    user = User.authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = Token.create_access_token(
        data={"sub": user.username}
    )
    return TokenSchema(access_token=access_token, token_type="bearer")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    }
}
