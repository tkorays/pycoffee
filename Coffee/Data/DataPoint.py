from datetime import datetime


class DataPoint:
    def __init__(self, name: str, timestamp: datetime, value: dict, tags: list, meta=dict):
        """
        init a datapoint

        :param name: name of this datapoint
        :param timestamp: timestamp of this datapoint
        :param value: datapoint value
        :param tags: for search filter when value is a dict type.
        :param meta: some metadata
        """
        self.name = name
        self.timestamp = timestamp
        self.value = value
        self.tags = tags
        self.meta = meta

    def timestamp_ms(self) -> int:
        return int(self.timestamp.timestamp() * 1000)

    def timestamp_s(self) -> float:
        return self.timestamp.timestamp()

    @staticmethod
    def make_meta_datapoint(meta):
        return DataPoint("", datetime.now(), {}, [], meta)
