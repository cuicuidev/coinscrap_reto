from typing import Optional, Iterable
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

class SamplingStrategy:

    def __init__(self, alias: Optional[str] = None) -> None:
        self.alias = alias

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

    def __init__(self, strata: Iterable[str], alias: Optional[str] = None) -> None:
        super().__init__(alias=alias)
        self.strata = strata

    def sample(self, df: pd.DataFrame, n: int, random_state: int | float | None) -> pd.DataFrame:

        def take_sample(group: pd.DataFrame) -> pd.DataFrame:
            proportion = len(group) / len(df)
            stratum_sample_size = round(n * proportion)
            return group.sample(min(len(group), stratum_sample_size), random_state=random_state)
        
        sample: pd.DataFrame = df.groupby(self.strata, group_keys=False, as_index=False).apply(take_sample)
        if len(sample) < n:
            remaining_df = df.merge(sample, indicator=True, how='outer').loc[lambda x: x['_merge'] == 'left_only']
            random_sample = remaining_df.sample(n-len(sample), random_state=42)
            sample = pd.concat([sample, random_sample]).drop('_merge', axis=1)
        return sample
    
class ClusterSampling(SamplingStrategy):

    """
    What if we cluster the data and use the cluster column as a strata?
    """

    def __init__(self, df: pd.DataFrame, n_clusters: int, fields: Iterable[str], random_state: Optional[int | float] = None, alias: Optional[str] = None) -> None:
        super().__init__(alias=alias)
        self.df = df.copy()
        self.n_clusters = n_clusters
        self.fields = fields

        kmeans = KMeans(n_clusters=self.n_clusters, n_init='auto', random_state=random_state)
        scaler = MinMaxScaler()
        cluster_data = self.df[self.fields]
        X, _ = self._encode(cluster_data)
        X = scaler.fit_transform(X)
        kmeans.fit(X)

        self.df['cluster'] = kmeans.labels_
        self.labels = kmeans.labels_

    def sample(self, df: pd.DataFrame, n: int, random_state: int | float | None) -> pd.DataFrame:
        
        sample: pd.DataFrame = self.df.groupby('cluster', group_keys=False, as_index=False).apply(self._sample_group, df_size= len(self.df), total_sample_size=n, random_state=random_state)
        if len(sample) < n:
            remaining_df = self.df.merge(sample, indicator=True, how='outer').loc[lambda x: x['_merge'] == 'left_only']
            random_sample = remaining_df.sample(n-len(sample), random_state=42)
            sample = pd.concat([sample, random_sample]).drop(['_merge'], axis=1)

        return sample.drop('cluster', axis=1)
    
    def _encode(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        encoded_df = df.copy()
        encodings = {}
        for column in encoded_df.columns:
            if encoded_df[column].dtype == 'object':
                encoder = LabelEncoder()
                encoded_df[column] = encoder.fit_transform(encoded_df[column])
                encodings[column] = encoder
        return encoded_df, encodings
    
    def _decode(self, df: pd.DataFrame, encodings: dict) -> pd.DataFrame:
        decoded_df = df.copy()
        for column, encoder in encodings.items():
            decoded_df[column] = encoder.inverse_transform(decoded_df[column])
        return decoded_df
    
    def _sample_group(self, group: pd.DataFrame, df_size: int, total_sample_size: int, random_state: int | float | None = None) -> pd.DataFrame:
        proportion = len(group) / df_size
        stratum_sample_size = round(total_sample_size * proportion)
        return group.sample(min(len(group), stratum_sample_size), random_state=random_state)