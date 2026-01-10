import asyncio
from src.utils import ProgressTracker

async def simulate_progress():
    steps = ["Initialization", "Drafting", "Notion Entry"]
    tracker = ProgressTracker(steps)
    
    print("--- Initial State ---")
    for s in tracker.get_steps_status():
        icon = "⬜" if s[1] == "pending" else "⏳" if s[1] == "in_progress" else "✅"
        print(f"{icon} {s[0]}")
    
    print("\n--- Start Initialization ---")
    tracker.start_step("Initialization")
    for s in tracker.get_steps_status():
        icon = "⬜" if s[1] == "pending" else "⏳" if s[1] == "in_progress" else "✅"
        print(f"{icon} {s[0]}")
        
    await asyncio.sleep(0.5)
    tracker.complete_step("Initialization")
    
    print("\n--- Initialization Complete, Start Drafting ---")
    tracker.start_step("Drafting")
    for s in tracker.get_steps_status():
        icon = "⬜" if s[1] == "pending" else "⏳" if s[1] == "in_progress" else "✅"
        timer = f" ({s[2]})" if s[2] else ""
        print(f"{icon} {s[0]}{timer}")

    await asyncio.sleep(1)
    tracker.complete_step("Drafting")
    
    print("\n--- Final State ---")
    for s in tracker.get_steps_status():
        icon = "⬜" if s[1] == "pending" else "⏳" if s[1] == "in_progress" else "✅"
        timer = f" ({s[2]})" if s[2] else ""
        print(f"{icon} {s[0]}{timer}")

if __name__ == "__main__":
    asyncio.run(simulate_progress())
