# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.
import abc
from abc import ABC
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DataPoint:
    """
    represent a single data record
    """
    # type of this datapoint
    name: str
    # timestamp of this datapoint
    timestamp: datetime
    # data values in key-value format
    value: dict
    # which keys should be a tag
    tags: list
    # meta data of this datapoint
    meta: dict

    def timestamp_ms(self) -> int:
        return int(self.timestamp.timestamp() * 1000)

    def timestamp_s(self) -> int:
        return int(self.timestamp.timestamp())

    @staticmethod
    def make_meta_datapoint(meta):
        return DataPoint("", datetime.now(), {}, [], meta)


class DataSink(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_data(self, datapoint: DataPoint) -> DataPoint:
        """
        Input source data to sink.

        :param datapoint: data
        """
        pass

    @abc.abstractmethod
    def finish(self, datapoint: DataPoint) -> DataPoint:
        """
        No data anymore. This is the last call for processing data.

        :param datapoint: data
        """
        pass


class DataSource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add_sink(self, sink: DataSink):
        """
        Add data consumer to the data source.

        :param sink: data consumer to consume the output data.
        """
        pass

    @abc.abstractmethod
    def start(self):
        """
        Bootstrap the data generator.
        """
        pass


class DataLoader(DataSource, DataSink, ABC):
    """
    Load data from some source, and feed datapoints to all sinks.
    """
    def __init__(self):
        self.sinks = []

    def add_sink(self, sink: DataSink):
        self.sinks.append(sink)
        return self

    def start(self):
        pass

    def on_data(self, datapoint: DataPoint) -> DataPoint:
        for s in self.sinks:
            datapoint = s.on_data(datapoint)
        return datapoint

    def finish(self, datapoint: DataPoint) -> DataPoint:
        for s in self.sinks:
            datapoint = s.finish(datapoint)
        return datapoint
