# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

from Coffee.Core.Playbook import Playbook
from Coffee.Core.Settings import DEF_CFG
from Coffee.Data import *
import webbrowser


class SimplePlaybook(Playbook):
    """
    usage:

        ```python
        SimplePlaybook("1.log").prepare().play()
        ```

    then coffee will:
    * auto generate a dashboard for displaying data
    * extract data from log
    * upload data to influxdb
    * print match result in the console
    * open grafana webpage to show timeseries data
    """
    def __init__(self, log: str = ''):
        self.log = log

        # definition for extracting data from file
        self.pattern_group = PatternGroupBuilder(
            "simple"
        ).set_ts_patterns(
            DEFAULT_TS_PATTERNS
        ).add_pattern(
            RegexPattern(
                name="a_pattern",
                pattern=r'(\d+),(\d+)',
                fields={
                    'a': int,
                    'b': int,
                },
                tags=[('a', 'A')],
                version='1.0'
            )
        ).build()

        # how to create a dashboard in grafana
        self.dashboard = GrafanaDashboardBuilder(
            title='a_dashboard',
            uid='a_dashboard',
            description='description of this dashboard',
            tags=['example']
        ).add_text_variable(
            name='A', label='A filter'
        ).add_influx_ts_panel(
            title='show data b',
            source=DEF_CFG.grafana_influxdb_source,
            influx_query_list=[
                # just show b and filter with A
                InfluxdbQueryBuilder('a_pattern').query_list(['b']).build(tags=['A'])
            ]
        ).build()

        self.time_tracker = DatapointTimeTracker()

    def prepare(self):
        # create or update grafana dashboard
        # you should call this at least once
        self.dashboard.update_dashboard(DEF_CFG.grafana_url, DEF_CFG.grafana_key)
        return self

    def play(self):
        # extract data from log, the log should have the format:
        # datetime-pattern data_a, data_b, for example
        """
        2022-08-13 12:00:00.000 1234,1
        2022-08-13 12:00:02.000 1234,3
        2022-08-13 12:00:04.000 1234,6
        2022-08-13 12:00:08.000 1234,0
        """
        LogFileDataLoader(self.log, self.pattern_group).add_sink(
            # upload data to influxdb
            InfluxDBDataSink(DEF_TSDB)
        ).add_sink(
            # show regex match result
            PatternMatchReporter()
        ).add_sink(
            # to track min max time
            self.time_tracker
        ).start()
        
        #  self.dashboard.update_dashboard(DEF_CFG.grafana_url, DEF_CFG.grafana_key)
        
        # open a new grafana page to show data
        webbrowser.open(self.dashboard.full_url(DEF_CFG.grafana_url,
                                                vars={},
                                                dt_from=self.time_tracker.min_ts,
                                                dt_to=self.time_tracker.max_ts)
                        )
        # then this page is open
        # http://127.0.0.1:3000/d/a_dashboard/a_dashboard?orgId=1&from=1660276800000&to=1660276808000
        # but now data will be displayed because the tag 'A' is not provided
        # when you fill the A filter with `1234`
        # you will see the data
        # http://127.0.0.1:3000/d/a_dashboard/a_dashboard?orgId=1&from=1660276800000&to=1660276808000&var-A=1234
        

if __name__ == '__main__':
    SimplePlaybook('1.log').prepare().play()

