<p align="center">
  <h2 align="center">☕ pycoffee</h2>
</p>

<p align="center">
  Assign your work to the machine and enjoy coffee!
</p>

&nbsp;


**Table of contents**
- [description](#description)
- [Getting started](#getting-started)
- [Extend your playbooks](#Extend-your-playbooks)
- [Author](#author)
- [Contributing](#contributing)

## description
`pycoffee` is a toolbox for improving the efficiency in daily work.
Our goal is saving your time and offer you more time to enjoy coffee! 

We provide some features you may like:

* Data extracting, processing and visualizing
  * Extract data from log file, see `Coffee.Data.DataLoader`
  * Store data to timeseries database, see `Coffee.Data.Database`
  * Generate Grafana dashboard by code, see `Coffee.Data.DataViz`
* All workflows are provided with the playbooks, see the default playbook `Coffee.Playbook.PowerToys`
* Plugin based architecture, you can extend the coffee by writing your playbooks

## Getting started

you can install the stable version pycoffee by pip:

```bash
# use pip to install the latest version
pip install pycoffee
```

or you can download the code and run `python ./setup.py install` in the project root.

Just run `--help` to see what features pycoffee provided. 

```bash
# use `--help` to see tools
cof --help

# show external playbooks
cof play --help
```

## Extend your playbooks
Custom playbooks are located in `~/.coffee/CustomPlays/`.
You should create a new directory to hold the playbook's source code and the directory name is the playbook's package name.
An example can be found in `Coffee.Playbook.PowerToys`.

For Example, code in `~/.coffee/CustomPlays/HelloWorld/__init__.py`:

```python
import click


@click.command("hello", help="print hello world")
def play_hello():
  click.echo('hello world')

# commands should be placed in the package's `__init__.py` file
commands = [play_hello, ]
```

Then type `cof play hello` in your console, and you will see the printed `hello world`.

## Author
tkorays <tkorays@hotmail.com>


## Contributing
Welcome to contribute code!
