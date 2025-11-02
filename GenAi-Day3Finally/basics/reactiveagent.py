
# reactive 

import random

def energy_monitor():
    energy_level = random.randint(50, 120)
    print(f"Energy usage: {energy_level} units")

    if energy_level > 100:
        print("⚠️ High usage! Sending alert.")
    else:
        print("✅ Usage normal.")

for _ in range(3):
    energy_monitor()
