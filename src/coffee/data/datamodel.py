from abc import ABCMeta


class DataModel(metaclass=ABCMeta):
    @staticmethod
    def get_class_data_filed(a_class) -> dict:
        ret = {}
        for k, v in a_class.__dict__.items():
            if k.startswith('__') and k.endswith('__'):
                continue
            ret[k] = v
        return ret

    @staticmethod
    def normalize_data_field(kv: dict, a_class: object) -> dict:
        result = {}
        fields = DataModel.get_class_data_filed(a_class)
        for n, t in fields.items():
            if n in kv.keys():
                # when convert failed, we should ignore these fields
                try:
                    result[n] = t(float(kv[n])) if t is int else t(kv[n])
                    # ignore inf values
                    if result[n] == float('inf') or result[n] == float('-inf'):
                        result.pop(n)
                        continue
                except:
                    continue
        return result
