import unittest
import os
import tempfile
from src import utils

class TestLogCommand(unittest.TestCase):
    def setUp(self):
        # Create a temporary log file
        self.test_log_file = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        self.test_log_path = self.test_log_file.name

    def tearDown(self):
        # Clean up
        self.test_log_file.close()
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    def test_get_logs_small_file(self):
        """Test reading a small log file completely."""
        content = "Line 1\nLine 2\nLine 3"
        self.test_log_file.write(content)
        self.test_log_file.close()
        
        # Call the function (not yet implemented)
        # We assume the function takes the file path and max_bytes
        logs = utils.get_logs(file_path=self.test_log_path, max_bytes=100)
        self.assertEqual(logs, content)

    def test_get_logs_truncation(self):
        """Test that logs are truncated to the specified limit (tail)."""
        # Create content larger than the limit
        line = "A" * 10 + "\n"
        content = line * 10  # 110 bytes total
        self.test_log_file.write(content)
        self.test_log_file.close()
        
        limit = 50
        logs = utils.get_logs(file_path=self.test_log_path, max_bytes=limit)
        
        self.assertLessEqual(len(logs.encode('utf-8')), limit)
        self.assertTrue(logs.endswith(line.strip() + "\n" + line.strip() + "\n")) # Should be the end of the file

    def test_get_logs_file_not_found(self):
        """Test handling of missing log file."""
        logs = utils.get_logs(file_path="non_existent_file.log")
        self.assertIsNone(logs)

if __name__ == '__main__':
    unittest.main()
