"""Factory pattern for DataFrame transformations."""
import logging
from datetime import datetime
from functools import reduce
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)

# TODO pipe or edit inplace data through transformations rather than copy
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.pipe.html
# https://www.kaggle.com/jankoch/scikit-learn-pipelines-and-pandas
# https://www.dataquest.io/blog/pandas-big-data/


class TransformerFactory(type):
    """Factory pattern for DataFrame transformations."""

    installed = {}

    def __new__(cls, name, bases, attrs):
        """Save derived classes in static class attribute."""
        sub = type.__new__(cls, name, bases, attrs)
        TransformerFactory.installed[name] = sub
        return sub

    @classmethod
    def build(cls, name, *args, **kwargs):
        """Build derived class from key."""
        try:
            sub = cls.installed[name]
        except KeyError:
            raise ValueError('Transformer not found: %s' % name)
        return sub(*args, **kwargs)


class Transformer(metaclass=TransformerFactory):
    """Factory pattern base class."""

    @classmethod
    def build_pipeline(cls, transformations):
        """Generate transformation pipeline from config."""
        def build(transformation):
            return TransformerFactory.build(**transformation)

        return map(build, transformations)

    @classmethod
    def run_pipeline(cls, dataframe, pipeline, meta_data=None):
        """Apply transformation pipeline to data and return result."""
        exec_time = datetime.now()

        def run_step(data, step):
            logger.info('running ===> %s' % step.__class__)
            result = step.apply(data)

            if meta_data:
                if not result.empty:
                    class_name = type(step).__name__
                    saver = TransformSaver(result, class_name, exec_time,
                                           meta_data)
                    saver.save_df()
                else:
                    logger.info("Skipping writing df as it is empty.")

            if hasattr(result, 'head'):
                logger.info('Transformer result preview ===>\n\n%s' % result.head())
            return result

        if hasattr(dataframe, 'head'):
            logger.info('Start point preview ===>\n\n%s' % dataframe.head())
        return reduce(run_step, pipeline, dataframe)

    def apply(self, _dataframe):
        """Interface for transformation to expose functionality."""
        raise NotImplementedError()


class TransformSaver:
    """Write df to csv."""

    def __init__(self, df: pd.DataFrame, transformer_name: str,
                 exec_time: datetime, options: dict):
        """
        Initialise instance variables.

        :param df: Dataframe to save.
        :param transformer_name: Name of transformer.
        :param exec_time: Timestamp when the transformer was run.
        :param options: File destination options
        """
        self.df = df
        self.exec_time = exec_time
        self.transformer_name = transformer_name
        self.options = options

    def save_df(self):
        """Call the save method specified in the options dictionary."""
        file_name = f'{self.get_order_number()}_{self.transformer_name}.csv'
        method = self.options.get('method')
        result_dir = getattr(TransformSaver, f"{method}_df")(self, file_name)
        logger.info(f"Successfully {method}ed {self.transformer_name}"
                    f" to {result_dir}")

    def persist_df(self, file_name: str):
        """
        Persist dataframe to local storage.

        :param file_name: Name that will transformer will be saved as.
        :return: Absolute path to persisted dataframe.
        """
        dest_dir = f"{self.options.get('destination')}/" \
            f"{self.options.get('dag_id')}/{self.options.get('task_id')}/" \
            f"{self.exec_time}"
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        dest_file_name = f"{dest_dir}/{file_name}"
        self.df.to_csv(dest_file_name, index=False)

        return dest_file_name

    def upload_df(self, file_name: str):
        """
        Persist dataframe to azure blob storage.

        :param file_name: Name that will transformer will be saved as.
        :return: Absolute path to persisted dataframe.
        """
        wasb_hook = WasbHook('accumine_azure')
        dest_dir = f"{self.options.get('destination')}/" \
            f"{self.options.get('task_id')}/{self.exec_time}"
        dest_file_name = f"{dest_dir}/{file_name}"
        with NamedTemporaryFile() as temp_file:
            self.df.to_csv(temp_file.name, index=False)
            wasb_hook.load_file(temp_file.name, self.options.get('container'),
                                dest_file_name)
        return dest_file_name

    @staticmethod
    def get_order_number():
        """Generate string that orders transformers according to time."""
        return datetime.now().strftime("%H:%M:%S:%f")
