"""Transformer to sum metric columns in rows with duplicates in key columns."""
import io
from os import replace
from typing import Union
import urllib

import pandas as pd
import requests

from .factory import Transformer


class AddExternalColumnTransformer(Transformer):
    """Combine duplicate rows by summing metric columns."""

    def __init__(self, match_column_mapping, external_columns):
        """
        Class initialisation.

        :param key_columns: Columns to check for duplicate rows
        :param sum_columns: Columns to sum for duplicate rows
        """
        self.internal_match_columns = list(match_column_mapping.keys())
        self.external_match_columns = list(match_column_mapping.values())
        self.external_columns = external_columns

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply transformation."""
        supplement_df = pd.read_csv("https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv")
        drop_columns = [
            item for item in supplement_df.columns
            if item not in self.internal_match_columns + self.external_match_columns + \
                self.external_columns
        ]
        supplement_df.drop(columns=drop_columns, inplace=True)
        joined_df = pd.merge(df, 
                             supplement_df, 
                             left_on=self.internal_match_columns,
                             right_on=self.external_match_columns,
                             how='left')
        # for count_column in self.count_column_mapping:
        #     joined_df[f"{count_column}_x"].fillna(joined_df[f"{count_column}_y"], inplace=True)
        
        return joined_df