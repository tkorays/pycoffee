# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

from grafanalib.core import Dashboard, Template, Templating, RowPanel, GridPos, TimeSeries, DEFAULT_TIME_PICKER, Table
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

    def build(self):
        self.dashboard = Dashboard(
            title=self.title,
            uid=self.uid,
            description=self.description,
            tags=self.tags,
            timezone='browser',
            timePicker=DEFAULT_TIME_PICKER,
            editable=True,
            templating=Templating(list=self.templates),
            panels=self.panels
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

