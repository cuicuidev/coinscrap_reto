from typing import Iterable

import pandas as pd
import plotly

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
    
    def evaluate(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, dict[str, float]]:
        pass

    def _plot(self, results: pd.DataFrame) -> Iterable[plotly.graph_objs.Figure]:
        pass

class DistributionComparisson(EvaluationStrategy):

    """
    This strategy is focused on asserting wether or not the population's data distributions are different from the sample's ones.
    The approach es as follows:
    - First, we separate the data into numeric and categoric variables.
    - We apply the Kolmogorov-Smirnov test to each one of the numeric columns.
    - Then, we apply the Chi Squared Goodness of Fit test to all the categoric columns, independently as well.
    - The evaluation results are stored as a dictionary that contains all the columns as keys and the metrics as values stored in an iterable of two elements (statistic and p-value).
    """

    def __init__(self, alpha: float = 0.05, tolerance: float = 0.05, time_series_analytics: bool = False, category_based_analytics: bool = False) -> None:
        super().__init__(alpha, tolerance)
        self.time_series_analytics = time_series_analytics
        self.category_based_analytics = category_based_analytics

        if self.category_based_analytics:
            raise NotImplementedError("Cannot perform ``category_based_analytics`` as stratification is not implemented yet.")
        
        if self.time_series_analytics:
            raise NotImplementedError("Cannot perform ``time_series_analytics`` as it's not implemented yet.")

    def evaluate(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, dict[str, float]]:

        p_cat_df = population.select_dtypes(include=['object'])
        s_cat_df = sample.select_dtypes(include=['object'])
        cat_eval = self._eval_categoric_fields(population=p_cat_df, sample=s_cat_df)

        p_num_df = population.select_dtypes(include=['number'])
        s_num_df = sample.select_dtypes(include=['number'])
        num_eval = self._eval_numeric_fields(population=p_num_df, sample=s_num_df)

        result = {**cat_eval, **num_eval}
        return result
    
    def _eval_numeric_fields(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, dict[str, float]]:
        columns = population.columns
        result = {column : self._apply_kolmogorov_smirnov(population=population[column], sample=sample[column]) for column in columns}
        return result

    def _eval_categoric_fields(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, dict[str, float]]:
        columns = population.columns
        result = {column : self._apply_chi_squared(population=population[column], sample=sample[column]) for column in columns}
        return result

    def _apply_kolmogorov_smirnov(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:
        result = {}
        result['ks_score'], result['p_value'] = metrics.KolmogorovSmirnov().measure(population=population, sample=sample)
        return result
    
    def _apply_chi_squared(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:
        result = {}
        result['chi_squared'], result['p_value'] = metrics.ChiSquaredGoodnessOfFit().measure(population=population, sample=sample)
        return result
    
    def _plot(self, results: pd.DataFrame) -> Iterable[plotly.graph_objs.Figure]:
        pass