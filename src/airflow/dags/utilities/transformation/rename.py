"""Change the name of a column."""
import pandas as pd

from .factory import Transformer


class RenameTransformer(Transformer):
    """Given a mapping dictionary, rename columns."""

    def __init__(self, mapping: dict):
        """
        Class initialisation.

        :param columns: dictionary of old and new column names
        """
        self.mapping = mapping

        super().__init__()

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply transformation."""
        df.rename(columns=self.mapping, inplace=True)

        return df
