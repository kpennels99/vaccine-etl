"""Join external columns to dataframe."""
from typing import Mapping, List
import pandas as pd

from .factory import Transformer


class AddExternalColumnTransformer(Transformer):
    """Add external region related columns to dataframe."""

    def __init__(self, match_column_mapping: Mapping[str, str], 
                 external_columns: List[str]):
        """Initialise instance attributes.
        
        Example:
            match_column_mapping: {"letter": "alphabet"}
            external_columns: ["name"]
            +-----------------+--+------------------------+   +------------------------+
            |        df       |  |       external         |   |          df            |
            +--------+--------+  +----------+------+------+   +--------+--------+------+
            | letter | number |  | alphabet | name | foo  |   | letter | number | name |
            +--------+--------+  +----------+------+------+   +--------+--------+------+
            | a      | 1      |  | a        | Ant  | bar  | = | a      | 1      | Ant  |
            +--------+--------+  +----------+------+------+   +--------+--------+------+
            | b      | 2      |  | b        | Bert | none |   | b      | 2      | Bert |
            +--------+--------+  +----------+------+------+   +--------+--------+------+
            | c      | 3      |  | c        | Cam  | null |   | c      | 3      | Cam  |
            +--------+--------+--+----------+------+------+   +--------+--------+------+
            
        Args:
            match_column_mapping (Mapping[str, str]): Columns in df and table to join on.
            external_columns (List[str]): Columns in external table to retrieve.
        """
        self.internal_match_columns = list(match_column_mapping.keys())
        self.external_match_columns = list(match_column_mapping.values())
        self.external_columns = external_columns

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Join df to external table and retrieve external_columns.

        Args:
            df (pd.DataFrame): Input dataframe.

        Returns:
            pd.DataFrame: Output dataframe with transformation applied.
        """
        supplement_df = pd.read_csv(
            "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-"
            "Codes/master/all/all.csv"
        )
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
        return joined_df