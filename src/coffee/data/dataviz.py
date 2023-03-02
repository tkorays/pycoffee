# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

from grafanalib.core import (
    Dashboard, Template, Templating, RowPanel, GridPos, TimeSeries, DEFAULT_TIME_PICKER, Table, Panel)
from grafanalib._gen import DashboardEncoder
from grafanalib.influxdb import InfluxDBTarget
import json
import requests


def influxdb_ts_sql(sql, interval: str = '1s', fill: str = 'none'):
    """
    query timeseries data with influx SQL.

    demo:
    select first("a") as "alia_A", first("b") from "measurement_123" where ("tagA" =~ /$grafana_value$/ and "tagB" = 1)

    we will add `time filter` and `group by`. If you want to query non ts data, just use raw SQL.
    """
    return f'{sql} AND $timeFilter GROUP BY time({interval}) fill({fill})'


def add_influxdb_source():
    "http://{server_addr}/api/datasources"
    pass

# InfluxQL aggregator, selector and transformer.
# see https://docs.influxdata.com/influxdb/v1.8/query_language/
InfluxQL_Aggregators = ['', 'count', 'distinct', 'integral', 'mean', 'median', 'mode', 'spread', 'stddev', 'sum']
InfluxQL_Selectors = ['', 'bottom', 'first', 'last', 'max', 'max', 'percentile', 'sample', 'top']
InfluxQL_Transformers = ['', 'abs', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos',
                         'cumulative_sum', 'derivative', 'difference', 'elapsed', 'exp',
                         'floor', 'histogram', 'ln', 'log', 'log2', 'log10', 'moving_average',
                         'non_negative_derivative', 'non_negative_difference',
                         'pow', 'round', 'sin', 'sqrt', 'tan']


def grafana_var(var_name):
    """
    `grafana_var` is used in `InfluxQLBuilder`
    """
    return f'~/^${var_name}$/'


class InfluxQLBuilder:
    """
        see all features at:
        https://docs.influxdata.com/influxdb/v1.8/query_language/
        """

    def __init__(self, measurement):
        self.fields = []
        self.measurement = measurement
        self.filters = {}
        self.tag_filters = {}
        self.custom_filters = {}
        self.interval = '1s'
        self.fill_with = 'none'

    def simple_select_list(self, select_list: list):
        for v in select_list:
            self.fields.append(f'"{v}"')
        return self

    def first_select_list(self, select_list: list):
        for v in select_list:
            self.fields.append(f'first("{v}")')
        return self

    def custom_select_list(self, select_list: list):
        for v in select_list:
            self.fields.append(v)
        return self

    def select(self, field_key: str,
               alias: str = '',
               selector: str = 'first',
               aggregator: str = '',
               transformer: str = ''):
        if selector not in InfluxQL_Selectors:
            print(f'bad selector {selector}')
            selector = 'first'
        if aggregator not in InfluxQL_Aggregators:
            print(f'bad aggregator {aggregator}')
            aggregator = ''
        if transformer not in InfluxQL_Transformers:
            print(f'bad transformer {transformer}')
            transformer = ''

        alias = alias if alias else field_key
        field_key = f'"{field_key}"'
        if selector:
            field_key = f'{selector}({field_key})'
        if aggregator:
            field_key = f'{aggregator}({field_key})'
        if transformer:
            field_key = f'{transformer}({field_key})'
        if alias:
            field_key = f'{field_key} AS "{alias}"'
        self.fields.append(field_key)
        return self

    def where(self, filters: dict = {}, tag_filters: dict = {}):
        if not tag_filters and not filters:
            raise Exception("filters should be specified!")
        self.filters = filters
        self.tag_filters = tag_filters
        return self

    def group_by(self, interval='1s'):
        self.interval = interval
        return self

    def fill(self, fill='none'):
        self.fill_with = fill
        return self

    def build_ts(self):
        sql = self.build_normal() + f' AND $timeFilter GROUP BY time({self.interval}) fill({self.fill_with})'
        return sql

    def build_normal(self):
        sql = f'SELECT ' + ','.join(self.fields) + f' FROM "{self.measurement}" WHERE '
        sql1 = ' AND '.join([f'"{k}"="{v}"' if type(v) is str and not v.startswith('~') else f'"{k}"={v}'
                             for k, v in self.filters.items()])
        sql += sql1
        sql2 = ' AND '.join([f'"{k}"=\'{v}\'' if type(v) is str and not v.startswith('~') else f'"{k}"={v}'
                             for k, v in self.tag_filters.items()])
        sql = sql + ' AND ' + sql2 if sql1 else sql + sql2
        sql = sql + ' AND $timeFilter'
        return sql


class DashboardBuilder:
    def add_text_variable(self, name: str, label: str, default: str = ''):
        pass

    def add_row_panel(self, title: str, collapsed=False):
        pass

    def build(self):
        pass


