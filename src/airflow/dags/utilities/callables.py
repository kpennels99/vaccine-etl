"""Python callable definitions."""
import io
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
import requests
from sqlalchemy import create_engine

from utilities.transformation.factory import Transformer
from copy import deepcopy


# todo: make env vars

DATA_URL = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
IMPORT_FILE_PATH = f'/bitnami'
RAW_DATA_DIR = f'{IMPORT_FILE_PATH}/raw/'
TRANSFORM_DATA_DIR = f'{IMPORT_FILE_PATH}/transformed/'

from functools import wraps

def csv_to_df(data_path):
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pathlist = Path(data_path).rglob('*.csv')
            for path in pathlist:
                df = pd.read_csv(str(path))
                new_kwargs = kwargs.copy()
                new_kwargs["df"] = df
                func(*args, **new_kwargs)
                
        return wrapper
    return real_decorator


def extract_data(**context):
    response = requests.get(url=DATA_URL, stream=True)
    if not response.status_code == 200:
        response.raise_for_status()

    p = Path(RAW_DATA_DIR)
    p.mkdir(exist_ok=True)
    # dump_file = (p / f'{int(datetime.now().timestamp())}.csv')
    dump_file = (p / f'test.csv')
    with dump_file.open('w') as fp:
        # prevent entire contents being loaded into memory
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            fp.write(chunk)

    # TODO: serialize as pickled df

@csv_to_df(RAW_DATA_DIR)
def transform_data(**context):
    pipeline = Transformer.build_pipeline(transformations=context['transformations'] )
    df = context['df']
    df: pd.DataFrame = Transformer.run_pipeline(dataframe=df, pipeline=pipeline,meta_data=None)
    p = Path(TRANSFORM_DATA_DIR)
    p.mkdir(exist_ok=True)
    dump_file = (p / f'transformed_test.csv')
    df.to_csv(dump_file, index=False)
    
@csv_to_df(TRANSFORM_DATA_DIR)
def load_data(**context):
    df = context['df']
    print(df.head())
    df.index.rename('id', inplace=True)
    df.index += 1
    print(df.head())
    engine = create_engine('postgresql+psycopg2://bn_airflow:bitnami1@vaccine-etl_postgresql_1:5432/test')
    table_name = 'github_vax_data'
    df.head(0).to_sql(table_name, engine, if_exists='replace') #drops old table and creates new empty table

    conn = engine.raw_connection()
    cur = conn.cursor()

    # convert df to csv and load it into memory
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, table_name, null='') # null values become ''
    conn.commit()
