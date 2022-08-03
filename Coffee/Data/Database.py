# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

"""正如历史总是要进入教科书，数据也是需要'永久'保存。"""


from influxdb import InfluxDBClient
from datetime import timedelta
from Coffee.Core.Settings import DEF_CFG


class TimeSeriesDatabase:
    def connect(self):
        """
        connect to DB
        """
        pass

    def disconnect(self):
        """
        disconnect to DB
        """
        pass

    def insert(self, fields, table, tags, dt):
        """
        insert data to DB
        """
        pass

    def select(self, fields, table, tags, time_range, filters=''):
        """
        fetch data from DB
        """
        pass

    def finish(self):
        """
        force update immediately
        """
        pass


class InfluxDBV1(TimeSeriesDatabase):
    def __init__(self,
                 host='localhost',
                 port=8086,
                 username='root',
                 password='root',
                 database=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

        self.batch_size = 1000
        self.batch_record = []

        self.client = None

    def connect(self):
        if self.client:
            return True
        self.client = InfluxDBClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database
        )
        return True if self.client else False

    def disconnect(self):
        self.finish()
        self.client = None

    def insert(self, fields, table, tags, dt):
        """
        fields and tags should be key-value pair
        """
        pt = {
            "measurement": table,
            "time": dt + timedelta(hours=-8),
            "tags": tags,
            "fields": fields
        }
        self.batch_record.append(pt)

        if len(self.batch_record) > self.batch_size:
            self.finish()

    def select(self, fields, table, tags, time_range, filters=''):
        if not self.client:
            return None

        if type(fields) == str:
            fields = [fields, ]
        if not fields:
            return None

        tags_str = ' and '.join(['='.join([k, "'"+str(v)+"'"]) for k, v in tags.items()])
        time_range = time_range.get_selector()
        pts = self.client.query(
            "select {} from {} where source='{}' {} {}".format(
                ','.join(fields), table, tags_str,
                '' if not time_range else ' and ' + time_range,
                ' and ' + filters if filters else ''
            )
        ).get_points()
        return pts

    def finish(self):
        if len(self.batch_record) > 0:
            if self.client:
                self.client.write_points(self.batch_record, batch_size=self.batch_size)
            self.batch_record = []


DEF_TSDB = InfluxDBV1(DEF_CFG.influxdb_host, DEF_CFG.influxdb_port, DEF_CFG.influxdb_username, DEF_CFG.influxdb_password,
                      DEF_CFG.influxdb_database)
DEF_TSDB.connect()
