from pydantic import BaseModel
from typing import Optional

class PaymentsFactResponse(BaseModel):
    id: int
    school_id: int
    semester_id: int
    currency_code: str
    total_amount: float
    status: int
    fee_amount: Optional[float]
    claim_amount: Optional[float]
    gift_amount: Optional[float]
    payment_type_id: int
    user_id: int
    payment_order_id: Optional[int]
    created: str

class UserDimResponse(BaseModel):
    user_id: int
    payment_user_id: int
    payment_email: str
    created: str

class InvoiceDimResponse(BaseModel):
    id: int
    type: str
    entity_id: str
    amount: float