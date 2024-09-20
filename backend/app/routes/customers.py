from fastapi import APIRouter, HTTPException, Request,Depends
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from typing import List,Optional,Any
import yfinance as yf
from app.models import Customer
from app.routes.schemas import CustomerRequenst,CustomerResponse,UserAuth,TokenSchema
from fastapi import APIRouter, HTTPException
from ..database.mongo import get_collections
from bson import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import APIRouter, HTTPException, status
from app.utils import authutils
from fastapi import APIRouter, HTTPException, Request,Depends


router = APIRouter()
    
    
    
@router.get("/admin", response_model=list[CustomerResponse])
async def get_customers(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    customers = await collections["customers"].find(
    
    ).to_list(length=100)
    return [CustomerResponse(**customer) for customer in customers]


@router.get("/admin/{customerid}", response_model=Customer)
async def read_customer_byid(customerid: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    item = await collections["customers"].find_one({"customer_id": customerid})
    if item:
        return Customer(**item)
    raise HTTPException(status_code=404, detail="Item not found")



@router.get("/admin/{username}", response_model=Customer)
async def read_customer_byusername(username: str,user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    item = await collections["customers"].find_one({"username": username})
    if item:
        return Customer(**item)
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/admin/{customerid}", response_model=Customer)
async def update_customer(customerid: int, update_data: CustomerRequenst, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    
    existing_customer = await collections["customers"].find_one({"customer_id": customerid})
    if not existing_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_dict = update_data.dict(exclude={"hashed_password"})
    update_dict['hashed_password'] = existing_customer.get('hashed_password')
    updated_customer = await collections["customers"].find_one_and_update(
        {"customer_id": customerid},
        {"$set": update_dict},
        return_document=ReturnDocument.AFTER
    )

    if updated_customer:
        return Customer(**updated_customer)
    else:
        raise HTTPException(status_code=404, detail="Customer update failed")
    

# @router.delete("/admin/{customerid}", response_model=dict)
# async def delete_customer(customerid: int ,user: Customer = Depends(authutils.get_current_admin)):
#     collections = await get_collections()
#     delete_result = await collections["customers"].delete_one({"customer_id": customerid})

#     if delete_result.deleted_count == 1:
#         return {"message": "Stock deleted successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Stock not found")

from pydantic import BaseModel
from typing import List


class CustomerDeleteRequest(BaseModel):
    customer_ids: List[int]

@router.delete("/admin", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_customers(delete_request: CustomerDeleteRequest, user: Customer = Depends(authutils.get_current_admin)):
    customer_ids = delete_request.customer_ids
    collections = await get_collections()
    
    delete_result = await collections["customers"].delete_many({"customer_id": {"$in": customer_ids}})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No customers found to delete")
    
    return {"message": f"{delete_result.deleted_count} customers deleted successfully"}