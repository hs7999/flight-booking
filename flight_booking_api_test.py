from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import random
import time
import json
import copy
import os

HTML_FILE_PATH = "flight_booking.html"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FLIGHTS = {}
with open("flight_list.json", "r") as file:
  flights_list = json.load(file)
  for idx, flight in enumerate(flights_list):
    flight["id"] = idx
    FLIGHTS[idx] = flight

# Flight booking storage (for simplicity, using a list)
BOOKINGS = {}
LAST_BOOKING_ID = 0

# Bug 1: No proper validation (e.g., missing required fields allowed)
class Booking(BaseModel):
    name: str
    email: str
    seats: int
    flight_id: int

@app.post("/book-flight")
def book_flight(booking: Booking):
    try:
      global LAST_BOOKING_ID
      name = booking.name
      email = booking.email
      seats = int(booking.seats)
      flight_id = int(booking.flight_id)
      LAST_BOOKING_ID += 1
      BOOKINGS[LAST_BOOKING_ID] = {
          "name": name,
          "email": email,
          "seats": seats,
          "flight_id": flight_id,
          "booking_id": LAST_BOOKING_ID
      }
      print(FLIGHTS.keys())
      FLIGHTS[flight_id]["seats_left"] -= seats
      return {"message": "Booking successful", "booking_id": LAST_BOOKING_ID}
    except:
      raise HTTPException(status_code=500, detail="Unable to book ticket")


@app.get("/flights")
def get_flights(start_time: str = Query(...), end_time: str = Query(...)):
    try:
      try:
          start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
          end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
      except ValueError:
          raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DDTHH:MM")
      filtered_flights = [
          FLIGHTS[flight] for flight in FLIGHTS
          if start_time_dt <= datetime.strptime(FLIGHTS[flight]["departure_time"], "%Y-%m-%d %H:%M") <= end_time_dt and
            start_time_dt <= datetime.strptime(FLIGHTS[flight]["arrival_time"], "%Y-%m-%d %H:%M") <= end_time_dt
      ]
      sorted_flights = sorted(filtered_flights, key=lambda x: datetime.strptime(x["departure_time"], "%Y-%m-%d %H:%M"))
      return sorted_flights
    except:
      raise HTTPException(status_code=500, detail="Unable to fetch flights")

@app.get("/bookings")
def get_booking():
    try:  
      bookings = copy.deepcopy(BOOKINGS)
      response = []
      for booking in bookings:
          # bookings[booking]["flight_details"] = FLIGHTS[bookings[booking]["flight_id"]]        
          response.append(bookings[booking])
          response[-1]["flight_details"] = FLIGHTS[response[-1]["flight_id"]]
      response.reverse()
      return response
    except:
      raise HTTPException(status_code=500, detail="Unable to fetch bookings")

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):
    raise HTTPException(status_code=500, detail="Unable to connect to Database")
    try:
      # Bug 8: No check if booking_id exists, can crash

      response = BOOKINGS.get(booking_id)
      if not response:
        return HTTPException(status_code=404, detail="Booking not found")
      response["flight_details"] = FLIGHTS[response["flight_id"]]
      return [response]
    except:
      raise HTTPException(status_code=500, detail="Unable to fetch booking")

@app.delete("/booking/{booking_id}")
def delete_booking(booking_id: int):
    try:
      # Bug 9: Doesn't validate if booking exists before deleting
      if booking_id not in BOOKINGS:
        return {"message": "Booking not found"}
      flight_id = BOOKINGS[booking_id]["flight_id"]
      FLIGHTS[flight_id]["seats_left"] += BOOKINGS[booking_id]["seats"]
      del BOOKINGS[booking_id]
      return {"message": "Booking deleted"}  # Bug 10: No success confirmation
    except:
      raise HTTPException(status_code=500, detail="Unable to delete booking")


# Serve the HTML file
@app.get("/app", response_class=HTMLResponse)
async def serve_html():
  file_path = HTML_FILE_PATH
  if os.path.exists(file_path):
      with open(file_path, "r") as file:
          return HTMLResponse(content=file.read(), status_code=200)
  else:
      raise HTTPException(status_code=404, detail="File not found")