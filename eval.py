import pandas as pd
from plotly.graph_objects import Figure
import plotly.express as px
import glob

class Eval:

    def __init__(self, df: pd.DataFrame | None = None, feature_importances: dict | None = None):

        self.df = df
        if self.df is None:
            self.df = pd.concat([pd.read_csv(csv, sep=";") for csv in glob.glob("*.csv")])

        self.feature_importances = {"curtosis" : 1, "symetry" : 1, "time_series_continuity" : 1}
        if feature_importances is not None:
            self.feature_importances.update(feature_importances)

        self.eval = None

        self.population_eval = self._get_metrics()

    def _get_metrics(self, df) -> pd.DataFrame:
        pass

    def _evaluate_sample(self, sample: pd.DataFrame) -> pd.DataFrame:
        sample_eval = self._get_metrics(sample)
        ## pseudocode
        # eval = self.population_eval - sample_eval
        # return eval.to_df()

    def sample(self, n: int) -> pd.DataFrame:
        pass

    def plot(self) -> Figure:
        if self.eval:
            return px.line(self.eval, x = 'n')
        return px.line(self.evaluate(), x ='n')

        
    def evaluate(self) -> pd.DataFrame:
        min_n = 1
        max_n = self.df.shape[0]
        evals = []
        for n in range(min_n, max_n):
            evals.append(self._evaluate_sample(n))
        self.eval = pd.concat(evals)
        return self.eval
