from Coffee.Data.DataProcessor import DataSink
from Coffee.Data.DataPoint import DataPoint
import click


class PatternMatchReporter(DataSink):
    def __init__(self):
        super().__init__()
        self.result = {}

    def on_data(self, datapoint: DataPoint) -> DataPoint:
        meta = datapoint.meta
        id = meta.get('id', '')
        if not id:
            return datapoint
        if id not in self.result.keys():
            self.result[id] = 1
        else:
            self.result[id] += 1
        return datapoint

    def finish(self, datapoint: DataPoint) -> DataPoint:
        click.echo(click.style('Pattern Match Result:', fg='green', bold=True))
        # click.echo(click.style('  {:<28s} : {}'.format('Begin Time', min_dt), fg='red'))
        # click.echo(click.style('  {:<28s} : {}'.format('End Time', max_dt), fg='red'))
        for k, v in self.result.items():
            click.echo('  {:<28s} : {}'.format(k, v))
        return datapoint
