import matplotlib.pyplot as plt
from classes.statistics.Statistics import Statistics
import numpy as np

x = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 7]
x = np.array(x)

possible_answers = len(set(x))
plt.hist(x, bins=np.arange(min(x), max(x)+2, 1)-0.5, ec="k")
plt.show()

summary_statistics = Statistics.getSummaryStatistics({"values": x})
print(summary_statistics)

x = [1, 7, 6, 3, 1, 3, 4, 2, 4, 4, 5, 3, 5, 1, 6, 7]
x = np.array(x)

possible_answers = len(set(x))
plt.hist(x, bins=np.arange(min(x), max(x)+2, 1)-0.5, ec="k")
plt.show()

summary_statistics = Statistics.getSummaryStatistics({"values": x})
print(summary_statistics)
