import unittest
import os
from src import config

class TestConfig(unittest.TestCase):
    def test_perplexity_config_loaded(self):
        # We expect the keys to be loaded (either placeholders or real keys)
        self.assertTrue(isinstance(config.PERPLEXITY_API_KEY_PRIMARY, str))
        self.assertTrue(len(config.PERPLEXITY_API_KEY_PRIMARY) > 0)
        
        self.assertTrue(isinstance(config.PERPLEXITY_API_KEY_FALLBACK, str))
        self.assertTrue(len(config.PERPLEXITY_API_KEY_FALLBACK) > 0)

if __name__ == '__main__':
    unittest.main()
