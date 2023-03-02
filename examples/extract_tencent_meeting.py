import pandas as pd
import matplotlib.pyplot as plt
import os
from coffee.data import (
    DataAggregator, LogFileDataLoader, RegexPattern
)

agg = DataAggregator(append_timestamp=True)

LogFileDataLoader(
    os.path.join(os.path.expanduser('~'),
                 'Library/Containers/com.tencent.meeting/Data/Library/Global/Logs/xcast_2022110620.log')
).add_ts_pattern(
    RegexPattern('', r'(\d+):(\d+):(\d+)\.(\d\d\d)', {
        'hour': int, 'minute': int, 'second': int, 'millisecond': int
    })
).add_pattern(
    RegexPattern(
        name='Tencent_Sys_Info',
        pattern=r'Sys\[CPU:([\d\.]+)%\(App\) ([\d\.]+)%\(Sys\) '
        r'.*CpuLevel:(\d+)\]',
        fields={'app': float, 'sys': float, 'cpu_level': int}
    )
).add_sink(agg).start()

df = pd.DataFrame(agg.all_points)
print(df)
df.plot(x='timestamp', y=['app', 'sys', 'cpu_level'], kind='line')
plt.show()
