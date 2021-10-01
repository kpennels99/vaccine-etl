"""Transformer to return unique column value count across duplicate key values."""
import pandas as pd

from .factory import Transformer


class FillEmptyCountsTransformer(Transformer):
    """Only use the last n rows."""

    def __init__(self, filter_column, count_columns):
        """
        Class initialisation.

        :param key_columns: Columns to check for duplicate rows
        :param count_column: Column to count for duplicate rows
        :param output_column: name of output column
        """
        self.filter_column = filter_column
        self.count_columns = count_columns
        
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply Weeks in Market (win) transformation."""

        for colum_filter in df[self.filter_column].unique():
            print(f"filling for {colum_filter}")
            df.loc[(df[self.filter_column]==colum_filter), self.count_columns] = \
                df.loc[(df[self.filter_column]==colum_filter), self.count_columns].fillna(method='ffill')

        return df