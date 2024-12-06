from abc import ABC, abstractmethod

import pandas as pd


class Fetcher(ABC):

    bucket_name: str

    @abstractmethod
    def fetch_data(self, query: str, verify_sll: bool) -> pd.DataFrame:
        pass
