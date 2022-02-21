"""Python callable definitions."""
from cmath import log
import io
import logging
import os
import shutil
from pathlib import Path
from typing import Callable, Mapping, Any

import pandas as pd
import requests
from sqlalchemy import create_engine
from functools import wraps

from utilities.transformation.factory import Transformer
from utilities.environment_adapter import EnvironmentAdapter

environment = EnvironmentAdapter()
RAW_DATA_DIR = f'{environment.import_file_path}/raw/'
TRANSFORM_DATA_DIR = f'{environment.import_file_path}/transformed/'
ARCHIVE_DATA_DIR = f'{environment.import_file_path}/archive/'

def csv_to_df(data_path: str) -> Callable:
    """CSV to dataframe decorator.

    Args:
        data_path ([type]): Path to csv to read into dataframe.
    """
    def real_decorator(func: Callable) -> Callable:
        """Decorating method of callable argument.

        Args:
            func (Callable): Callable that is decorated.

        Returns:
            Callable: Wrapped func callable
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Read csv at data_path into pandas df and add it as keyword argument."""
            pathlist = Path(data_path).rglob('*.csv')
            path = max(pathlist, key=os.path.getctime)
            logging.info(f"Processing {path}")
            df = pd.read_csv(str(path))
            new_kwargs = kwargs.copy()
            new_kwargs["df"] = df
            func(*args, **new_kwargs)
                
        return wrapper
    
    return real_decorator


def get_or_create_file(path: str, filename: str):
    """Create binary file under the path directory and return Pathlib instance.
    
    Args:
        path (str): Absolute path of directory under which file will be created
        filename (str): Name that file will be stored as.
        
    Returns:
        Path: Path instance of file.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return (p / filename)
    

def extract_data(data_url: str, exec_time: str, **context: Mapping[Any, Any]):
    """Read CSV from data_url and persist it in the raw data directory.

    Args:
        data_url (str): Url from which CSV will be retrieved
        exec_time (str): Date and time when execution started
    """
    response = requests.get(url=data_url, stream=True)
    if not response.status_code == 200:
        logging.error(f"Failed request to {data_url}")
        response.raise_for_status()
        
    logging.info(f"Successfully retrieved vaccine data from {data_url}")

    dump_file = get_or_create_file(RAW_DATA_DIR, f"{exec_time}.csv")
    with dump_file.open('w') as fp:
        # prevent entire contents being loaded into memory
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            fp.write(chunk)
            
    logging.info(f"Stored raw file at {dump_file}")

    # TODO: serialize as pickled df

@csv_to_df(RAW_DATA_DIR)
def transform_data(transformations, exec_time: str, **context):
    """Load persisted df, perform transformations and persist to transformed directory"""
    pipeline = Transformer.build_pipeline(transformations=transformations)
    df = context['df']
    df: pd.DataFrame = Transformer.run_pipeline(dataframe=df, pipeline=pipeline,meta_data=None)
    logging.info(f"Successfully applied transformations.")
    dump_file = get_or_create_file(TRANSFORM_DATA_DIR, f"{exec_time}.csv")
    df.to_csv(dump_file, index=False)
    logging.info(f"Stored transformed file at {dump_file}")
    
    
@csv_to_df(TRANSFORM_DATA_DIR)
def load_data(db_connection, destination_table, exec_time: str, **context):
    """Load persisted df, truncate destination_table and load df to database.

    Args:
        db_connection ([type]): Database connection string.
        destination_table ([type]): Name of table to import data into.
    """
    df = context['df']
    df.index.rename('id', inplace=True)
    df.index += 1
    df['date'] = pd.to_datetime(df['date'])
    engine = create_engine(db_connection)
    df.head(0).to_sql(destination_table, engine, if_exists='replace') #drops old table and creates new empty table
    
    logging.info(f"Successfully truncated {destination_table}")

    conn = engine.raw_connection()
    cur = conn.cursor()

    # convert df to csv and load it into memory
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, destination_table, null='') # null values become ''
    conn.commit()
    
    logging.info(f"Imported new load of vaccine data into {destination_table}")
    
    # move data to archive 
    from_file = get_or_create_file(TRANSFORM_DATA_DIR, f"{exec_time}.csv")
    exec_date, exec_timestamp = exec_time.split('T')
    archive_sub_dir = f'{exec_date.replace("-", "/")}/'\
                        f'{"/".join(exec_timestamp.split(":")[:3])}'
    to_file = get_or_create_file(f'{ARCHIVE_DATA_DIR}{archive_sub_dir}/', 'vax_data.csv')
    shutil.copy(from_file, to_file)
    logging.info(f"Archived transformed file at {to_file}")