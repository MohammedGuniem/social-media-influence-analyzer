import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math


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

    def line_plot(x, y, xlabel="", ylabel="", legend=""):
        x = np.array(x)
        y = np.array(y)
        plt.plot(x, y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xlim(min(x), max(x))
        plt.ylim(min(y), max(y))
        plt.show()

    def subplot_histograms(data):
        number_of_histograms = len(data.keys())
        number_of_rows = 4
        number_of_columns = math.ceil(number_of_histograms/number_of_rows)

        fig, axs = plt.subplots(number_of_rows, number_of_columns,
                                sharey=True, tight_layout=True)
        row_number = 0
        column_number = 0
        for key, value in data.items():
            x = np.array(value)
            possible_answers = len(set(x))
            axs[row_number, column_number].hist(x, bins=np.arange(
                min(x), max(x)+2, 1)-0.5, ec="k")
            axs[row_number, column_number].set_title(key)

            if column_number == (number_of_columns-1):
                column_number = 0
                row_number += 1
            else:
                column_number += 1

        plt.show()
