import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class Statistics:
    def getSummaryStatistics(data_dict):
        df = pd.DataFrame(data_dict)

        # Rename '50%' percentile to '50% - median' since it is the same.
        summary_statistics = df.describe(
            percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).rename(index={'50%': '50% - median'})

        # Calculate mode and append to statistics dataframe.
        mode_statistics = df.mode().rename(index={0: 'mode'}).iloc[0]
        summary_statistics = summary_statistics.append(mode_statistics)

        # Calculate variance and append to statistics dataframe.
        var_statistics = pd.DataFrame(
            df.var()).transpose().rename(index={0: 'var'})
        summary_statistics = summary_statistics.append(var_statistics)

        return summary_statistics

    def plot(x, y, xlabel="", ylabel="", legend=""):
        x = np.array(x)
        y = np.array(y)
        plt.scatter(x, y, label="")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if legend:
            plt.legend(loc=legend)
        plt.show()
