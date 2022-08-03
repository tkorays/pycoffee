from Coffee.Data.DataPattern import RegexPattern

DEFAULT_TS_PATTERNS = [
    RegexPattern(
        name='ts',
        pattern=r'(\d+):(\d+):(\d+)\.(\d\d\d)[ \[]',
        fields={
            'hour': int,
            'minute': int,
            'second': int,
            'millisecond': int,
        }
    ),
    RegexPattern(
        name='ts',
        pattern=r'(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)\.(\d\d\d)',
        fields={
            'year': int,
            'month': int,
            'day': int,
            'hour': int,
            'minute': int,
            'second': int,
            'millisecond': int,
        }
    ),
    RegexPattern(
        name='ts',
        pattern=r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\.(\d\d\d)',
        fields={
            'year': int,
            'month': int,
            'day': int,
            'hour': int,
            'minute': int,
            'second': int,
            'millisecond': int,
        }
    ),
    RegexPattern(
        name='ts',
        pattern=r'(\d+)-(\d+)-(\d+) GMT\+08:00 (\d+):(\d+):(\d+).(\d+)',
        fields={
            'year': int,
            'month': int,
            'day': int,
            'hour': int,
            'minute': int,
            'second': int,
            'millisecond': int,
        }
    ),
    RegexPattern(
        name='ts',
        pattern=r'(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+).(\d+)\+08:00',
        fields={
            'year': int,
            'month': int,
            'day': int,
            'hour': int,
            'minute': int,
            'second': int,
            'millisecond': int,
        }
    ),
    RegexPattern(
        name='ts',
        pattern=r'(\d+)-(\d+)-(\d+)  (\d+):(\d+):(\d+)',
        fields={
            'year': int,
            'month': int,
            'day': int,
            'hour': int,
            'minute': int,
            'second': int
        }
    ),
    RegexPattern(
        name='ts',
        pattern=r'(\d+):(\d+):(\d+)\.(\d\d\d)',
        fields={
            'hour': int,
            'minute': int,
            'second': int,
            'millisecond': int,
        }
    )
]