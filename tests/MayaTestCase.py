import os
import tempfile
import unittest
import uuid


class MayaTestCase(unittest.TestCase):

    files_created = []

    @classmethod
    def tearDownClass(cls):
        super(MayaTestCase, cls).tearDownClass()
        cls.delete_temp_files()

    @classmethod
    def delete_temp_files(cls):
        for f in cls.files_created:
            if os.path.exists(f):
                os.remove(f)
        cls.files_created = []

    @classmethod
    def get_temp_filename(cls, file_name):
        temp_dir = os.path.join(tempfile.gettempdir(), "unit_test", str(uuid.uuid4()))
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        base_name, ext = os.path.splittext(file_name)
        path = "{0}/{1}{2}".format(temp_dir, base_name, ext)
        count = 0
        while os.path.exists(path):
            count += 1
            path = "{0}/{1}{2}{3}".format(temp_dir, base_name, count, ext)
        cls.files_created.append(path)
        return path
