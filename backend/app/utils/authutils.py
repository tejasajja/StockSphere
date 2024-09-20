from fastapi import APIRouter, HTTPException, Request,Depends,Body
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from typing import List,Optional,Any
import yfinance as yf
from app.models import Customer
from app.routes.schemas import CustomerRequenst,CustomerResponse,UserAuth,TokenSchema,TokenPayload
from fastapi import APIRouter, HTTPException
from ..database.mongo import get_collections
from bson import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from app.utils import securityutils
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from pydantic import ValidationError
from jose import jwt


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl=f"api/auth/login",
    scheme_name="JWT"
)



async def userbyid(customerid: int):
    collections = await get_collections()
    item = await collections["customers"].find_one({"customer_id": customerid})
    if item:
        return Customer(**item)
    raise HTTPException(status_code=404, detail="Item not found")


async def userbyusername(username: str):
    collections = await get_collections()
    item = await collections["customers"].find_one({"username": username})
    if item:
        return Customer(**item)
    raise HTTPException(status_code=404, detail="Item not found")



async def get_current_user(token: str = Depends(reuseable_oauth)) -> Customer:
    try:
        payload = jwt.decode(
            token, securityutils.JWT_SECRET_KEY, algorithms=[securityutils.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        token_exp_naive_utc = token_data.exp.replace(tzinfo=None)
        current_time_naive_utc = datetime.utcnow()
        
        if token_exp_naive_utc < current_time_naive_utc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await userbyid(token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return user

async def get_current_admin(token: str = Depends(reuseable_oauth)) -> Customer:
    user = await get_current_user(token)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user