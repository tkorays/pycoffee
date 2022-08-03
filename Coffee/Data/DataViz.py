from grafanalib.core import Dashboard, Template, Templating, RowPanel, GridPos, TimeSeries, DEFAULT_TIME_PICKER
from grafanalib._gen import DashboardEncoder
from grafanalib.influxdb import InfluxDBTarget
import json
import requests


class InfluxdbQueryBuilder:
    def __init__(self, measurement):
        self.fields = []
        self.measurement = measurement

    def query(self, name, alias='',
              selector='first' in ['first', 'last', 'min', 'max'],
              processor='' in ['', 'difference']):
        alias = alias if alias else name
        if not processor:
            self.fields.append(f'{selector}("{name}") AS "{alias}"')
        else:
            self.fields.append(f'{processor}({selector}("{name}")) AS "{alias}"')
        return self

    def query_list(self, li: list):
        for item in li:
            if isinstance(item, str):
                self.fields.append(f'first("{item}") AS "{item}"')
            else:
                proc = '' if len(item) < 4 else item[3]
                sel = 'first' if len(item) < 3 else item[2]
                alias = item[0] if len(item) < 2 else item[1]
                self.query(item[0], alias, sel, proc)
        return self

    def build(self, tags: list, interval='1s', fill='none'):
        query = 'SELECT ' + ' ,'.join(self.fields) + f' from "{self.measurement}" WHERE ('
        query += ' AND '.join([f'"{k}"=~/^${k}$/' for k in tags])
        query += f') AND $timeFilter GROUP BY time({interval}) fill({fill})'
        # print(query)
        return query


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

    def add_row_panel(self, title: str):
        self.panels.append(RowPanel(title=title, gridPos=GridPos(h=1, w=24, x=self.cur_x, y=self.cur_y)))
        self.cur_x = 0
        self.cur_y += 1
        return self

    def add_influx_ts_panel(self, title: str, source: str, influx_query_list: list):
        self.panels.append(TimeSeries(
            title=title,
            dataSource=source,
            targets=[
                InfluxDBTarget(query=x, format='time_series') for x in influx_query_list
            ],
            interval='500ms',
            showPoints='always',
            tooltipMode='multi',
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
