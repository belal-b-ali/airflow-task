from clickhouse_connect import get_client
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, FloatType, IntegerType

class Config:
    clickhouse_client = get_client(host='clickhouse', port=8123, username='default', password='default')

    spark = SparkSession.builder \
        .appName("Airflow PySpark Example") \
        .master("local[*]") \
        .config("spark.ui.port", "4050") \
        .getOrCreate()
    
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
    }

    data_schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("total_amount", FloatType(), True),
        StructField("status", IntegerType(), True),
        StructField("invoices", StringType(), True),
        StructField("types", StringType(), True),
        StructField("meta_data", StringType(), True),
        StructField("types_status", StringType(), True),
        StructField("payment_type_id", IntegerType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("payment_user_id", IntegerType(), True),
        StructField("payment_email", StringType(), True),
        StructField("school_id", IntegerType(), True),
        StructField("semester_id", IntegerType(), True),
        StructField("payment_order_id", IntegerType(), True),
        StructField("currency_code", StringType(), True),
        StructField("created", StringType(), True)
    ])

    invoices_schema = StructType([
        StructField("claims", ArrayType(StructType([
            StructField("claim_id", StringType(), True),
            StructField("amount", StringType(), True)
        ])), True),
        StructField("fees_payments", ArrayType(StructType([
            StructField("fee_id", StringType(), True),
            StructField("amount", StringType(), True)
        ])), True),
        StructField("gifts", StructType([
            StructField("gift_id", StringType(), True),
            StructField("amount", StringType(), True)
        ]), True)
    ])

    column_map = {
        "payments_fact": ["id", "total_amount", "status", "fee_amount", "claim_amount", "gift_amount", "payment_type_id", "user_id", "payment_order_id", "school_id", "semester_id", "currency_code", "created"],
        "user_dim": ["user_id", "payment_user_id", "payment_email", "created"],
        "time_dim": ["day", "month", "year", "quarter", "created"],
        "invoice_dim": ["id", "type", "entity_id", "amount"]
    }
