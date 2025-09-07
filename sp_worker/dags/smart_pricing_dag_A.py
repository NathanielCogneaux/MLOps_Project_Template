from airflow import DAG
from smart_pricing_dag_common import create_smart_pricing_tasks
from smart_pricing_dag_utils import default_args

dag = DAG(
    "smart_pricing_dag_A",
    default_args=default_args,
    description="Hourly Smart Pricing DAG for scrap_type A",
    schedule_interval="@hourly",
    max_active_runs=1,
    catchup=False,
)

create_smart_pricing_tasks(dag, scrap_type="A")