class GrafanaDashboardBuilder:
    """
    Utils class for creating dashboard for grafana.
    """
    def __init__(self, title: str, uid: str, description: str, tags: list):
        self.title = title
        self.uid = uid
        self.description = description
        self.tags = tags
        self.templates = []
        self.panels = []
        self.cur_x = 0
        self.cur_y = 0
        self.dashboard = None

    def add_text_variable(self, name: str, label: str, default: str = ''):
        self.templates.append(Template(
            name=name,
            default=default,
            query='',
            label=label,
            type='textbox'
        ))
        return self

    def add_query_variable(self, name: str, label: str, query: str, datasource: str):
        self.templates.append(Template(
            name=name,
            default='',
            query=query,
            label=label,
            type='query',
            includeAll=True,
            multi=True,
            dataSource=datasource
        ))
        return self

    def add_panel(self, panel: Panel, comment: str = ''):
        """
        add a grafana dashboard by pure grafanalib
        """
        if not isinstance(panel, Panel):
            raise Exception(f'expect a panel, but you pass `{panel}`')
        pos = GridPos(h=8, w=24, x=self.cur_x, y=self.cur_y) if not panel.gridPos else\
            GridPos(h=panel.gridPos.h, w=panel.gridPos.w, x=self.cur_x, y=self.cur_y)
        # enter a new row
        if self.cur_x + pos.w > 24:
            self.cur_x = 0
            self.cur_y += 1
            pos = GridPos(h=pos.h, w=pos.w, x=self.cur_x, y=self.cur_y)
        panel.gridPos = pos
        self.panels.append(panel)
        self.cur_x += panel.gridPos.w
        if self.cur_x >= 24:
            self.cur_x = 0
            self.cur_y += 1
        return self

    def add_row_panel(self, title: str, collapsed=False):
        self.panels.append(RowPanel(title=title, collapsed=collapsed,
                                    gridPos=GridPos(h=1, w=24, x=self.cur_x, y=self.cur_y)))
        self.cur_x = 0
        self.cur_y += 1
        return self

    def add_influx_ts_panel(self, title: str, source: str, influx_query_list: list, height=8):
        self.panels.append(TimeSeries(
            title=title,
            dataSource=source,
            targets=[
                InfluxDBTarget(query=x, format='time_series') for x in influx_query_list
            ],
            showPoints='always',
            interval='1ms',
            tooltipMode='multi',
            gridPos=GridPos(h=height, w=24, x=self.cur_x, y=self.cur_y)
        ))
        self.cur_x = 0
        self.cur_y += height
        return self

    def add_influx_table_panel(self, title: str, source: str, influx_query_list, overrides=[]):
        self.panels.append(Table(
            title=title,
            dataSource=source,
            targets=[
                InfluxDBTarget(query=x, format='table') for x in influx_query_list
            ],
            overrides=overrides,
            filterable=True,
            align='auto',
            displayMode='color-background-solid',
            colorMode='continuous-BlPu',
            gridPos=GridPos(h=8, w=24, x=self.cur_x, y=self.cur_y)
        ))
        self.cur_x = 0
        self.cur_y += 8
        return self

    def build(self, crosshair=False):
        self.dashboard = Dashboard(
            title=self.title,
            uid=self.uid,
            description=self.description,
            tags=self.tags,
            timezone='browser',
            timePicker=DEFAULT_TIME_PICKER,
            editable=True,
            templating=Templating(list=self.templates),
            panels=self.panels,
            sharedCrosshair=crosshair
        )
        return self

    def update_dashboard(self, server_addr: str, api_key: str):
        dashboard_json = json.dumps({
            "dashboard": self.dashboard.to_json_data(),
            "overwrite": True,
            "message": 'update dashboard'
        }, sort_keys=True, indent=2, cls=DashboardEncoder)

        headers = {'Authorization': f"Bearer {api_key}", 'Content-Type': 'application/json'}
        r = requests.post(f"http://{server_addr}/api/dashboards/db", data=dashboard_json, headers=headers, verify=True)
        if r.status_code != 200:
            return None
        # print(f"{r.status_code} - {r.content}")
        result = json.loads(r.content)
        if result['status'] != 'success':
            return None
        return f'http://{server_addr}{result["url"]}'

    def url(self, server_addr: str):
        return f'http://{server_addr}/d/{self.title}/{self.uid.lower()}'

    def full_url(self, server_addr: str, vars: dict, dt_from: int, dt_to: int):
        v = '&'.join([f'var-{k}={v}' for k, v in vars.items()])
        return f'{self.url(server_addr)}?orgId=1&{v}&from={dt_from}&to={dt_to}'

    @staticmethod
    def override_hide_field(field):
        return {
            "matcher": {
              "id": "byName",
              "options": field
            },
            "properties": [
              {
                "id": "custom.hidden",
                "value": True
              }
            ]
          }

    @staticmethod
    def overrides_display_link(link_name, override_field, link_field):
        return {
            "matcher": {
              "id": "byName",
              "options": override_field
            },
            "properties": [
              {
                "id": "links",
                "value": [
                  {
                    "targetBlank": False,
                    "title": link_name,
                    "url": "${__data.fields." + link_field + "}"
                  }
                ]
              }
            ]
          }

