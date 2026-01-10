import unittest
import time
from src.utils import ProgressTracker

class TestProgressTracker(unittest.TestCase):
    def test_initial_state(self):
        steps = ["Step 1", "Step 2"]
        tracker = ProgressTracker(steps)
        status = tracker.get_steps_status()
        self.assertEqual(len(status), 2)
        self.assertEqual(status[0], ["Step 1", "pending", None])
        self.assertEqual(status[1], ["Step 2", "pending", None])

    def test_start_step(self):
        steps = ["Step 1"]
        tracker = ProgressTracker(steps)
        tracker.start_step("Step 1")
        status = tracker.get_steps_status()
        self.assertEqual(status[0][1], "in_progress")
        self.assertIn("Step 1", tracker.start_times)

    def test_complete_step(self):
        steps = ["Step 1"]
        tracker = ProgressTracker(steps)
        tracker.start_step("Step 1")
        time.sleep(0.1) # Simulate some work
        tracker.complete_step("Step 1")
        status = tracker.get_steps_status()
        self.assertEqual(status[0][1], "completed")
        self.assertTrue(status[0][2].endswith("s"))
        
        # Check if it's a float-like string (e.g., "0.1s")
        elapsed_val = float(status[0][2][:-1])
        self.assertGreaterEqual(elapsed_val, 0.1)

    def test_fail_step(self):
        steps = ["Step 1"]
        tracker = ProgressTracker(steps)
        tracker.fail_step("Step 1")
        status = tracker.get_steps_status()
        self.assertEqual(status[0][1], "failed")

if __name__ == '__main__':
    unittest.main()