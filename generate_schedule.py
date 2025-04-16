import random
from datetime import datetime, timedelta

def generate_random_timings(num_timings=20):
    # Generate random minutes within 24 hours (1440 minutes)
    minutes = sorted(random.sample(range(1440), num_timings))
    
    # Convert minutes to HH:MM format
    timings = []
    for minute in minutes:
        hours = minute // 60
        mins = minute % 60
        timings.append(f"{hours:02d}:{mins:02d}")
    
    return timings

if __name__ == "__main__":
    timings = generate_random_timings()
    print("Generated random timings (HH:MM):")
    for time in timings:
        print(time)
    
    # Also print in cron format
    print("\nCron format:")
    for time in timings:
        hour, minute = time.split(":")
        print(f"{minute} {hour} * * *") 