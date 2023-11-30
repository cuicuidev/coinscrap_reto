from typing import Iterable
import random

import pandas as pd

from scipy import stats

class MetricStrategy:

    def __repr__(self) -> str:
        return self.__class__.__name__
    
    def measure(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:
        pass

class RandomValueAssignment(MetricStrategy):

    """
    ## This class is purely for interface testing.
    """

    def measure(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:
        return random.random(), random.random()

class KolmogorovSmirnov(MetricStrategy):

    def measure(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:
        return self._apply_kolmogorov_smirnov(population=population, sample=sample)
    
    def _apply_kolmogorov_smirnov(
            self,
            population: pd.Series,
            sample: pd.Series,
        ) -> Iterable[float]:
        """
        Compares the distributions of two pandas Series

        Parameters
        ---
        - ``population_series`` is a pandas Series object that represents the population.
        - ``sample_series`` is a pandas Series object that represents a sample.

        Return
        ---
        - Returns the ks statistic and its p-value in a tuple
        """

        statistic, p = stats.ks_2samp(data1 = sample, data2 = population)
        return statistic, p