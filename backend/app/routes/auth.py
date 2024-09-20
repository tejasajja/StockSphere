from fastapi import APIRouter, HTTPException, Request,Depends,Body
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from typing import List,Optional,Any
import yfinance as yf
from app.models import Customer
from app.routes.schemas import CustomerRequenst,CustomerResponse,UserAuth,TokenSchema,TokenPayload,UserLoginSchema
from fastapi import APIRouter, HTTPException
from ..database.mongo import get_collections
from bson import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from app.utils import securityutils , authutils
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from pydantic import ValidationError
from jose import jwt


router = APIRouter()
    
@router.post("/register", response_model=CustomerResponse)
async def create_customer(customer_request: CustomerRequenst):
    collections = await get_collections()

    existing_user = await collections["customers"].find_one({"email": customer_request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    max_id_doc = await collections["customers"].find_one(sort=[("customer_id", -1)])
    maxid = max_id_doc['customer_id'] + 1 if max_id_doc and 'customer_id' in max_id_doc else 1

    hashed_password = securityutils.get_hashed_password(customer_request.hashed_password)
    customer_data = customer_request.dict(by_alias=True)
    customer_data["customer_id"] = maxid
    customer_data["hashed_password"] = hashed_password 
    res = await collections["customers"].insert_one(customer_data)
    created_customer = await collections["customers"].find_one({"_id": res.inserted_id})
    return CustomerResponse(**{k: v for k, v in created_customer.items() if k != 'hashed_password'})



async def authenticate(username: str, password: str) -> Optional[CustomerResponse]:
    user = await authutils.userbyusername(username=username)
    if not user:
        return None
    if not securityutils.verify_password(password=password, hashed_pass=user.hashed_password):
        return None
    return user

async def get_form_data(request: Request) -> UserLoginSchema:
    if request.headers.get("Content-Type") == "application/json":
        try:
            return await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")
    else:
        form_data = await request.form()
        return UserLoginSchema(username=form_data.get('username'), password=form_data.get('password'))

async def get_login_data(request: Request) -> UserLoginSchema:
    try:
        body = await request.json()
        return UserLoginSchema(**body)
    except Exception:
       
        form = await request.form()
        return UserLoginSchema(username=form.get('username'), password=form.get('password'))


@router.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: UserLoginSchema = Depends(get_login_data)  ) -> Any:
    print(f"Form Data: {form_data}")
    user = await authenticate(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "access_token": securityutils.create_access_token(subject=user.customer_id, 
    role=user.role),
        "refresh_token": securityutils.create_refresh_token(subject=user.customer_id),
    }
    

@router.post('/test-token', summary="Test if the access token is valid", response_model=Customer)
async def test_token(user: Customer = Depends(authutils.get_current_user)):
    return user



@router.post('/refresh', summary="Refresh token", response_model=TokenSchema)
async def refresh_token(refresh_token: str = Body(...)):
    try:
        payload = jwt.decode(
            refresh_token, securityutils.JWT_REFRESH_SECRET_KEY, algorithms=[securityutils.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await authutils.userbyid(token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token for user",
        )
    return {
        "access_token": securityutils.create_access_token(user.customer_id),
        "refresh_token": securityutils.create_refresh_token(user.customer_id),
    }
    

@router.put("/updatecustomer", response_model=Customer)
async def update_customer(update_data: CustomerRequenst ,current_user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    updated_stock = await collections["customers"].find_one_and_update(
        {"customer_id": current_user.customer_id},
        {"$set": update_data.dict(by_alias=True)},
        return_document=ReturnDocument.AFTER
    )

    if updated_stock:
        return Customer(**updated_stock)
    else:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    
    
    
    
@router.delete("/deletecustomer", response_model=dict)
async def delete_customer(current_user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    delete_result = await collections["customers"].delete_one({"customer_id": current_user.customer_id})
    
    if delete_result.deleted_count == 1:
        return {"current_user": "customer deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="customer not found")