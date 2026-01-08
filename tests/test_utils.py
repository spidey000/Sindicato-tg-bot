import unittest
from src.utils import generate_case_id
from datetime import datetime

class TestUtils(unittest.TestCase):
    def test_id_generation(self):
        case_id = generate_case_id("D")
        self.assertTrue(case_id.startswith("D-"))
        self.assertIn(str(datetime.now().year), case_id)
        
        case_id_j = generate_case_id("J")
        self.assertTrue(case_id_j.startswith("J-"))

if __name__ == '__main__':
    unittest.main()
