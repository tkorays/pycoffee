import re
import types
import yaml


class PatternInterface:
    """
    patterns is used to extract data from logs
    """

    def get_unique_id(self):
        """
        every pattern has a unique id.
        """
        pass

    def get_name(self):
        """
        pattern's name.
        """
        pass

    def get_tags(self):
        """
        tags are data fields in patterns which will be used in searching.
        """
        pass

    def get_match_count(self):
        """
        match count of this pattern in this running context.
        """
        pass

    def match(self, s):
        """
        do extracting.
        """
        pass


class PatternGroup:
    """
    group of patterns.
    """

    def __init__(self, name, patterns, ts_patterns):
        self.name = name
        self.patterns = patterns
        self.ts_patterns = ts_patterns

    def get_name(self):
        return self.name

    def get_patterns(self):
        return self.patterns

    def get_ts_patterns(self):
        return self.ts_patterns

    def run_tests(self):
        for p in self.patterns:
            p.run_tests()


class RegexPattern(PatternInterface, yaml.YAMLObject):
    def __init__(self, name, pattern, fields, tags=[], version='', processors=[], exclude_report=[], tests=[]):
        self.name = name
        self.version = version
        self.pattern = pattern
        self.tags = tags
        self.processors = processors
        self.regex = None
        self.fields = fields
        self.exclude_report = exclude_report
        self.tests = tests
        self.match_count = 0

    def __repr__(self):
        return "%s(name=%r, pattern=%r, fields=%r, tags=%r, version=%r, processors=%r, exclude_report=%r, tests=%r)" % (
            self.__class__.__name__, self.name, self.pattern, self.fields, self.tags, self.version,
            self.processors, self.exclude_report, self.tests
        )

    def get_unique_id(self):
        return self.name + (('@' + str(self.version)) if self.version else '')

    def get_name(self):
        return self.name
    
    def get_tags(self):
        return self.tags
    
    def get_exclude_report(self):
        return self.exclude_report
    
    def get_match_count(self):
        return self.match_count

    def match(self, s):
        self.regex = re.compile(self.pattern) if not self.regex else self.regex
        if not self.regex:
            return {}

        result = self.regex.findall(s)
        if not result:
            return {}

        if isinstance(result[0], type(())):
            result = result[0]
        if type(result) in [type([]), type({}), type(())]:
            result_len = len(result)
        else:
            result_len = 1
        
        if result_len != len(self.fields):
            return {}

        kv = {}
        idx = 0
        for k, v in self.fields.items():
            try:
                kv[k] = v(result[idx])
            except ValueError:
                print("type convert failed, field name: {} in {}".format(k, self.get_unique_id()))
            idx += 1
        
        self.match_count = self.match_count + 1
        for p in self.processors:
            if isinstance(p, types.FunctionType):
                kv = p(self.name, kv)
            else:
                kv = p.process(self.name, kv)
        return kv
    
    def run_tests(self):
        success_cnt = 0
        for t in self.tests:
            success_cnt += 1 if self.match(t) else 0
        print("run [{}] test done {}/{}".format(self.get_unique_id(), success_cnt, len(self.tests)))
        return success_cnt == len(self.tests)
