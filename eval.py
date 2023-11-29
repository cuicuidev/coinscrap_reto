import pandas as pd
from plotly.graph_objects import Figure
import plotly.express as px
import glob

class Eval:

    def __init__(self, df: pd.DataFrame | None = None, feature_importances: dict | None = None):

        self.df = df
        if df is None:
            print('heeheee')
            self.df = pd.concat([pd.read_csv(csv, sep=";") for csv in glob.glob("*.csv")])

        self.feature_importances = {"curtosis" : 1, "symetry" : 1, "time_series_continuity" : 1}
        if feature_importances is not None:
            self.feature_importances.update(feature_importances)

        self.eval = None

        self.population_eval = self._get_metrics(self.df)

        def process_df(df: pd.DataFrame) -> pd.DataFrame:
            df['datetime'] = pd.to_datetime(df.date)

            df['year'] = df.datetime.dt.year
            df['month'] = df.datetime.dt.month
            df['day'] = df.datetime.dt.day
            df['hour'] = df.datetime.dt.hour
            df['minute'] = df.datetime.dt.minute
            df['second'] = df.datetime.dt.second
            df['utc_offset'] = df.datetime.apply(lambda x: x.utcoffset().total_seconds())

            seasons_map = {
                1 : 'winter',
                2 : 'winter',
                3 : 'spring',
                4 : 'spring',
                5 : 'spring',
                6 : 'summer',
                7 : 'summer',
                8 : 'summer',
                9 : 'fall',
                10 : 'fall',
                11 : 'fall',
                12 : 'winter',
            }
            df['season'] = df.month.replace(seasons_map)

            df.rename(columns={"Categoría": "category"}, inplace=True)

            df = df.drop("date", axis=1)

            return df

        self.df = process_df(self.df)


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



if __name__ == '__main__':
    e = Eval()
    e.plot()