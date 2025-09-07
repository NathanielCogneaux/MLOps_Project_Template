from airflow import DAG
from smart_pricing_dag_common import create_smart_pricing_tasks
from smart_pricing_dag_utils import default_args

dag = DAG(
    "smart_pricing_dag_B",
    default_args=default_args,
    description="Daily Smart Pricing DAG for scrap_type B",
    schedule_interval="30 0 * * *",  # 00:30 daily
    max_active_runs=1,
    catchup=False,
)

create_smart_pricing_tasks(dag, scrap_type="B")
