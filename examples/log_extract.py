import pandas as pd
import matplotlib.pyplot as plt

from coffee.data import DataPoint, DataAggregator, RegexPattern
from coffee.logkit import LogFileDataLoader

class DataAggregator1(DataAggregator):
    def on_data(self, datapoint: DataPoint) -> DataPoint:
        value = datapoint.value
        value['datetime'] = datapoint.timestamp
        self.all_points.append(value)
        return datapoint


agg = DataAggregator1()


LogFileDataLoader("simple.log").add_pattern(
    RegexPattern(name="a_pattern",
                 pattern=r'(\d+),(\d+)',
                 fields={
                     'a': int,
                     'b': int,
                 },
                 tags=[('a', 'A')],
                 version='1.0')
).add_sink(agg).start()

df = pd.DataFrame(agg.all_points)
print(df)
df.plot(x='datetime', y=['a', 'b'], kind='line')
plt.show()
