"""Transformer to return unique column value count across duplicate key values."""
import pandas as pd

from .factory import Transformer


class WindowByDaysTransformer(Transformer):
    """Only use the last n rows."""

    def __init__(self, number_of_days):
        """
        Class initialisation.

        :param key_columns: Columns to check for duplicate rows
        :param count_column: Column to count for duplicate rows
        :param output_column: name of output column
        """
        self.number_of_days = number_of_days
        
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply Weeks in Market (win) transformation."""
        return df.tail(self.number_of_days)
