"""Transformer to fill em."""
import pandas as pd
from typing import List

from .factory import Transformer


class FillEmptyCountsTransformer(Transformer):
    """Forward fill the count_columns empty rows within the same filter_column range."""

    def __init__(self, filter_column: str, count_columns: List[str]):
        """Initialise instance attributes.
        
        Example:
            filter_column: "letter"
            count_columns: ["number"]
            +-----------------+   +-----------------+
            |        df       |   |        df       |
            +--------+--------+   +--------+--------+
            | letter | number |   | letter | number |
            +--------+--------+   +--------+--------+
            | a      |        |   | a      |        |
            +--------+--------+   +--------+--------+
            | b      | 2      |   | b      | 2      |
            +--------+--------+   +--------+--------+
            | b      |        | = | b      | 2      |
            +--------+--------+   +--------+--------+
            | c      | 1      |   | c      | 1      |
            +--------+--------+   +--------+--------+
            | c      |        |   | c      | 1      |
            +--------+--------+   +--------+--------+
            | c      |        |   | c      | 1      |
            +--------+--------+   +--------+--------+

        Args:
            filter_column (str): Range defining column to forward fill empty value within.
            count_columns (List[str]): Columns that will be forward filled.
        """
        self.filter_column = filter_column
        self.count_columns = count_columns
        
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Forward fill count_columns empty rows within the same filter column range.

        Args:
            df (pd.DataFrame): Input dataframe.

        Returns:
            pd.DataFrame: Output dataframe with transformation applied.
        """
        for colum_filter in df[self.filter_column].unique():
            print(f"filling for {colum_filter}")
            df.loc[(df[self.filter_column]==colum_filter), self.count_columns] = \
                df.loc[(df[self.filter_column]==colum_filter), self.count_columns].fillna(method='ffill')

        return df