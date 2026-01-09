import unittest
import os
from src import config

class TestConfig(unittest.TestCase):
    def test_perplexity_config_loaded(self):
        # We expect the placeholders we added to .env to be loaded
        self.assertEqual(config.PERPLEXITY_API_KEY_PRIMARY, "your_perplexity_api_key_primary")
        self.assertEqual(config.PERPLEXITY_API_KEY_FALLBACK, "your_perplexity_api_key_fallback")

if __name__ == '__main__':
    unittest.main()
