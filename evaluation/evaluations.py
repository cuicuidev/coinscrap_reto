from typing import Iterable

import pandas as pd

from . import metrics

class EvaluationStrategy:

    def __init__(self, alpha: float = 0.05, tolerance: float = 0.05) -> None:
        self.alpha = alpha
        self.tolerance = tolerance

    def __repr__(self) -> str:
        return self.__class__.__name__
    
    def evaluate(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, float]:
        pass

class DistributionComparisson(EvaluationStrategy):

    def evaluate(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, float]:
        float_columns = population.select_dtypes(include=['float']).columns
        non_float_columns = population.drop(float_columns, axis=1).columns

        ks_result = {column : self._apply_kolmogorov_smirnov(population=population[column], sample=sample[column])[0] for column in float_columns}
        random_result = {column : self._apply_random_value_assignment(population=population[column], sample=sample[column])[0] for column in non_float_columns}
        ks_result.update(random_result)
        result = ks_result
        return result
    
    def _apply_kolmogorov_smirnov(self, population: pd.Series, sample: pd.DataFrame) -> Iterable[float]:
        return metrics.KolmogorovSmirnov().measure(population=population, sample=sample) # TODO: Cambiar por filtrado de columnas por flotantes
    
    def _apply_random_value_assignment(self, population: pd.DataFrame, sample: pd.DataFrame) -> Iterable[float]:
        return metrics.RandomValueAssignment().measure(population=population, sample=sample)