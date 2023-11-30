from typing import Iterable

import pandas as pd

from . import metrics

class EvaluationStrategy:

    """
    Base class for evaluation strategies.
    """

    def __init__(self, alpha: float = 0.05, tolerance: float = 0.05) -> None:
        self.alpha = alpha
        self.tolerance = tolerance

    def __repr__(self) -> str:
        return self.__class__.__name__
    
    def evaluate(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, float]:
        pass

class DistributionComparisson(EvaluationStrategy):

    """
    This strategy is based on data distributions. More specifically, it asserts wether or not the category fields are distributed equally. Furthermore, it also asserts that both 
    sample and population distributions are the same in numeric continuous fields across all the posible categories filters.
    """

    def __init__(self, alpha: float = 0.05, tolerance: float = 0.05, time_series_analytics: bool = False, category_based_analytics: bool = False) -> None:
        super().__init__(alpha, tolerance)
        self.time_series_analytics = time_series_analytics
        self.category_based_analytics = category_based_analytics

        if self.category_based_analytics:
            raise NotImplementedError("Cannot perform ``category_based_analytics`` as stratification is not implemented yet.")
        
        if self.time_series_analytics:
            raise NotImplementedError("Cannot perform ``time_series_analytics`` as it's not implemented yet.")

    def evaluate(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, float]:

        p_cat_df = population.select_dtypes(include=['object'])
        s_cat_df = sample.select_dtypes(include=['object'])
        cat_eval = self._eval_categoric_fields(population=p_cat_df, sample=s_cat_df)

        p_dt_df = population.select_dtypes(include=['datetimetz'])
        s_dt_df = sample.select_dtypes(include=['datetimetz'])
        dt_eval = self._eval_datetime_fields(population=p_dt_df, sample=s_dt_df)

        p_num_df = population.select_dtypes(include=['number'])
        s_num_df = sample.select_dtypes(include=['number'])
        num_eval = self._eval_numeric_fields(population=p_num_df, sample=s_num_df)

        result = {**cat_eval, **dt_eval, **num_eval}
        return result
    
    def _eval_numeric_fields(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, float]:
        columns = population.columns
        result = {column : self._apply_kolmogorov_smirnov(population=population[column], sample=sample[column])[0] for column in columns}
        print(result)
        return result

    def _eval_datetime_fields(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, float]:
        columns = population.columns
        result = {column : self._apply_random_value_assignment(population=population[column], sample=sample[column])[0] for column in columns}
        print(result)
        return result

    def _eval_categoric_fields(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, float]:
        columns = population.columns
        result = {column : self._apply_random_value_assignment(population=population[column], sample=sample[column])[0] for column in columns}
        print(result)
        return result

    def _apply_kolmogorov_smirnov(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:
        return metrics.KolmogorovSmirnov().measure(population=population, sample=sample) # TODO: Cambiar por filtrado de columnas por flotantes
    
    def _apply_random_value_assignment(self, population: pd.DataFrame, sample: pd.DataFrame) -> Iterable[float]:
        return metrics.RandomValueAssignment().measure(population=population, sample=sample)