import unittest
import os
import tempfile
import shutil
import ddt
from coffee.data import FileSystemDataStore, HDF5DataStore


@ddt.ddt
class DataStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_file1 = tempfile.mkdtemp()
        self.temp_file2 = tempfile.mktemp()
        self.datastore = [FileSystemDataStore(self.temp_file1), HDF5DataStore(self.temp_file2)]

    def tearDown(self) -> None:
        for ds in self.datastore:
            del ds
        if os.path.exists(self.temp_file1):
            shutil.rmtree(self.temp_file1)
        if os.path.exists(self.temp_file2):
            os.remove(self.temp_file2)

    @ddt.data(0, 1)
    def testAdd(self, store_idx):
        self.datastore[store_idx].add('type_name_aaa', '1234', '1234')
        result = self.datastore[store_idx].fetch('type_name_aaa', '1234')
        self.assertEqual(result, '1234')

    @ddt.data(0, 1)
    def testUpdate(self, store_idx):
        self.datastore[store_idx].add('type_name_aaa', '1234', '1234')
        self.datastore[store_idx].update('type_name_aaa', '1234', '5678')
        self.assertEqual(self.datastore[store_idx].fetch('type_name_aaa', '1234'), '5678')

    @ddt.data(0, 1)
    def testUpdateOrAdd(self, store_idx):
        self.datastore[store_idx].update_or_add('type_name_aaa', '1234', '1234')
        self.datastore[store_idx].update_or_add('type_name_aaa', '1234', '5678')
        self.assertEqual(self.datastore[store_idx].fetch('type_name_aaa', '1234'), '5678')
