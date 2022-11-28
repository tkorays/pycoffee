# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

"""
道生一，一生二，二生三，三生万物。
万物负阴而抱阳，冲气以为和。
"""
from datetime import datetime
from rich.console import Console
from rich.progress import Progress
import io

from Coffee.Data.DataExtractor import RegexPattern, PatternGroupBuilder
from Coffee.Core.Utils import merge_datetime
from Coffee.Data.DataExtractor import PatternGroup
from Coffee.Data.DataFlow import DataPoint, DataLoader


class LogFileDataLoader(DataLoader, PatternGroupBuilder):
    def __init__(self, log_path: str):
        DataLoader.__init__(self)
        PatternGroupBuilder.__init__(self)
        self.log_path = log_path

    def set_pattern_group(self, group: PatternGroup):
        self.pattern_group = group
        return self

    def start(self):
        # timestamp pattern in logs
        PTS = self.pattern_group.get_ts_patterns()
        # data pattern in logs
        PDT = self.pattern_group.get_patterns()

        # try to get date in log path
        # some logs don't have year/moth/day info
        try:
            dff = RegexPattern("", r'(\d+)-(\d+)-(\d+)', {'year': int, 'month': int, 'day': int}).match(self.log_path)
            base_datetime = merge_datetime(datetime.utcnow(), dff) if dff else datetime.utcnow()
        except ValueError:
            base_datetime = datetime.utcnow()

        prev_datetime = None

        # get lines of this log
        lines = 0
        for _, _ in enumerate(io.open(self.log_path, encoding='utf-8', errors='ignore')):
            lines += 1

        with io.open(self.log_path, encoding='utf-8', errors='ignore') as f, \
                Progress(console=Console(stderr=True)) as progress:

            task = progress.add_task("Parsing...", total=lines)

            while True:
                progress.update(task, advance=1)

                line = f.readline()
                if not line:
                    break

                # match time
                ts = None
                for t in PTS:
                    ts = t.match(line)
                    # early break when find ts
                    if ts:
                        break

                if not ts:
                    if not prev_datetime:
                        continue
                    dt = prev_datetime
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

        dp = DataPoint.make_meta_datapoint({})
        dp = self.finish(dp)
        return dp
