from typing import Iterable, Optional

import pandas as pd

from . import sampling, evaluations

class Evaluation:

    """
    This class recieves a pandas ``DataFrame`` object as ``df``, an iterable of ``SamplingStrategy`` objects as ``sampling_strategies`` and an ``evaluation_strategy`` as a 
    ``EvaluationStrategy`` object. Once instantiated, it allowes to use methods such as ``.run()`` and ``.plot()`` to evaluate all the sampling strategies 
    using the evaluation strategy, across all sample sizes between 1 and the size of ``df``.
    """
    
    def __init__(self, df: pd.DataFrame, sampling_strategies: Iterable[sampling.SamplingStrategy], evaluation_strategy: evaluations.EvaluationStrategy) -> None:
        self.df = df
        self.strategies = sampling_strategies
        self.evaluation_strategy = evaluation_strategy

        self.eval: Optional[pd.DataFrame] = None

    def run(self, step: int = 50, random_state: Optional[int | float] = None) -> pd.DataFrame:

        """
        Evaluates every ``SamplingStrategy`` in ``self.sampling_strategies`` against the ``self.evaluation_strategy`` for every sample 
        size between 1 and the size of ``self.df`` in strides of ``step``.
        """

        results: Iterable[pd.DataFrame] = []

        for strategy in self.strategies:
            result = self._evaluate_sampling_strategy(strategy=strategy, step = step, random_state = random_state)
            results.append(result)

        result = pd.concat(results)
        self.eval = result
        return result
    
    def plot(self) -> None:

        """
        Displays all the plots of the evaluation strategy.
        """

        figures = self.evaluation_strategy._plot(results=self.eval)
        
        for fig in figures:
            fig.show()


    def _evaluate_sampling_strategy(self, strategy: sampling.SamplingStrategy, step: int, random_state: Optional[int | float]) -> pd.DataFrame:

        """
        Evaluates a ``SamplingStrategy`` against the ``self.evaluation_strategy`` for every sample size between 1 and the size of ``self.df`` in strides of ``step``.
        """
        
        population_size = self.df.shape[0]
        results = {col : [] for col in self.df.columns}
        results['SampleSize']: Iterable[int] = []

        for n in range(step, population_size, step):
            sample = self._apply_sampling_strategy(strategy=strategy, n=n, random_state=random_state)
            result = self._evaluate_sample(sample=sample)

            results['SampleSize'].append(n)

            for column, score in result.items():
                results[column].append(score)

        if strategy.alias:
            results['SamplingStrategy'] = [strategy.__repr__() + strategy.alias for _ in range(len(list(results.values())[0]))]
        else:
            results['SamplingStrategy'] = [strategy.__repr__() for _ in range(len(list(results.values())[0]))]

        return pd.DataFrame(results)
    
    def _evaluate_sample(self, sample: pd.DataFrame) -> dict[str, float]:

        """
        Evaluates a single sample with the ``self.evaluation_strategy``.
        """
        
        return self.evaluation_strategy.evaluate(population=self.df, sample=sample)

    def _apply_sampling_strategy(self, strategy: sampling.SamplingStrategy, n: int, random_state: Optional[int | float]) -> pd.DataFrame:
        
        """
        Samples ``self.df`` with the size ``n`` using a ``SamplingStrategy`` passed as ``strategy```.
        """

        return strategy.sample(self.df, n=n, random_state=random_state)

