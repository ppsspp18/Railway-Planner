import json
from datetime import datetime, timedelta
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Routing Engine")

# Load Datasets
with open("train_dataset.json", "r") as f:
    TRAINS = json.load(f)
with open("seat_dataset.json", "r") as f:
    SEAT_DATA = json.load(f)

# Build a lookup for seats
SEAT_LOOKUP = {}
for record in SEAT_DATA:
    dt = record["journey_start_date"]
    tr = record["train_number"]
    if dt not in SEAT_LOOKUP: SEAT_LOOKUP[dt] = {}
    SEAT_LOOKUP[dt][tr] = record["leg_availability"]

def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

def build_edges():
    edges = []
    for t in TRAINS:
        stations = [t["src"], t["first_stop"], t["second_stop"], t["dest"]]
        times = [
            parse_time(t["src_departure_time"]),
            parse_time(t["first_stop_departure_time"]),
            parse_time(t["second_stop_departure_time"]),
            parse_time(t["destination_arrival_time"])
        ]
        
        for i in range(len(stations)):
            for j in range(i + 1, len(stations)):
                dep_time = times[i]
                arr_time = times[j]
                
                day_offset = 0
                current_time = dep_time
                for k in range(i, j):
                    next_time = times[k+1]
                    if next_time < current_time:
                        day_offset += 1
                    current_time = next_time
                
                legs_covered = [f"{stations[k]}-{stations[k+1]}" for k in range(i, j)]
                
                edges.append({
                    "train": t["train_number"],
                    "src": stations[i],
                    "dest": stations[j],
                    "dep_time_str": times[i].strftime("%H:%M"),
                    "arr_time_str": times[j].strftime("%H:%M"),
                    "duration_mins": (arr_time - dep_time).total_seconds() / 60 + (day_offset * 1440),
                    "day_offset": day_offset,
                    "legs": legs_covered
                })
    return edges

GRAPH_EDGES = build_edges()

def get_availability(train, date_str, legs):
    try:
        avail = SEAT_LOOKUP[date_str][train]
        min_seats = min(avail[leg] for leg in legs)
    except KeyError:
        return "N/A", 0, -100

    if min_seats > 50:
        status = "AVAILABLE"
        prob = 100
    elif -50 <= min_seats <= 50:
        status = f"RAC {50 - min_seats}"
        prob = 100
    elif -99 <= min_seats < -50:
        status = f"WL {-50 - min_seats}"
        prob = round(20 + (min_seats - (-99)) * (79 / 49), 1)
    else:
        status = "REGRET"
        prob = 0
        
    return status, prob, min_seats

@app.get("/routes")
def find_routes(src: str, dest: str, date: str):
    start_date = datetime.strptime(date, "%Y-%m-%d")
    valid_routes = []

    # 1. Direct Routes
    direct_edges = [e for e in GRAPH_EDGES if e["src"] == src and e["dest"] == dest]
    for e in direct_edges:
        status, prob, min_seats = get_availability(e["train"], date, e["legs"])
        
        dep_dt = datetime.strptime(f"{date} {e['dep_time_str']}", "%Y-%m-%d %H:%M")
        arr_dt = dep_dt + timedelta(minutes=e["duration_mins"])
        
        valid_routes.append({
            "type": "Direct",
            "total_time_mins": e["duration_mins"],
            "overall_prob": prob,
            "min_seats": min_seats,
            "route_legs": [{
                "train": e["train"],
                "src": src, "dest": dest,
                "dep_dt": dep_dt.strftime("%Y-%m-%d %H:%M"),
                "arr_dt": arr_dt.strftime("%Y-%m-%d %H:%M"),
                "status": status
            }],
            "transfer_mins": 0
        })

    # 2. One-Layover Routes
    from_src = [e for e in GRAPH_EDGES if e["src"] == src]
    to_dest = [e for e in GRAPH_EDGES if e["dest"] == dest]

    for leg1 in from_src:
        for leg2 in to_dest:
            if leg1["dest"] == leg2["src"]: 
                hub = leg1["dest"]
                
                # Leg 1 Times
                l1_dep_dt = datetime.strptime(f"{date} {leg1['dep_time_str']}", "%Y-%m-%d %H:%M")
                l1_arr_dt = l1_dep_dt + timedelta(minutes=leg1["duration_mins"])
                
                # Leg 2 Times
                l2_dep_dt = datetime.strptime(f"{l1_arr_dt.strftime('%Y-%m-%d')} {leg2['dep_time_str']}", "%Y-%m-%d %H:%M")
                if l2_dep_dt < l1_arr_dt: 
                    l2_dep_dt += timedelta(days=1) # Train left earlier, catch it tomorrow
                
                transfer_mins = (l2_dep_dt - l1_arr_dt).total_seconds() / 60
                
                if 30 <= transfer_mins <= 720: # 30 min to 12 hour layover
                    # FIX: Explicitly add duration to get proper arrival time
                    l2_arr_dt = l2_dep_dt + timedelta(minutes=leg2["duration_mins"])
                    
                    s1, p1, m1 = get_availability(leg1["train"], l1_dep_dt.strftime("%Y-%m-%d"), leg1["legs"])
                    s2, p2, m2 = get_availability(leg2["train"], l2_dep_dt.strftime("%Y-%m-%d"), leg2["legs"])
                    
                    overall_prob = round((p1 / 100) * (p2 / 100) * 100, 1)
                    total_time = leg1["duration_mins"] + transfer_mins + leg2["duration_mins"]
                    
                    valid_routes.append({
                        "type": "1-Stop Layover",
                        "total_time_mins": total_time,
                        "overall_prob": overall_prob,
                        "min_seats": min(m1, m2),
                        "transfer_mins": transfer_mins,
                        "route_legs": [
                            {
                                "train": leg1["train"], "src": src, "dest": hub,
                                "dep_dt": l1_dep_dt.strftime("%Y-%m-%d %H:%M"),
                                "arr_dt": l1_arr_dt.strftime("%Y-%m-%d %H:%M"),
                                "status": s1
                            },
                            {
                                "train": leg2["train"], "src": hub, "dest": dest,
                                "dep_dt": l2_dep_dt.strftime("%Y-%m-%d %H:%M"),
                                "arr_dt": l2_arr_dt.strftime("%Y-%m-%d %H:%M"),
                                "status": s2
                            }
                        ]
                    })

    # Sort
    valid_routes.sort(key=lambda x: (x["total_time_mins"], -x["overall_prob"]))
    return {"status": "success", "routes": valid_routes[:10]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)