"""Excel data loader for the Relationship Finder MCP service."""
import os
from datetime import datetime
from threading import Lock
from typing import Optional

import pandas as pd


class ExcelLoader:
    """Thread-safe Excel data loader with caching."""

    def __init__(self, excel_path: str, aliases_path: Optional[str] = None):
        """Initialize the loader with paths to Excel files."""
        self.excel_path = excel_path
        self.aliases_path = aliases_path
        self._df: Optional[pd.DataFrame] = None
        self._last_loaded: Optional[datetime] = None
        self._last_mtime: Optional[float] = None
        self._lock = Lock()

    def _load_excel(self) -> pd.DataFrame:
        """Load the Excel file and optional aliases."""
        df = pd.read_excel(self.excel_path)
        
        if self.aliases_path and os.path.exists(self.aliases_path):
            aliases = pd.read_excel(self.aliases_path)
            # Add alias rows to main dataframe
            alias_rows = []
            for _, row in aliases.iterrows():
                alias_rows.append({
                    "Name": row["Alias"],
                    "RelationshipToGirish": df[df["Name"] == row["Name"]]["RelationshipToGirish"].iloc[0]
                })
            if alias_rows:
                df = pd.concat([df, pd.DataFrame(alias_rows)], ignore_index=True)

        return df

    def needs_reload(self) -> bool:
        """Check if the Excel file has been modified since last load."""
        try:
            current_mtime = os.path.getmtime(self.excel_path)
            return (
                self._last_mtime is None
                or self._df is None
                or current_mtime > self._last_mtime
            )
        except OSError:
            return True

    def get_df(self) -> pd.DataFrame:
        """Get the current DataFrame, reloading if necessary."""
        with self._lock:
            if self.needs_reload():
                self._df = self._load_excel()
                self._last_loaded = datetime.utcnow()
                self._last_mtime = os.path.getmtime(self.excel_path)
            return self._df

    def reload(self) -> None:
        """Force reload the Excel file."""
        with self._lock:
            self._df = self._load_excel()
            self._last_loaded = datetime.utcnow()
            self._last_mtime = os.path.getmtime(self.excel_path)

    def get_last_loaded(self) -> Optional[datetime]:
        """Get the last load timestamp."""
        return self._last_loaded

    def get_row_count(self) -> int:
        """Get the total number of rows in the DataFrame."""
        df = self.get_df()
        return len(df)