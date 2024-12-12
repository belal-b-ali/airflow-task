from datetime import datetime
import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup


from pyspark.sql.functions import col, explode, from_json, to_date, year, month, quarter, lit
from pyspark.sql.functions import col, explode
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import FloatType

from config import Config

os.environ["SPARK_HOME"] = "/opt/spark"
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-arm64"
os.environ["PYSPARK_PYTHON"] = "/usr/local/bin/python3"

_tables = ["payments_fact", "user_dim", "time_dim", "invoice_dim"]

def _invoice_transformation(df):
    exploded_invoices = df.withColumn("invoices", from_json(col("invoices"), Config.invoices_schema))

    fees_df = exploded_invoices.select(
        col("id").alias("fee_id"),
        explode(col("invoices.fees_payments")).alias("fee_payment")
    ).select(
        col("fee_id"),
        col("fee_payment.fee_id").alias("fee_detail_id"),
        col("fee_payment.amount").cast(FloatType()).alias("fee_amount")
    )

    claims_df = exploded_invoices.select(
        col("id").alias("claim_id"),
        explode(col("invoices.claims")).alias("claim_detail")
    ).select(
        col("claim_id"),
        col("claim_detail.claim_id").alias("claim_detail_id"),
        col("claim_detail.amount").cast(FloatType()).alias("claim_amount")
    )

    gifts_df = exploded_invoices.select(
        col("id").alias("gift_id"),
        col("invoices.gifts.amount").cast(FloatType()).alias("gift_amount")
    )

    invoice_df = exploded_invoices \
        .join(fees_df, exploded_invoices.id == fees_df.fee_id, how="left") \
        .join(claims_df, exploded_invoices.id == claims_df.claim_id, how="left") \
        .join(gifts_df, exploded_invoices.id == gifts_df.gift_id, how="left")

    return invoice_df
def read_json_file(**kwargs):
    df = Config.spark.read.option("multiline", True).json('/opt/airflow/invoices_logs.json')

    json_data = [row.asDict() for row in df.collect()]

    kwargs['ti'].xcom_push(key='json_data', value=json_data)

def data_transformation(**kwargs):
    ti = kwargs['ti']
    json_data = ti.xcom_pull(task_ids='read_task', key='json_data')
    df = Config.spark.createDataFrame(json_data, Config.data_schema)

    invoices_df = _invoice_transformation(df)

    fee_payment_df = invoices_df.select(
        "id",
        lit("fee_payment").alias("type"),
        invoices_df["fee_detail_id"].alias("entity_id"),
        invoices_df["fee_amount"].alias("amount")
    ).where("fee_detail_id IS NOT NULL AND fee_amount IS NOT NULL")

    # Process claim entries
    claim_df = invoices_df.select(
        "id",
        lit("claim").alias("type"),
        invoices_df["claim_detail_id"].alias("entity_id"),
        invoices_df["claim_amount"].alias("amount")
    ).where("claim_detail_id IS NOT NULL AND claim_amount IS NOT NULL")

    # Process gift entries
    gift_df = invoices_df.select(
        "id",
        lit("gift").alias("type"),
        invoices_df["gift_id"].alias("entity_id"),
        invoices_df["gift_amount"].alias("amount")
    ).where("gift_id IS NOT NULL AND gift_amount IS NOT NULL")

    # Combine all entries into a single DataFrame
    invoice_dim = fee_payment_df.union(claim_df).union(gift_df).distinct()

    payments_fact = invoices_df.select(
        col("id"),
        col("total_amount"),
        col("status"),
        col("fee_amount"),
        col("claim_amount"),
        col("gift_amount"),
        col("payment_type_id"),
        col("user_id"),
        col("payment_order_id"),
        col("school_id"),
        col("semester_id"),
        col("currency_code"),
        col("created")
    )

    user_dim = df.select(
        col("user_id"),
        col("payment_user_id"),
        col("payment_email"),
        col("created")
    )

    time_dim = df.select(
        to_date(col("created")).alias("day"),
        month(col("created")).alias("month"),
        year(col("created")).alias("year"),
        quarter(col("created")).alias("quarter"),
        col("created")
    )

    for name, table in [
        ("payments_fact", payments_fact),
        ("user_dim", user_dim),
        ("time_dim", time_dim),
        ("invoice_dim", invoice_dim)
    ]:

        ti.xcom_push(key=name, value=[tuple(row) for row in table.collect()])

    kwargs['ti'].xcom_push(key='transformed_data', value=json_data)

def load_data_to_clickhouse(table_name, **kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform_task', key=table_name)

    if data:
        Config.clickhouse_client.insert(table_name, data, column_names=Config.column_map[table_name])

with DAG(
    'json_read_transform_and_load',
    default_args=Config.default_args,
    description='A DAG to read, transform, and load JSON data',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    read_task = PythonOperator(
        task_id='read_task',
        python_callable=read_json_file,
        provide_context=True
    )

    transform_task = PythonOperator(
        task_id='transform_task',
        python_callable=data_transformation,
        provide_context=True
    )

    with TaskGroup("load_tasks_group") as load_tasks_group:
        for table in _tables:
            PythonOperator(
                task_id=f'load_{table}_task',
                python_callable=load_data_to_clickhouse,
                op_kwargs={'table_name': table},
                provide_context=True
            )

    read_task >> transform_task >> load_tasks_group
