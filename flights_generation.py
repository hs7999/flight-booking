from datetime import datetime, timedelta
import random
import json

# Flight options
flight_codes = ["AI101", "6E202", "UK404", "AI997", "G8123", "SG567", "IX999", "QF303", "EK204", "LH789"]
base_departure_time = datetime(2025, 4, 1, 6, 0)  # Flights start at 6:00 AM on April 1st

flights = []

for i in range(100):
    flight_code = random.choice(flight_codes)
    
    # Generate random departure date and time (April 1-30, 2025)
    departure_datetime = base_departure_time + timedelta(days=random.randint(0, 29), hours=random.randint(0, 18))
    arrival_datetime = departure_datetime + timedelta(hours=random.randint(2, 3))  # Flight duration 2-3 hours
    
    price = random.randint(5000, 10000)
    seats_left = random.randint(1, 15)

    flights.append({
        "flight": flight_code,
        "price": price,
        "seats_left": seats_left,
        "departure_time": departure_datetime.strftime("%Y-%m-%d %H:%M"),
        "arrival_time": arrival_datetime.strftime("%Y-%m-%d %H:%M")
    })

# Sort flights by departure_time (ascending)
flights.sort(key=lambda x: datetime.strptime(x["departure_time"], "%Y-%m-%d %H:%M"))

# Print the sorted list
print(json.dumps(flights, indent=4))
