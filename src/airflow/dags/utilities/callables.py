"""Python callable definitions."""
import logging
import pandas as pd
from datetime import datetime
import requests
from pathlib import Path

from sqlalchemy import create_engine
import psycopg2 
import io

# todo: make env vars

DATA_URL = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
IMPORT_FILE_PATH = f'/bitnami'
RAW_DATA_DIR = f'{IMPORT_FILE_PATH}/raw/'

def extract_data(**context):
    response = requests.get(url=DATA_URL, stream=True)
    if not response.status_code == 200:
        response.raise_for_status()

    p = Path(RAW_DATA_DIR)
    p.mkdir(exist_ok=True)
    dump_file = (p / f"{int(datetime.now().timestamp())}.csv")
    with dump_file.open('w') as fp:
        # prevent entire contents being loaded into memory 
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            fp.write(chunk)

    # TODO: serialize as pickled df

def load_data(**context):
    table_name = 'github_vax_data'
    pathlist = Path(RAW_DATA_DIR).rglob('*.csv')
    for path in pathlist:
        df = pd.read_csv(str(path))
        df.index.rename('id', inplace=True)
        engine = create_engine('postgresql+psycopg2://bn_airflow:bitnami1@vaccines_postgresql_1:5432/test')

        df.head(0).to_sql(table_name, engine, if_exists='replace') #drops old table and creates new empty table

        conn = engine.raw_connection()
        cur = conn.cursor()

        # convert df to csv and load it into memory
        output = io.StringIO()
        df.to_csv(output, sep='\t', header=False)
        output.seek(0)
        contents = output.getvalue()
        cur.copy_from(output, table_name, null="") # null values become ''
        conn.commit()
