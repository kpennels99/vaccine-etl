"""Bi direction transfer DAG."""
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from utilities import callables


args = {
    'owner': 'airflow',
}

# TODO: Dag to load previous load (corrupted data, wanna load a previous import)
with DAG(
    dag_id='github_vaccination_workflow',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(2)
) as dag:

    extract_data = PythonOperator(
        task_id='extract_raw_github_data',
        python_callable=callables.extract_data,
        op_kwargs={
        },
        dag=dag
    )

    # transform_data = PythonOperator(
    #     task_id='transform_data',
    #     python_callable=callables.transform_data,
    #     op_kwargs={
    #     },
    #     dag=dag
    # )

    load_github_data = PythonOperator(
        task_id='load_data',
        python_callable=callables.load_data,
        dag=dag
    )

   
    extract_data >> load_github_data
