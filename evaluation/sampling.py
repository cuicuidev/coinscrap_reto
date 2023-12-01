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
    
class StratifiedRandomSampling(SamplingStrategy):

    """
    We should see improvements in chi squared evals when implementing this kind of sampling.
    """

    def sample(self, df: pd.DataFrame, n: int, random_state: int | float | None) -> pd.DataFrame:
        cat_columns = df.select_dtypes(include=['object']).columns

        print(cat_columns)

        groups = df.groupby(list(cat_columns), group_keys=False)
        proportions = groups.size() / len(df)
        sample_sizes = (proportions * n).astype(int)
        return sample_sizes # TODO: FIX THIS :(
        sample = groups.apply(lambda x: x.sample(n=sample_sizes.loc[(x.name[0], x.name[1])], random_state=random_state))
        return sample