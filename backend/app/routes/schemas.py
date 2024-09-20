from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, Field, validator
from pydantic import BaseModel, Field , conint
from typing import Optional
from bson import ObjectId
from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime



class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr  
    password: constr(min_length=8) 

    
    otp_enabled: bool = False
    otp_verified: bool = False
    otp_base32: str | None = None
    otp_auth_url: str | None = None

    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  


class UserRequestSchema(BaseModel):
    user_id: str
    token: str | None = None





#---------------------------------------------------------------------------------------------------------------------
class UserLoginSchema(BaseModel):
    username: str
    password: str

class CreateStockRequest(BaseModel):
    Company_name: str
    Company_ticker: str
    Closed_price: float
    Company_info: str
    Company_PE: Optional[float] = Field(None, description="Price to Earnings Ratio")
    Company_cash_flow: Optional[float] = Field(None, description="Operating Cash Flow")
    Company_dividend: Optional[float] = Field(None, description="Dividend Rate")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda o: str(o)}
        populate_by_name  = True
        
        
class CustomerRequenst(BaseModel):
    username: str
    email: EmailStr
    hashed_password: Optional[str] = None
    balance: Optional[float] = Field(None, description="Account Balance")
    role: str = Field(default="customer", description="The role of the user") 
    net_stock: float = Field(default=0.0, description="Stock worth")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda o: str(o)}
        populate_by_name  = True
        
class CreateCryptoRequest(BaseModel):
    Name: str
    Symbol: str
    Last_Close: float
    Market_Cap: Optional[float] = Field(None, description="Market Capitalization")
    Volume_24h: Optional[float] = Field(None, description="24 Hour Trading Volume")
    Circulating_Supply: Optional[float] = Field(None, description="Circulating Supply")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda o: str(o)}
        populate_by_name = True
        
class CustomerResponse(BaseModel):
    customer_id: int
    username: str
    email: EmailStr
    balance: float
    net_stock:  Optional[float] = Field(None, description="stock Balance")
    role: str = Field(default="customer", description="The role of the user") 
    
    
class TransactionRequest(BaseModel):
    # transaction_id: conint(ge=0, le=999999)
    # customer_id: conint(ge=0, le=999999)
    stock_id: Optional[conint(ge=0, le=999999)]
    crypto_id: Optional[conint(ge=0, le=999999)] 
    agent_id: conint(ge=0, le=999999)
    ticket: str
    volume: int
    each_cost:float
    action: str  # constrains the string to either 'buy' or 'sell'
    
    @validator('action')
    def check_action(cls, v):
        if v not in ['buy', 'sell']:
            raise ValueError('Action must be "buy" or "sell"')
        return v

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda o: str(o)}
        schema_extra = {
            "example": {
                "customer_id": "1",
                "stock_id": "1",
                "agent_id": "1",
                "ticket": "GOOGL",
                "volume": 100,
                "action": "buy",
                "date": "2024-03-26T12:00:00Z"
            }
        }
class TransactionAdminRequest(BaseModel):
    # transaction_id: conint(ge=0, le=999999)
    customer_id: conint(ge=0, le=999999)
    stock_id: conint(ge=0, le=999999)
    agent_id: conint(ge=0, le=999999)
    ticket: str
    volume: int
    each_cost:float
    action: str  # constrains the string to either 'buy' or 'sell'
    
    @validator('action')
    def check_action(cls, v):
        if v not in ['buy', 'sell']:
            raise ValueError('Action must be "buy" or "sell"')
        return v

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda o: str(o)}
        schema_extra = {
            "example": {
                "customer_id": "1",
                "stock_id": "1",
                "agent_id": "1",
                "ticket": "GOOGL",
                "volume": 100,
                "action": "buy",
                "date": "2024-03-26T12:00:00Z"
            }
        }


from uuid import UUID
from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    
    
class Cstock(BaseModel):  
    stock_ticket: str
    each_cost: float
    volume: int
    
    
class TokenPayload(BaseModel):
    sub: int = None
    exp: datetime = None
    role: str
    
    
class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")
    
class Transactionpro(BaseModel):
    transaction_id: conint(ge=0, le=999999)
    customer_id: conint(ge=0, le=999999)
    stock_id: conint(ge=0, le=999999)
    agent_id: conint(ge=0, le=999999)
    ticket: str
    volume: int
    each_cost: float
    action: str  # Constrained to 'buy' or 'sell'
    date: datetime = Field(default_factory=datetime.now)
    customer_name: Optional[str] = None
    agent_name: Optional[str] = None

    @validator('action')
    def check_action(cls, v):
        if v not in ['buy', 'sell']:
            raise ValueError('Action must be "buy" or "sell"')
        return v


class CustomerInfo(BaseModel):
    customer_id: int
    username: str
    email: str
    total_cost: float
    agent_name: str
    agent_level: str
    
class AgentInfo(BaseModel):
    agent_id: int
    agent_name: str
    agent_level: str
    total_cost: float
    
class CustomerTransactionInfo(BaseModel):
    customer_id: int
    username: str
    email: str
    total_transactions: int
    agent_name: str
    agent_level: str