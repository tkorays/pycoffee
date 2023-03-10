# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.
"""
道生一，一生二，二生三，三生万物。
万物负阴而抱阳，冲气以为和。
"""

import io
import os
import re
from datetime import datetime

from rich.console import Console
from rich.progress import Progress
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from coffee.data import (
    RegexPattern, PatternGroupBuilder, PatternGroup, DataPoint, DataLoader,
    PatternMatchReporter, DatapointTimeTracker, DataSink
)
from coffee.core.utils import merge_datetime
from coffee.logkit.utils.logtail import LogTail


class LineSink:
    """
    sink for processing lines one by one
    """
    def on_line(self, filename: str, line: str):
        pass


class LogWatchHandler(FileSystemEventHandler):
    """
    handle system event
    """
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
            self.log_tails[event.src_path] = LogTail(event.src_path, sleep_interval=1, only_new=self.only_new)

        while True:
            line = self.log_tails[event.src_path].nextline()
            if line is not None:
                self.line_sink.on_line(event.src_path, line)
            else:
                break

    def on_created(self, event):
        pass


class LogFileDataLoader(DataLoader, PatternGroupBuilder, LineSink):
    """
    extract data from log.

    example for live loading:
    ```python
    LogFileDataLoader(
        path='../../core/',
        live_watch=r'.*\.log',
        show_progress=True,
        only_new=False
    ).set_pattern_group(group).start()
    ```

    example for offline loading:
    ```python
    LogFileDataLoader(
        path='../../core/abc.log',
        live_watch='',
        show_progress=True,
        only_new=False
    ).set_pattern_group(group).start()
    ```
    """
    def __init__(self,
                 path: str,
                 live_watch: str = '',
                 base_datetime: datetime = datetime.now(),
                 show_progress: bool = False,
                 show_match_result: bool = False,
                 custom_time_tracker: DataSink = None,
                 only_new: bool = False):
        DataLoader.__init__(self)
        PatternGroupBuilder.__init__(self)
        LineSink.__init__(self)

        self.path = os.path.abspath(path)
        self.base_datetime = base_datetime
        self.show_progress = show_progress
        if show_match_result:
            self.add_sink(PatternMatchReporter())
        if live_watch:
            self.event_handler = LogWatchHandler(live_watch, self, only_new)
        else:
            self.event_handler = None
        self.observer = PollingObserver()
        self.prev_datetime = None

        if not custom_time_tracker:
            self.time_tracker = DatapointTimeTracker()
        else:
            self.time_tracker = custom_time_tracker
        self.add_sink(self.time_tracker)
        self.set_ts_patterns(DEFAULT_TS_PATTERNS)

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
            dt = merge_datetime(self.base_datetime, ts)
            self.prev_datetime = dt

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
        if self.event_handler:
            self.observer.schedule(self.event_handler, self.path)
            self.observer.start()
            print('watching...')
            try:
                while self.observer.is_alive():
                    pass
            finally:
                self.observer.stop()
                self.observer.join()
        else:
            # get lines of this log
            lines = 0
            for _, _ in enumerate(io.open(self.path, encoding='utf-8', errors='ignore')):
                lines += 1
            with io.open(self.path, encoding='utf-8', errors='ignore') as f, \
                    Progress(console=Console(stderr=True)) as progress:
                if self.show_progress:
                    task = progress.add_task("Parsing...", total=lines)
                while True:
                    if self.show_progress:
                        progress.update(task, advance=1)

                    line = f.readline()
                    if not line:
                        break

                    self.on_line("", line)

        dp = DataPoint.make_meta_datapoint({})
        dp = self.finish(dp)
        return dp


if __name__ == '__main__':
    from coffee.data import DEFAULT_TS_PATTERNS, DataSink

    class DetailDataSink(DataSink):
        def on_data(self, datapoint: DataPoint) -> DataPoint:
            print(datapoint.value)
            return datapoint

        def finish(self, datapoint: DataPoint) -> DataPoint:
            return datapoint


    # r'.*\.log'
    LogFileDataLoader(
        path='../core/abc.log',
        live_watch=r'',
        show_progress=True,
        show_match_result=True,
        only_new=False
    ).set_ts_patterns(DEFAULT_TS_PATTERNS).add_pattern(
        RegexPattern(name="a_pattern",
                     pattern=r'(\d+),(\d+)',
                     fields={
                        'a': int,
                        'b': int,
                     },
                     tags=[('a', 'A')],
                     version='1.0')
    ).add_sink(DetailDataSink()).start()
