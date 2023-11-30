from typing import Optional
import pandas as pd

class SamplingStrategy:

    def __repr__(self) -> str:
        return self.__class__.__name__
    
    def sample(self, df: pd.DataFrame, n: int, random_state: Optional[int | float]) -> pd.DataFrame:
        pass

class RandomSampling(SamplingStrategy):

    """
    ## This class is purely for interface testing.
    """

    def sample(self, df: pd.DataFrame, n: int, random_state: Optional[int | float]) -> pd.DataFrame:
        s = df.sample(n=n, random_state=random_state)
        return s