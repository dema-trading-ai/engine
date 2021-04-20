# Libraries
import unittest
import os.path
from os import path

class TestConfig(unittest.TestCase):
    """
    Checks if the config is configured correctly.
    """    
    def test_config(self):
        self.assertTrue(path.exists("config.json"))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConfig)
    unittest.TextTestRunner(verbosity=2).run(suite)
