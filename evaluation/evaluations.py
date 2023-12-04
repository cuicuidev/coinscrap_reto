from typing import Iterable, Optional

import pandas as pd
import numpy as np
import plotly
import plotly.express as px

from . import metrics

def get_metric(var, metric: metrics.MetricStrategy):

    """
    Takes in a variable and a metric strategy. Returns the variable if it holds a metric or if it's not a dictionary type, else returns a numpy nan object.
    """

    if isinstance(var, dict):
        m = var.get(metric.__repr__())
        return var if m else np.nan

    return var

class EvaluationStrategy:

    """
    Base class for evaluation strategies.
    """

    def __init__(self, alpha: Optional[float] = None, tolerance: Optional[float] = None) -> None:

        self.alpha = alpha
        self.tolerance = tolerance

        if self.tolerance:
            raise NotImplementedError("``tolerance`` not implemented.")
        if self.alpha:
            raise NotImplementedError("``alpha`` not implemented.")
        

    def __repr__(self) -> str:

        return self.__class__.__name__
    
    
    def evaluate(self, population: pd.DataFrame, sample: pd.DataFrame) -> dict[str, dict[str, float]]:

        """
        ## Main interface of the evaluation strategy.
        - Must always receive a population and a sample as Pandas DataFrame instances.
        - Must always return data structured as ``dict[str, dict[str, float]]``.

        #### Notes for dev:
        - Implement Pydantic models to better handle interfaces.
        """
        
        pass


    def _plot(self, results: pd.DataFrame) -> Iterable[plotly.graph_objs.Figure]:

        """
        ## Interface for evaluation plots.
        - Must always receive a Pandas DataFrame instance as an input.
        - Must always yield Plotly Figure instances, or return them as an iterable type.
        """

        pass

class DistributionComparisson(EvaluationStrategy):

    """
    This strategy is focused on asserting wether or not the population's data distributions are different from the sample's ones.
    The approach is as follows:
    - First, we separate the data into numeric and categoric variables.
    - We apply the Kolmogorov-Smirnov test to each one of the numeric columns.
    - Then, we apply the Chi Squared Goodness of Fit test to all the categoric columns, independently as well.
    - The evaluation results are stored as a dictionary that contains all the columns as keys and the metrics as values stored in an iterable of two elements (statistic and p-value).
    """

    def __init__(self, alpha: Optional[float] = None, tolerance: Optional[float] = None, time_series_analytics: bool = False, category_based_analytics: bool = False) -> None:

        super().__init__(alpha, tolerance)
        self.time_series_analytics = time_series_analytics
        self.category_based_analytics = category_based_analytics

        if self.category_based_analytics:
            raise NotImplementedError("Cannot perform ``category_based_analytics`` as it's not implemented yet.")
        
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
        result[metrics.KolmogorovSmirnov().__repr__()], result['p_value'] = metrics.KolmogorovSmirnov().measure(population=population, sample=sample)
        return result
    
    
    def _apply_chi_squared(self, population: pd.Series, sample: pd.Series) -> Iterable[float]:

        result = {}
        result[metrics.ChiSquaredGoodnessOfFit().__repr__()], result['p_value'] = metrics.ChiSquaredGoodnessOfFit().measure(population=population, sample=sample)
        return result
    

    def _get_metric_dfs(self, df: pd.DataFrame, metric: metrics.MetricStrategy) -> pd.DataFrame:

        df = df.map(get_metric, metric=metric)
        df = df.dropna(axis=1)

        m_df = df.map(lambda x: x.get(metric.__repr__()) if isinstance(x, dict) else x) # metrics
        p_df = df.map(lambda x: x.get('p_value') if isinstance(x, dict) else x) # p-values

        return m_df, p_df
    
    
    def _plot(self, results: pd.DataFrame) -> Iterable[plotly.graph_objs.Figure]:

        x = 'SampleSize'
        color = 'SamplingStrategy'

        chi_m, chi_p = self._get_metric_dfs(results, metric=metrics.ChiSquaredGoodnessOfFit())
        title =metrics.ChiSquaredGoodnessOfFit().__repr__()

        y = list(chi_m.drop([x, color], axis=1).columns)
        yield px.line(chi_m, x=x, y=y, color=color, title=title + " statistic")
        
        y = list(chi_p.drop([x, color], axis=1).columns)
        yield px.line(chi_p, x=x, y=y, color=color, title=title + "'s p-value")

        ks_m, ks_p = self._get_metric_dfs(results, metric=metrics.KolmogorovSmirnov())
        title =metrics.KolmogorovSmirnov().__repr__()

        y = list(ks_m.drop([x, color], axis=1).columns)
        yield px.line(ks_m, x=x, y=y, color=color, title=title + " statistic")
        
        y = list(ks_p.drop([x, color], axis=1).columns)
        yield px.line(ks_p, x=x, y=y, color=color, title=title + "'s p-value")