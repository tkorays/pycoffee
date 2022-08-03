import abc
import importlib
from datetime import datetime
from Coffee.Data.DataStore import DataStore


class DiagnoseLabel:
    """
    用于表示一个诊断结果标签。
    """
    def __init__(self, name: str, accuracy: float = 1.0, description: str = ''):
        """
        :param name: label name
        :param accuracy: accuracy of the label
        :param description: description of this diagnose
        """
        self.name = name
        self.accuracy = accuracy
        self.description = description
        self.datetime = datetime.now()


class DiagnoseResult:
    def __init__(self):
        self.summary = []  # DiagnoseLabel
        self.details = []


class DiagnoseAnalyzer(metaclass=abc.ABCMeta):
    """
    分析器，用于分析一类问题，输出分析后的结果标签。
    """
    @abc.abstractmethod
    def __init__(self, cache: DataStore):
        self.cache = cache

    @abc.abstractmethod
    def analyze(self, info: dict, hint: list) -> DiagnoseLabel:
        pass


class Diagnoser:
    def __init__(self, analyzers: dict, cache: DataStore):
        self.analyzers = analyzers
        self.cache = cache

    def diagnose(self, info: dict, problems: list):
        """
        input information for diagnosing and diagnose purpose and return the result for every problem.
        """
        result = {}
        for p in problems:
            if p in self.analyzers.keys():
                module = importlib.import_module(self.analyzers[p])
                module = importlib.reload(module)

                analyzer_class = module.analyzer
                ret = analyzer_class(self.cache).analyze(info, problems)
                result[p] = ret
        return result
