""" Extract relevant statistics from the Victorian daily coronavirus cases.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime


class CoronaStats:
    def __init__(self, data, regional_moving_average=0):
        _data = pd.read_csv(data, index_col='Date')
        _data.index = pd.to_datetime(_data.index + '-2020')

        self.data = _data
        self.regional_ma = regional_moving_average

        self.output_dir = './../results/'

    def _moving_average(self, remove_regional=0):
        """ Calculate an array of the 14-day moving averages.
        """

        cases = self.data.Cases

        ma = []
        for i in range(len(cases) - 14):
            ma.append(np.mean(cases[i:i+14]) - remove_regional)

        return pd.Series(np.array(ma), self.data.index[7:-7])

    def _moving_std(self):
        """ Calculate an array of the 14-day moving standard deviations.
        """

        cases = self.data.Cases[7:-7]
        ma = self._moving_average(self.regional_ma)

        ms = []
        for i in range(len(cases) - 7):
            ms.append(np.std((cases - ma)[i:i+7]))

        return pd.Series(np.array(ms), self.data.index[7:-7-7])

    def plot(self, save=False):
        """ Plot timeseries of daily cases with a 14-day moving average plot.
        """

        plt.figure(figsize=(30,20))
        plt.bar(self.data.index, self.data['Cases'])
        plt.plot(self.data.index[7:-7], self._moving_average(), color='r',
                 linewidth=10)

        forecast_ma = self.forecast_to_date('11/6/2020')
        index = forecast_ma.index - pd.Timedelta(7, 'days')
        plt.plot(index, forecast_ma['moving_average'], color='orange',
                 linewidth=10)

        std = self._moving_std()
        y = self._moving_average()[:-7]
        plt.fill_between(y.index, y - 1.645*std, y + 1.645*std,
                         color='gray', alpha=0.2)

        date_to_trigger = pd.to_datetime(self.date_to_trigger())
        plt.scatter(date_to_trigger, 5, s=1000, marker='x', color='k')
        plt.text(date_to_trigger - pd.Timedelta(20, 'days'),
                 500,
                 'Date to Step 3 trigger\n{}'.format(date_to_trigger.strftime('%d-%m-%Y')),
                 fontsize=26
                )

        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)

        if save:
            plt.savefig(self.output_dir + 'images/plot.png')

    def rrp(self):
        """ Reproduction number based off the 14-day moving averages.
        """

        ma = self._moving_average(self.regional_ma)
        rrp = pd.Series(ma.values[:-1] / ma.values[1:], ma.index[1:])

        ma_rrp = []
        for i in range(len(rrp) - 7):
            ma_rrp.append(np.mean(rrp[i:i+7]))

        return pd.Series(np.array(ma_rrp), rrp.index[:-7])

    def model(self, t):
        """
        """

        current_ma = self._moving_average(self.regional_ma)[0]
        current_std = self._moving_std()[0]
        current_rrp = self.rrp()[0]

        forecast_ma = current_ma * (current_rrp ** t)
        forecast_std = current_std * (current_rrp ** t)

        return forecast_ma, forecast_std

    def predict_cases(self, date, print_results=True):
        """ Predict coronavirus statistics on a chosen day.

        Parameters
        ----------

        date: str

            Date to forecast.

        Returns: list

            daily: 90% confidence interval of daily number of cases
            moving_average: 14-day moving average on chosen day.

        """

        t = (pd.to_datetime(date) - self.data.index[0]).days
        forecast_ma, forecast_std = self.model(t)

        min = forecast_ma - 1.645 * forecast_std
        max = forecast_ma + 1.645 * forecast_std
        forecast_range = [min, max]

        results = {
            "date": date,
            "moving_average": forecast_ma,
            "moving_std": forecast_std,
            "range_daily": forecast_range
        }

        if print_results:
            print(f'Date: {date}')
            print(f'Moving average: {forecast_ma:.2f}')
            print(f'Min.: {forecast_range[0]:.0f}')
            print(f'Max.: {forecast_range[1]:.0f}')
        else:
            return results

    def forecast_to_date(self, date, save=False):
        """
        """

        start = self.data.index[0] + pd.Timedelta(1, 'day')
        end = pd.to_datetime(date)
        time_range = pd.date_range(start=start, end=end)

        forecast_data = {}
        for day in time_range:
            forecast_data[day] = {key:self.predict_cases(day, print_results=False)[key]
                                  for key in['moving_average', 'moving_std']}

        forecast_dataframe = pd.DataFrame(forecast_data).T

        if save:
            forecast_dataframe.to_csv(self.output_dir + 'prediction.csv')

        return forecast_dataframe

    def forecast_plot(self, date, save=False):
        """
        """

        forecast = self.forecast_to_date(date)
        forecast_ma = forecast['moving_average']
        forecast_std = forecast['moving_std']

        plt.figure(figsize=(30,20))
        plt.plot(forecast_ma, color='orange',
                 linewidth=10)
        plt.bar(forecast_ma.index, forecast_ma, width=0.5)
        plt.fill_between(forecast_ma.index, forecast_ma - 1.645*forecast_std,
                         forecast_ma + 1.645*forecast_std, color='gray',
                         alpha=0.2)

        if save:
            plt.savefig(self.output_dir + 'images/forecast_plot.png')

    def date_to_trigger(self, moving_average=5, save=False):
        """
        """

        t = 0
        ma = moving_average + 1
        while ma >= moving_average:
            t += 1
            ma = self.model(t)[0]

        date = (self.data.index[0] + pd.Timedelta(t, 'days')).strftime('%d-%m-%Y')

        if save:
            with open(self.output_dir + 'date_to_trigger.csv', 'w') as f:
                f.write(f'Moving average,{moving_average}\n')
                f.write(f'Date,{date}\n')

        return date

df = CoronaStats('./../data/net_cases.csv', 0.1)
df.date_to_trigger()

# df._moving_average()

# df.rrp().plot()

# df.plot()
