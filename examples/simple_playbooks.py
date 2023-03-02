# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

from coffee.core.playbook import Playbook
from coffee.core.settings import DEF_CFG
from coffee.data import (
    PatternGroupBuilder, DEFAULT_TS_PATTERNS, RegexPattern, GrafanaDashboardBuilder, influxdb_ts_sql,
    DatapointTimeTracker, LogFileDataLoader, InfluxDBDataSink, DEF_TSDB, PatternMatchReporter
)
import webbrowser


class SimplePlaybook(Playbook):
    def __init__(self, log: str = ''):
        self.log = log

        # definition for extracting data from file
        self.pattern_group = PatternGroupBuilder(
            "simple"
        ).set_ts_patterns(
            DEFAULT_TS_PATTERNS
        ).add_pattern(
            RegexPattern(
                name="b_pattern",
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
            name="filter_a", label='A filter'
        ).add_influx_ts_panel(
            title='show data b',
            source=DEF_CFG.grafana_influxdb_source,
            influx_query_list=[
                # just show b and filter with A
                influxdb_ts_sql(''' select first("b") as "B" from b_pattern where ("A" =~ /^$filter_a$/) ''')
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
        LogFileDataLoader(self.log).set_pattern_group(self.pattern_group).add_sink(
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


if __name__ == '__main__':
    SimplePlaybook('simple.log').prepare().play()

