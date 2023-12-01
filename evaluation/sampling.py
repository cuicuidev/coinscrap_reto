from typing import Optional, Iterable
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

    def __init__(self, strata: Iterable[str]) -> None:
        self.strata = strata

    def sample(self, df: pd.DataFrame, n: int, random_state: int | float | None) -> pd.DataFrame:

        def take_sample(group: pd.DataFrame) -> pd.DataFrame:
            proportion = len(group) / len(df)
            stratum_sample_size = round(n * proportion)
            # print(stratum_sample_size)
            return group.sample(min(len(group), stratum_sample_size), random_state=random_state)
        
        sample: pd.DataFrame = df.groupby(self.strata, group_keys=False, as_index=False).apply(take_sample)
        if len(sample) < n:
            remaining_df = df.merge(sample, indicator=True, how='outer').loc[lambda x: x['_merge'] == 'left_only']
            random_sample = remaining_df.sample(n-len(sample), random_state=42)
            sample = pd.concat([sample, random_sample]).drop('_merge', axis=1)
        return sample