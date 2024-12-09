from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from clickhouse_driver import Client
from response_model import PaymentsFactResponse, UserDimResponse, InvoiceDimResponse
app = FastAPI()

# Initialize ClickHouse client
client = Client(host='clickhouse', port=9000, user='default', password='default')


# Endpoints for payments_fact
@app.get("/payments_fact", response_model=List[PaymentsFactResponse])
def get_all_payments_fact():
    query = "SELECT * FROM payments_fact"
    result = client.execute(query)

    columns = [desc[0] for desc in client.execute('DESCRIBE TABLE payments_fact')]

    return [PaymentsFactResponse(**dict(zip(columns, row))) for row in result]

@app.get("/payments_fact/{id}", response_model=List[PaymentsFactResponse])
def get_payment_fact_by_id(id: int):
    query = """
        SELECT *
        FROM payments_fact 
        WHERE id = %(id)s
    """
    # Execute the query with the parameters
    result = client.execute(query, {'id': id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    # Get column names from the result's metadata
    columns = [desc[0] for desc in client.execute('DESCRIBE TABLE payments_fact')]
    
    # Map the result row to the response model using the columns
    return [PaymentsFactResponse(**dict(zip(columns, row))) for row in result]


# Endpoints for user_dim
@app.get("/user_dim", response_model=List[UserDimResponse])
def get_all_user_dim():
    query = "SELECT * FROM user_dim"
    result = client.execute(query)

    columns = [desc[0] for desc in client.execute('DESCRIBE TABLE user_dim')]

    return [UserDimResponse(**dict(zip(columns, row))) for row in result]

@app.get("/user_dim/{user_id}", response_model=List[UserDimResponse])
def get_user_dim_by_id(user_id: int):
    query = """
        SELECT *
        FROM user_dim 
        WHERE user_id = %(user_id)s
    """
    # Execute the query with the parameters
    result = client.execute(query, {'user_id': user_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="user not found")
    
    # Get column names from the result's metadata
    columns = [desc[0] for desc in client.execute('DESCRIBE TABLE user_dim')]
    
    # Map the result row to the response model using the columns
    return [UserDimResponse(**dict(zip(columns, row))) for row in result]


@app.get("/invoice_dim", response_model=List[InvoiceDimResponse])
def get_all_invoices():
    query = "SELECT * FROM invoice_dim"
    result = client.execute(query)

    # Get column names from the result's metadata
    columns = [desc[0] for desc in client.execute('DESCRIBE TABLE invoice_dim')]

    # Map the result rows to the response model using the columns
    return [InvoiceDimResponse(**dict(zip(columns, row))) for row in result]

@app.get("/invoice_dim/{id}", response_model=List[InvoiceDimResponse])
def get_invoice_by_id_and_type(id: int):
    query = """
        SELECT *
        FROM invoice_dim 
        WHERE id = %(id)s
    """
    # Execute the query with the parameters
    result = client.execute(query, {'id': id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Get column names from the result's metadata
    columns = [desc[0] for desc in client.execute('DESCRIBE TABLE invoice_dim')]
    
    # Map the result row to the response model using the columns
    return [InvoiceDimResponse(**dict(zip(columns, row))) for row in result]