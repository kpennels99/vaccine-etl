"""OWID vaccine data ETL DAG."""
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from utilities import callables
from utilities.environment_adapter import EnvironmentAdapter


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
    
    environment = EnvironmentAdapter()
    execution_time = '{{ ts }}'
    
    extract_data = PythonOperator(
        task_id='extract_raw_github_data',
        python_callable=callables.extract_data,
        op_kwargs={"data_url": environment.data_url,
                   "exec_time": execution_time},
        dag=dag
    )
    
    transformations = [
        {
            'name': 'FillEmptyCountsTransformer',
            'filter_column': "location",
            'count_columns': ["total_vaccinations", "people_vaccinated", 
                              "people_fully_vaccinated", "total_boosters",
                              "daily_vaccinations_raw", "daily_vaccinations",
                              "total_vaccinations_per_hundred", "people_vaccinated_per_hundred",
                              "people_fully_vaccinated_per_hundred", "total_boosters_per_hundred",
                              "daily_vaccinations_per_million"]
        },
        {
            'name': 'AddExternalColumnTransformer',
            'match_column_mapping': {"iso_code": "alpha-3"},
            "external_columns": ["region", "sub-region", "intermediate-region"]
        },
        {
            'name': 'RenameTransformer',
            # make column names python identifier compliant to allow django orm mapping
            'mapping': {"sub-region": "sub_region",
                        "intermediate-region": "intermediate_region"}
        }
    ]

    transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=callables.transform_data,
        op_kwargs={
            "transformations": transformations,
            "exec_time": execution_time
        },
        dag=dag
    )

    db_driver = 'postgresql+psycopg2'
    load_github_data = PythonOperator(
        task_id='load_data',
        python_callable=callables.load_data,
        op_kwargs={'db_connection': environment.destination_db_connection(db_driver),
                   'destination_table': environment.destination_db_table,
                   "exec_time": execution_time},
        dag=dag
    )

    extract_data >> transform_data >> load_github_data
