# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.
import webbrowser
from grafanalib.core import TimeSeries
from coffee.core.playbook import Playbook
from coffee.core.settings import DEF_CFG
from coffee.data import (
    PatternGroupBuilder, DEFAULT_TS_PATTERNS, RegexPattern, GrafanaDashboardBuilder,
    InfluxDBDataSink, DEF_TSDB,
    InfluxDBTarget, InfluxQLBuilder, grafana_var
)
from coffee.logkit import LogFileDataLoader


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
        )
        self.dashboard.add_text_variable(name="filter_a", label='A filter')
        self.dashboard.add_panel(TimeSeries(
            title='show data b',
            dataSource=DEF_CFG.grafana_influxdb_source,
            targets=[
                InfluxDBTarget(query=InfluxQLBuilder('b_pattern').select(
                    'b', alias='B'
                ).where(tag_filters={'A': grafana_var('filter_a')}).build_ts())
            ]
        ))
        self.dashboard.build(True)

    def prepare(self):
        # create or update grafana dashboard
        # you should call this at least once
        self.dashboard.update_dashboard(DEF_CFG.grafana_url, DEF_CFG.grafana_key)
        return self

    def play(self):
        # extract data from log, the log should have the format:
        # datetime-pattern data_a, data_b, for example
        loader = LogFileDataLoader(
            self.log,
            show_progress=True,
            show_match_result=True
        ).set_pattern_group(
            self.pattern_group
        ).add_sink(
            # upload data to influxdb
            InfluxDBDataSink(DEF_TSDB)
        )
        loader.start()
        
        #  self.dashboard.update_dashboard(DEF_CFG.grafana_url, DEF_CFG.grafana_key)
        
        # open a new grafana page to show data
        webbrowser.open(self.dashboard.full_url(DEF_CFG.grafana_url,
                                                vars={},
                                                dt_from=loader.time_tracker.min_ts,
                                                dt_to=loader.time_tracker.max_ts)
                        )


if __name__ == '__main__':
    SimplePlaybook('simple.log').prepare().play()

