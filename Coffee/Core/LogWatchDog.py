from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from Coffee.Core.LogTail import LogTail
from Coffee.Core.Utils import merge_datetime
from Coffee.Data import (
    PatternGroupBuilder, PatternGroup, RegexPattern
)
from Data import DataLoader
from Coffee.Data.DataFlow import DataPoint, DataSink
from datetime import datetime
import re
import os


class LineSink:
    def on_line(self, filename: str, line: str):
        pass


class LogWatchHandler(FileSystemEventHandler):
    def __init__(self, pattern: str, line_sink: LineSink, only_new: bool = False):
        super().__init__()

        self.pattern = pattern
        self.line_sink = line_sink
        self.only_new = only_new
        self.log_tails = {}

    def on_modified(self, event):
        if not re.match(self.pattern, event.src_path):
            return
        if event.src_path not in self.log_tails.keys():
            self.log_tails[event.src_path] = LogTail(event.src_path, only_new=self.only_new)

        while True:
            line = self.log_tails[event.src_path].nextline()
            if line is not None:
                self.line_sink.on_line(event.src_path, line)
            else:
                break

    def on_created(self, event):
        pass


class LogWatchDog(DataLoader, PatternGroupBuilder, LineSink):
    """
    watch single type log and extract data.
    """
    def __init__(self, path: str, pattern: str, only_new: bool = False):
        super().__init__()
        PatternGroupBuilder.__init__(self)
        LineSink.__init__(self)

        self.path = os.path.abspath(path)
        self.pattern = pattern
        self.event_handler = LogWatchHandler(self.pattern, self, only_new)
        self.observer = PollingObserver()

        self.prev_datetime = None

    def set_pattern_group(self, group: PatternGroup):
        self.pattern_group = group
        return self

    def on_line(self, filename: str, line: str):
        # print(f'{filename} : {line}')
        if not line:
            dp = DataPoint.make_meta_datapoint({})
            dp = self.finish(dp)
            return dp

        # timestamp pattern in logs
        PTS = self.pattern_group.get_ts_patterns()
        # data pattern in logs
        PDT = self.pattern_group.get_patterns()

        # try to get date in log path
        # some logs don't have year/moth/day info
        try:
            dff = RegexPattern("", r'(\d+)-(\d+)-(\d+)', {'year': int, 'month': int, 'day': int}).match(filename)
            base_datetime = merge_datetime(datetime.utcnow(), dff) if dff else datetime.utcnow()
        except ValueError:
            base_datetime = datetime.utcnow()

        # match time
        ts = None
        for t in PTS:
            ts = t.match(line)
            # early break when find ts
            if ts:
                break

        if not ts:
            if not self.prev_datetime:
                return
            dt = self.prev_datetime
        else:
            dt = merge_datetime(base_datetime, ts)
            prev_datetime = dt

        for p in PDT:
            # match data
            r = p.match(line)
            if not r:
                continue

            dp = DataPoint(
                name=p.get_name(),
                timestamp=dt,
                value=r,
                tags=p.get_tags(),
                meta={
                    'name': p.get_name(),
                    'id': p.get_unique_id(),
                    'tags': p.get_tags(),
                }
            )
            dp = self.on_data(dp)

    def start(self):
        self.observer.schedule(self.event_handler, self.path)
        self.observer.start()
        print('watching...')
        try:
            while self.observer.is_alive():
                pass
        finally:
            self.observer.stop()
            self.observer.join()


if __name__ == '__main__':
    from Coffee.Data import DEFAULT_TS_PATTERNS

    class DetailDataSink(DataSink):
        def on_data(self, datapoint: DataPoint) -> DataPoint:
            print(datapoint.value)
            return datapoint

        def finish(self, datapoint: DataPoint) -> DataPoint:
            return datapoint


    LogWatchDog('./', r'.*\.log', only_new=True).set_ts_patterns(DEFAULT_TS_PATTERNS).add_pattern(
        RegexPattern(name="a_pattern",
                     pattern=r'(\d+),(\d+)',
                     fields={
                        'a': int,
                        'b': int,
                     },
                     tags=[('a', 'A')],
                     version='1.0')
    ).add_sink(DetailDataSink()).start()
