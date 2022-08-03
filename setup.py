from setuptools import setup, find_packages
version = '1.0.1'


setup(
    name="coffee",
    version=version,
    description="coffee tools",
    author="tkorays",
    author_email="tkorays@hotmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    scripts=[],
    data_files=[
    ],
    entry_points={
        'console_scripts': [
            'cof=Coffee.CLI.coffee:coffee'
        ]
    },
    install_requires=[
        'configparser',
        'pyyaml',
        'click',
        'influxdb',
        'elasticsearch',
        'requests',
        'wget',
        'watchdog',
        'rich',
        'ntplib',
        'pyqt5',
        'grafanalib',
        'flask'
    ],
    dependency_links=[
    ],
    long_description='''
    Coffee is a hacker tools!
    '''
)
