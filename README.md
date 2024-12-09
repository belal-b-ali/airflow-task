This project implements a complete ETL pipeline for reading, transforming, and loading JSON data into a ClickHouse database using Airflow and PySpark. It also includes a FastAPI service for querying and retrieving the processed data via RESTful APIs.

---

## 1. Project Components

### 1.1 Airflow Pipeline

- **Read Task**: Reads a JSON file and extracts data into a Spark DataFrame.
- **Transform Task**: Processes and validates data using PySpark, producing structured tables.
- **Load Task**: Inserts the processed data into ClickHouse tables.

### 1.2 ClickHouse Database

Stores the transformed data in the following tables:

- **`payments_fact`**: Fact table for payment records.
- **`user_dim`**: Dimension table for user data.
- **`time_dim`**: Dimension table for time-related information.
- **`invoice_dim`**: Dimension table for invoice details.

### 1.3 FastAPI Service

Provides endpoints to query the ClickHouse tables:

- **GET `/payments_fact`**: Retrieve all payment records.
- **GET `/payments_fact/{id}`**: Retrieve a specific payment by ID.
- **GET `/user_dim`**: Retrieve all user records.
- **GET `/user_dim/{user_id}`**: Retrieve a specific user by user ID.
- **GET `/invoice_dim`**: Retrieve all invoice records.
- **GET `/invoice_dim/{id}`**: Retrieve a specific invoice by ID.

---

## 2. Project Structure

```
├── dags/ 
    ├── dag.py # Airflow DAG definition
    ├── config.py # Configuration and schema definitions
├── fastapi/
    ├── main.py # FastAPI application
    ├── response_model.py # FastAPI response models
├── clickhouse-init/  
    ├── init.sql # ClickHouse table initialization script
├── Dockerfile # Dockerfile for Airflow servicess
├── Dockerfile.fastapi # Dockerfile for FastAPI service
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt # Dependencies for Airflow services
├── requirements.fastapi.txt # Dependencies for FastAPI service
```

## 3. Setting Up and Running the Project

### 3.1 Prerequisites

- Docker and Docker Compose installed on your machine.

### 3.2 Steps to Run

1. Clone the repository:

   ```bash
   git clone https://github.com/belal-b-ali/airflow-task
   cd project

2. Build and start the services:

    docker-compose up airflow-init webserver scheduler clickhouse fastapi --build

3. Access the following services:

    Airflow Webserver: http://localhost:8080
    FastAPI Docs: http://localhost:8000/docs

4. Key Configurations and Code

    4.1 Airflow DAG (dag.py)
        Defines the ETL pipeline for processing JSON data:
        Tasks:
            read_data: Reads JSON and pushes raw data to XCom.
            transform_data: Transforms the JSON into structured data.
            load_data: Inserts structured data into ClickHouse.

        from airflow import DAG
        from airflow.operators.python import PythonOperator
        from config import get_spark_session, process_data
        from datetime import datetime

        default_args = {"start_date": datetime(2023, 12, 1)}

        with DAG("json_etl", default_args=default_args, schedule_interval=None) as dag:
            def read_json():
                # Logic to read JSON data and push to XCom
                pass

            def transform_data(ti):
                # Logic to transform JSON data using Spark
                pass

            def load_data():
                # Logic to load transformed data into ClickHouse
                pass

            read_task = PythonOperator(task_id="read_data", python_callable=read_json)
            transform_task = PythonOperator(task_id="transform_data", python_callable=transform_data)
            load_task = PythonOperator(task_id="load_data", python_callable=load_data)

            read_task >> transform_task >> load_task

    4.2 ClickHouse Initialization (init.sql)
        Defines the database schema for storing transformed data:

        ```sql
        CREATE TABLE payments_fact (
            id UInt64,
            school_id UInt64,
            semester_id UInt64,
            currency_code String,
            total_amount Float64,
            status UInt8,
            fee_amount Nullable(Float64),
            claim_amount Nullable(Float64),
            gift_amount Nullable(Float64),
            payment_type_id UInt64,
            user_id UInt64,
            payment_order_id Nullable(UInt64),
            created String
        ) ENGINE = MergeTree() ORDER BY id;
        
        CREATE TABLE user_dim (
            user_id UInt64,
            payment_user_id UInt64,
            payment_email String,
            created String
        ) ENGINE = MergeTree()
        ORDER BY (user_id);

        CREATE TABLE time_dim (
            day Date,
            month UInt8,
            year UInt16,
            quarter UInt8,
            created String
        ) ENGINE = MergeTree()
        ORDER BY (year);

        CREATE TABLE invoice_dim (
            id UInt64, 
            type String,
            entity_id String,
            amount Float64
        ) ENGINE = MergeTree()
        ORDER BY (id, type);

        ```

    4.3 FastAPI Application (main.py)
        Provides endpoints for querying the database:
        ```python
        from fastapi import FastAPI
        from clickhouse_driver import Client
        from response_model import PaymentsFactResponse

        app = FastAPI()
        client = Client(host="clickhouse")

        @app.get("/payments_fact", response_model=list[PaymentsFactResponse])
        def get_payments_fact():
            query = "SELECT * FROM payments_fact"
            result = client.execute(query)
            return [PaymentsFactResponse(**dict(zip(["id", "school_id", ...], row))) for row in result]

5. Dependencies
    5.1 Airflow Requirements (requirements.txt)
        ```
        apache-airflow==2.6.3
        pyspark
        clickhouse-driver```
    5.2 FastAPI Requirements (requirements.fastapi.txt)
        ```f
        astapi
        uvicorn
        clickhouse-driver```

6. API Documentation

    | API Name       | Endpoint              | Method | Description                   |
    |----------------|-----------------------|--------|-------------------------------|
    | Payments API   | `/payments_fact`      | GET    | Fetch all payment records.    |
    | User API       | `/user_dim`           | GET    | Fetch all user records.       |
    | Invoices API   | `/invoice_dim`        | GET    | Fetch all invoice records.    |
    | Payment by ID  | `/payments_fact/{id}` | GET    | Fetch a payment by its ID.    |
    | User by ID     | `/user_dim/{user_id}` | GET    | Fetch a user by their ID.     |
    | Invoice by ID  | `/invoice_dim/{id}`   | GET    | Fetch an invoice by its ID.   |
