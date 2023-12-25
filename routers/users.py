import sys
sys.path.append("..")
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends, HTTPException, status, APIRouter,Request,Response,Form
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .auth  import get_current_user,verify_password,get_password_hash
SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


templates=Jinja2Templates(directory="templates")
router = APIRouter(prefix="/users",tags=["users"],responses={404:{"description":"Not Found"}})
def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()
class UserVerification(BaseModel):
    username:str
    password:str
    new_password:str





@router.get("/change",response_class=HTMLResponse)
async def edit_user_view(request:Request):
    user=await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth",status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("change.html",
                                      {"request":request, "user":user})
@router.post("/change", response_class=HTMLResponse)
async def user_password_change(request:Request, username:str=Form(...),
                               password:str=Form(...),new_password:str=Form(...),
                               db:Session=Depends(get_db)):
    user=await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    user_data=db.query(models.Users).filter(models.Users.username==username).first()
    msg="invalid username or password"
    if user_data is not None:
        if username==user_data.username and verify_password(password,user_data.hashed_password):
            user_data.hashed_password=get_password_hash(new_password)
            user_data.password=new_password
            db.add(user_data)
            db.commit()
            msg=" password updated"
        return templates.TemplateResponse("change.html", {"request":request,"user":user, "msg":msg})

