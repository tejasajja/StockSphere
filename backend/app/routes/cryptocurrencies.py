from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from typing import List
import yfinance as yf
from app.models import Crypto, Customer
from app.routes.schemas import CreateCryptoRequest
from fastapi import APIRouter, HTTPException
from app.database.mongo import get_collections
from bson import ObjectId
from pymongo.collection import ReturnDocument
from app.utils import authutils
from fastapi import APIRouter, Request, Depends




router = APIRouter()



@router.get("/", response_model=List[Crypto])
async def get_cryptos(user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    cryptos = await collections["cryptocurrencies"].find().to_list(length=100)
    return cryptos



@router.post("/", response_model=Crypto)
async def create_crypto(crypto: CreateCryptoRequest, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    max_id_doc = await collections["cryptocurrencies"].find_one(sort=[("crypto_id", -1)])
    max_id = max_id_doc['crypto_id'] + 1 if max_id_doc and 'crypto_id' in max_id_doc else 1

    crypto_data = crypto.dict(by_alias=True)
    crypto_data["crypto_id"] = max_id

    result = await collections["cryptocurrencies"].insert_one(crypto_data)
    created_crypto = await collections["cryptocurrencies"].find_one({"_id": result.inserted_id})
    return created_crypto



@router.get("/{cryptoid}", response_model=Crypto)
async def read_crypto_byid(cryptoid: int, user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    item = await collections["cryptocurrencies"].find_one({"crypto_id": cryptoid})
    if item:
        return Crypto(**item)
    raise HTTPException(status_code=404, detail="Item not found")



@router.post("/{ytic}", response_model=Crypto)
async def create_crypto_by_ticker(ytic: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    existing_crypto = await collections["cryptocurrencies"].find_one({'Symbol': ytic})
    if existing_crypto:
        return Crypto(**existing_crypto)

    try:
        comp = yf.Ticker(ytic)
        if "name" not in comp.info:
            raise HTTPException(status_code=404, detail="Yahoo Finance ticker not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    crypto_data = CreateCryptoRequest(
        Name=comp.info['name'],
        Symbol=comp.info['symbol'],
        Last_Close=comp.info['previousClose'],
        Market_Cap=comp.info.get('marketCap'),
        Volume_24h=comp.info.get('volume24Hr'),
        Circulating_Supply=comp.info.get('circulatingSupply')
    )
    result = await create_crypto(crypto=crypto_data)
    created_crypto = Crypto(**crypto_data.dict(), id=result.inserted_id)
    return created_crypto



@router.put("/{cryptoid}", response_model=Crypto)
async def update_crypto(cryptoid: int, update_data: CreateCryptoRequest, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    updated_crypto = await collections["cryptocurrencies"].find_one_and_update(
        {"crypto_id": cryptoid},
        {"$set": update_data.dict(by_alias=True)},
        return_document=ReturnDocument.AFTER
    )

    if updated_crypto:
        return Crypto(**updated_crypto)
    else:
        raise HTTPException(status_code=404, detail="Crypto not found")



@router.put("/{ytic}", response_model=Crypto)
async def update_crypto_by_ticker(ytic: str, update_data: CreateCryptoRequest, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    updated_crypto = await collections["cryptocurrencies"].find_one_and_update(
        {"Symbol": ytic},
        {"$set": update_data.dict(by_alias=True)},
        return_document=ReturnDocument.AFTER
    )

    if updated_crypto:
        return Crypto(**updated_crypto)
    else:
        raise HTTPException(status_code=404, detail="Crypto with given ticker not found")

from pydantic import BaseModel
class cryptoDeleteRequest(BaseModel):
    crypto_ids: List[int]
    
    

@router.delete("/admin", response_model=dict)
async def delete_crypto(delete_request: cryptoDeleteRequest ,user: Customer = Depends(authutils.get_current_admin)):
    crypto_ids = delete_request.crypto_ids
    collections = await get_collections()
    delete_result = await collections["cryptocurrencies"].delete_many({"crypto_id": {"$in": crypto_ids}})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No crypto found to delete")
    return {"message": f"{delete_result.deleted_count} crypto deleted successfully"}


# @router.delete("/admin", response_model=dict)
# async def delete_crypto(cryptoid: int, user: Customer = Depends(authutils.get_current_admin)):
#     collections = await get_collections()
#     delete_result = await collections["cryptocurrencies"].delete_one({"crypto_id": cryptoid})

#     if delete_result.deleted_count == 1:
#         return {"message": "Crypto deleted successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Crypto not found")



@router.delete("/{ytic}", response_model=dict)
async def delete_crypto_by_ticker(ytic: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    delete_result = await collections["cryptocurrencies"].delete_one({"Symbol": ytic})

    if delete_result.deleted_count == 1:
        return {"message": "Crypto with ticker '{}' deleted successfully".format(ytic)}
    else:
        raise HTTPException(status_code=404, detail="Crypto with given ticker not found")
