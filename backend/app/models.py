from pydantic import BaseModel, Field , conint,constr,validator
from typing import Optional
from bson import ObjectId
from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(ObjectId(v))
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        
        

class Agent(BaseModel):
    agent_id: conint(ge=0, le=999999)
    # name: _get_object_size
    name : str  
    contact: str
    level: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda o: str(o)}
        
        
class Customer(BaseModel):
    customer_id: conint(ge=0, le=999999)
    username: str
    email: EmailStr
    hashed_password: str
    balance: Optional[float] = Field(None, description="Account Balance")
    net_stock:  float = Field(default=0.0, description="Stock worth")
    role: str = Field(default="customer", description="The role of the user") 
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        



class Stock(BaseModel):
    stock_id: conint(ge=0, le=999999)
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
        # orm_mode = True
        
        
class StockData(BaseModel):
    Open: float
    High: float
    Low: float
    Close: float
    Adj_Close: float = Field(..., alias='Adj Close')  # Alias for 'Adj Close'
    Volume: int
    Company_ticker: str
    Date:  str = Field(..., alias='date')  # Alias for 'date'



# class Transaction(BaseModel):
#     transaction_id: conint(ge=0, le=999999)
#     customer_id: conint(ge=0, le=999999)
#     stock_id: conint(ge=0, le=999999)
#     crypto_id: conint(ge=0, le=999999)
#     agent_id: conint(ge=0, le=999999)
#     ticket: str
#     volume: int
#     each_cost:float
#     crypto_id: Optional[int] = Field(None, description="The crypto ID if applicable")

#     action: str  # constrains the string to either 'buy' or 'sell'
#     date: datetime = Field(default_factory=datetime.now)
    

class Transaction(BaseModel):
    transaction_id: conint(ge=0, le=999999)
    customer_id: conint(ge=0, le=999999)
    stock_id: Optional[conint(ge=0, le=999999)]
    crypto_id: Optional[conint(ge=0, le=999999)] 
    agent_id: conint(ge=0, le=999999)
    ticket: str
    volume: int
    each_cost: float
    action: str  # constrains the string to either 'buy' or 'sell'
    date: datetime = Field(default_factory=datetime.now)
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


class Crypto(BaseModel):
    crypto_id: conint(ge=0, le=999999)
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
        # orm_mode = True if you're interfacing directly with ORMs

class CryptoData(BaseModel):
    Open: float
    High: float
    Low: float
    Close: float
    Adj_Close: float = Field(..., alias='Adj Close')  # Alias for 'Adj Close'
    Volume: int
    Symbol: str
    Date: str = Field(..., alias='date')  # Alias for 'date'


