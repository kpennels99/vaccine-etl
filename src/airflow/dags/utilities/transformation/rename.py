"""Transformer to change the name of a columns."""
import pandas as pd
from typing import Mapping

from .factory import Transformer


class RenameTransformer(Transformer):
    """Given a mapping dictionary, rename columns."""

    def __init__(self, mapping: Mapping[str,str]):
        """Initialise instance attribute.
        
        Example:
            mapping: {"letter": "alphabet"}
            +-----------------+   +-------------------+
            |        df       |   |        df         |
            +--------+--------+   +----------+--------+
            | letter | number |   | alphabet | number |
            +--------+--------+   +----------+--------+
            | a      | 0      | = | a        | 0      |
            +--------+--------+   +----------+--------+
            | b      | 2      |   | b        | 2      |
            +--------+--------+   +----------+--------+
            | b      | 3      |   | b        | 3      |
            +--------+--------+   +----------+--------+

        Args:
            mapping (Mapping[str,str]): Old to new column name mapping.
        """
        self.mapping = mapping

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename column names using mapping.

        Args:
            df (pd.DataFrame): Input dataframe.

        Returns:
            pd.DataFrame: Output dataframe with transformation applied.
        """
        df.rename(columns=self.mapping, inplace=True)

        return df
