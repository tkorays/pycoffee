# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

"""
this file provides some data processors:
* bypass processor
* influxdb processor
* time tracker
* data aggregator
"""

from Coffee.Data.DataFlow import DataPoint
from Coffee.Data.Database import InfluxDBV1
from Coffee.Core.Utils import randstr
from Coffee.Data.DataFlow import DataSink

from datetime import datetime, timedelta


class BypassDataSink(DataSink):
    def on_data(self, datapoint: DataPoint) -> DataPoint:
        return datapoint

    def finish(self, datapoint: DataPoint) -> DataPoint:
        return datapoint


class InfluxDBDataSink(DataSink):
    """
    track the min and max time for range selection.
    """
    def __init__(self, influx: InfluxDBV1, source=''):
        super().__init__()
        self.influx = influx
        self.source_id = randstr(10) if not source else source

    def on_data(self, datapoint: DataPoint) -> DataPoint:
        tags_kv = {
            'source': self.source_id
        }
        for tag in datapoint.tags:
            if tag[0] in datapoint.value.keys():
                tags_kv[tag[1]] = datapoint.value[tag[0]]
        self.influx.insert(
            fields=datapoint.value,
            table=datapoint.name,
            tags=tags_kv,
            dt=datapoint.timestamp
        )

        datapoint.meta['_source'] = self.source_id
        return datapoint

    def finish(self, datapoint: DataPoint) -> DataPoint:
        self.influx.finish()
        return datapoint


class DatapointTimeTracker(DataSink):
    def __init__(self):
        super().__init__()
        self.min_ts = 18446744073709551615
        self.max_ts = 0

    def on_data(self, datapoint: DataPoint) -> DataPoint:
        self.min_ts = datapoint.timestamp_ms() if datapoint.timestamp_ms() < self.min_ts else self.min_ts
        self.max_ts = datapoint.timestamp_ms() if datapoint.timestamp_ms() > self.max_ts else self.max_ts
        return datapoint

    def finish(self, datapoint: DataPoint) -> DataPoint:
        return datapoint

    def get_min_ts(self) -> datetime:
        # reserve 60s offset for better display
        return datetime.fromtimestamp(self.min_ts / 1000) - timedelta(seconds=60)

    def get_max_ts(self) -> datetime:
        # reserve 60s offset for better display
        return datetime.fromtimestamp(self.max_ts / 1000) + timedelta(seconds=60)


class DataAggregator(DataSink):
    """
    aggregate all points in an object, don't process one by one
    """

    def __init__(self, append_timestamp: bool = False):
        super(DataAggregator, self).__init__()
        self.all_points = []
        self.append_timestamp = append_timestamp

    def on_data(self, datapoint: DataPoint) -> DataPoint:
        value = datapoint.value
        value['timestamp'] = datapoint.timestamp
        self.all_points.append(value)
        return datapoint

    def finish(self, datapoint: DataPoint) -> DataPoint:
        return datapoint

    def points(self):
        return self.all_points
