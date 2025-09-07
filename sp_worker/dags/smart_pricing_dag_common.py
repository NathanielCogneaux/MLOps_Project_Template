from airflow.operators.python import PythonOperator


def create_smart_pricing_tasks(dag, scrap_type: str):
    """
    Creates four tasks for smart pricing pipeline and sets dependencies:
    raw_data_updater -> data_cleaner -> sub_charts_updater -> baseline_model_updater
    """
    from src.data_ingestion.ingestion_pipeline import data_cleaner, raw_data_updater
    from src.data_analytics.sub_charts_pipeline import sub_charts_updater
    from src.ml.baseline.baseline_pipeline import baseline_model_updater
    from src.ml.optimized_baseline.opt_baseline_pipeline import (
        opt_baseline_model_updater,
    )

    task_raw_updater = PythonOperator(
        task_id=f"raw_data_updater_{scrap_type}",
        python_callable=raw_data_updater,
        op_args=[scrap_type],
        dag=dag,
    )

    task_cleaner = PythonOperator(
        task_id=f"data_cleaner_{scrap_type}",
        python_callable=data_cleaner,
        op_args=[scrap_type],
        dag=dag,
    )

    task_sub_charts = PythonOperator(
        task_id=f"sub_charts_updater_{scrap_type}",
        python_callable=sub_charts_updater,
        op_args=[scrap_type],
        dag=dag,
    )

    task_baseline = PythonOperator(
        task_id=f"baseline_model_updater_{scrap_type}",
        python_callable=baseline_model_updater,
        op_args=[scrap_type],
        dag=dag,
    )

    task_opt_baseline = PythonOperator(
        task_id=f"Optimized_baseline_model_updater_{scrap_type}",
        python_callable=opt_baseline_model_updater,
        op_args=[scrap_type],
        dag=dag,
    )

    # Set dependencies
    (
        task_raw_updater
        >> task_cleaner
        >> task_sub_charts
        >> task_baseline
        >> task_opt_baseline
    )

    return task_opt_baseline  # optional: return last task for triggers
