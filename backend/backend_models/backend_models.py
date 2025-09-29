from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from bson import ObjectId


 
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        json_schema = handler(schema)
        json_schema.update(type="string")
        return json_schema

class BaseModelConfig:
    validate_by_name = True  # Updated from 'allow_population_by_field_name' for Pydantic v2 compatibility
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}
    
class Transaction(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    description: str
    amount: float
    category: str
    type: str

    class Config(BaseModelConfig):
        pass


 

class LiabilityType(str, Enum):
    loan = "loan"
    credit_card = "credit_card"
    mortgage = "mortgage"
    other = "other"

class Liabilities(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    type: LiabilityType
    balance: float
    interestRate: float
    monthlyPayment: float
    currency: str

    class Config(BaseModelConfig):
        pass

 

class Investment(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    type: str
    currentValue: float
    purchaseValue: float
    quantity: float
    currency: str

    class Config(BaseModelConfig):
        pass

 

class EpfBalance(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    totalBalance: float
    employeeContributions: float
    employerContributions: float
    currency: str

    class Config(BaseModelConfig):
        pass


 

class CreditScore(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    score: float
    rating: str
    factors: List[str]

    class Config(BaseModelConfig):
        pass

 
class Asset(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    type: Optional[str] = None
    value: float
    currency: str

    class Config(BaseModelConfig):
        pass


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    clerkUserId: str  # from Clerk
    email: str
    name: Optional[str] = None
    
    # References (store as lists of ObjectId)
    transactions: List[PyObjectId] = []
    liabilities: List[PyObjectId] = []
    investments: List[PyObjectId] = []
    epf_balances: List[PyObjectId] = []
    credit_scores: List[PyObjectId] = []
    assets: List[PyObjectId] = []
    conversations: List[PyObjectId] = []

    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config(BaseModelConfig):
        pass



class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class Conversation(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    userId: str  # reference Clerk's userId
    messages: List[Message]
    startedAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config(BaseModelConfig):
        pass