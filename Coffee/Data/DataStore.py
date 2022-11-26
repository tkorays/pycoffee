# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

import abc
import os
import pickle
import h5py
import numpy as np
from Coffee.Core.Settings import DEF_CFG


class DataStorable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def store_id(self) -> str:
        pass

    @abc.abstractmethod
    def store_type(self) -> str:
        pass


class DataStore(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exist(self, type_id: str, cache_id: str):
        """
        To check whether the data has been cached.

        :param type_id: the data type id, the same type data has the same structure.
        :param cache_id: data id identified by some fields.
        :return True if the data has been cached.
        """
        pass

    @abc.abstractmethod
    def add(self, type_id: str, cache_id: str, data):
        """
        add a new data.

        :param type_id: the data type id, the same type data has the same structure.
        :param cache_id: data id identified by some fields.
        :param data: data.
        :return True if the data has been added.
        """
        pass

    @abc.abstractmethod
    def update(self, type_id: str, cache_id: str, data):
        """
        update data.

        :param type_id: the data type id, the same type data has the same structure.
        :param cache_id: data id identified by some fields.
        :param data: data.
        :return True if the data has been updated.
        """
        pass

    @abc.abstractmethod
    def update_or_add(self, type_id: str, cache_id: str, data):
        """
        update if exist or add new data.

        :param type_id: the data type id, the same type data has the same structure.
        :param cache_id: data id identified by some fields.
        :param data: data.
        :return True if the data has been updated.
        """
        pass

    @abc.abstractmethod
    def fetch(self, type_id: str, cache_id: str):
        """
        fetch data.

        :param type_id: the data type id, the same type data has the same structure.
        :param cache_id: data id identified by some fields.
        :return data.
        """
        pass


class FileSystemDataStore(DataStore):
    """
    store data in the filesystem.
    """
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if not os.path.exists(self.path):
            raise Exception("failed to crate storage.")

    def exist(self, type_id: str, cache_id: str):
        if os.path.exists(os.path.join(self.path, type_id, cache_id)):
            return True
        else:
            return False

    def add(self, type_id: str, cache_id: str, data):
        if os.path.exists(os.path.join(self.path, type_id, cache_id)):
            return True

        if not os.path.exists(os.path.join(self.path, type_id)):
            os.mkdir(os.path.join(self.path, type_id))
        if not os.path.exists(os.path.join(self.path, type_id)):
            return False

        with open(os.path.join(self.path, type_id, cache_id), 'wb') as f:
            pickle.dump(data, f)
        return True

    def update(self, type_id: str, cache_id: str, data):
        if not os.path.exists(os.path.join(self.path, type_id)):
            os.mkdir(os.path.join(self.path, type_id))
        if not os.path.exists(os.path.join(self.path, type_id)):
            return False

        with open(os.path.join(self.path, type_id, cache_id), 'wb') as f:
            pickle.dump(data, f)
        return True

    def update_or_add(self, type_id: str, cache_id: str, data):
        if self.exist(type_id, cache_id):
            return self.update(type_id, cache_id, data)
        else:
            return self.add(type_id, cache_id, data)

    def fetch(self, type_id: str, cache_id: str):
        if not os.path.exists(os.path.join(self.path, type_id, cache_id)):
            return None

        data = None
        with open(os.path.join(self.path, type_id, cache_id), 'rb') as f:
            data = pickle.load(f)
        return data


class HDF5DataStore(DataStore):
    # how to store VLEN bytes in HDF5
    # https://docs.h5py.org/en/latest/special.html?highlight=VLEN#h5py.vlen_dtype

    def __init__(self, path):
        self.path = path
        self.hdf5 = h5py.File(self.path, "a")
        # root has a data set named type_id

    def __del__(self):
        self.hdf5.close()

    def exist(self, type_id: str, cache_id: str):
        dataset = self.hdf5.get(f"{type_id}")
        if not dataset:
            return False
        return cache_id in dataset.keys()

    def add(self, type_id: str, cache_id: str, data):
        dataset = self.hdf5.get(f"{type_id}")
        if not dataset:
            self.hdf5.create_dataset(f'{type_id}', data='')
            dataset = self.hdf5.get(f"{type_id}")
        else:
            if cache_id not in dataset.attrs.keys():
                return True
        dataset.attrs[cache_id] = np.void(pickle.dumps(data))
        self.hdf5.update()
        return True

    def update(self, type_id: str, cache_id: str, data):
        dataset = self.hdf5.get(f"{type_id}")
        if dataset:
            dataset.attrs[cache_id] = np.void(pickle.dumps(data))
            self.hdf5.update()
        return True

    def update_or_add(self, type_id: str, cache_id: str, data):
        dataset = self.hdf5.get(f"{type_id}")
        if not dataset:
            self.hdf5.create_dataset(f'{type_id}', data='')
            dataset = self.hdf5.get(f"{type_id}")

        dataset.attrs[cache_id] = np.void(pickle.dumps(data))
        self.hdf5.update()
        return True

    def fetch(self, type_id: str, cache_id: str):
        dataset = self.hdf5.get(f"{type_id}")
        if not dataset:
            return None
        if cache_id not in dataset.attrs.keys():
            return None
        return pickle.loads(dataset.attrs[cache_id].tobytes())


DEF_DATA_STORE = FileSystemDataStore(DEF_CFG.data_store_path)
