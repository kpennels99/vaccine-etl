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

            if hasattr(result, 'head'):
                logger.info('Transformer result preview ===>\n\n%s' % result.head())
            return result

        if hasattr(dataframe, 'head'):
            logger.info('Start point preview ===>\n\n%s' % dataframe.head())
        return reduce(run_step, pipeline, dataframe)

    def apply(self, _dataframe):
        """Interface for transformation to expose functionality."""
        raise NotImplementedError()
