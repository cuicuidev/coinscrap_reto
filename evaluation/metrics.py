from typing import Iterable
import random

import pandas as pd

from scipy import stats

class MetricStrategy:

    def __repr__(self) -> str:

        return self.__class__.__name__
    
    def measure(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:

        """
        ## Main interface for a metric strategy.
        - Must always receive a population and a sample as Pandas Series instances.
        - Must always return an iterable type of floating point numbers.
        """
        
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
        Compares the distributions of two numeric pandas Series using the Kolmogorov-Smirnov method.

        - Returns the ks statistic and its p-value in a tuple.
        """

        statistic, p = stats.ks_2samp(data1 = sample, data2 = population)
        return statistic, p
    
    
class ChiSquaredGoodnessOfFit(MetricStrategy):

    def measure(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:

        return self._apply_chi_squared(population=population, sample=sample)
    
    
    def _apply_chi_squared(
            self,
            population: pd.Series,
            sample = pd.Series,
        ) -> Iterable[float]:

        """
        Compares the distributions of two categoric pandas Series using the Chi Squared Goodness of Fit method.

        - Returns the chi squared statistic and its p-value in a tuple.
        """

        population_counts = population.value_counts()
        sample_counts = sample.value_counts()

        contingency_table = pd.DataFrame({'Population': population_counts, 'Sample': sample_counts})

        contingency_table = contingency_table.fillna(0)

        statistic, p, _, _ = stats.chi2_contingency(contingency_table)

        return statistic, p