# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

from datetime import datetime
from dataclasses import dataclass


@dataclass
class DataPoint:
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
