"""Public flight data for the flights page.

`python3 tools/flights_data.py PATH_TO_VAULT_CSV` refreshes tools/flights.csv
from the vault's Resources/Flight Log.csv. Only what is safe to publish is
kept: no booking references, email links, seats, notes or other passengers,
no cancelled bookings, nothing undated and nothing from the last week.
"""
import csv
import re
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE / "flights.csv"
FIELDS = ["id", "trip", "date", "dep", "arr", "next_day", "flight", "airline", "from", "to", "km", "min", "cabin", "aircraft"]

# iata: (city, country, lat, lon)
AIRPORTS = {
 'AMD': ('Ahmedabad', 'India', 23.0772, 72.6347),
 'AMS': ('Amsterdam', 'Netherlands', 52.3086, 4.7639),
 'ATL': ('Atlanta', 'United States', 33.6367, -84.4281),
 'AYT': ('Antalya', 'Turkey', 36.8987, 30.8005),
 'BDJ': ('Banjarmasin', 'Indonesia', -3.4424, 114.7626),
 'BKI': ('Kota Kinabalu', 'Malaysia', 5.9372, 116.0510),
 'BOM': ('Mumbai', 'India', 19.0887, 72.8679),
 'BRS': ('Bristol', 'United Kingdom', 51.3827, -2.7191),
 'CDG': ('Paris', 'France', 49.0097, 2.5479),
 'CKG': ('Chongqing', 'China', 29.7192, 106.6417),
 'CTS': ('Sapporo', 'Japan', 42.7752, 141.6923),
 'DAD': ('Da Nang', 'Vietnam', 16.0439, 108.1994),
 'DMK': ('Bangkok', 'Thailand', 13.9126, 100.6070),
 'DPS': ('Bali', 'Indonesia', -8.7482, 115.1672),
 'EDI': ('Edinburgh', 'United Kingdom', 55.9500, -3.3725),
 'FNC': ('Madeira', 'Portugal', 32.6979, -16.7745),
 'FUK': ('Fukuoka', 'Japan', 33.5859, 130.4510),
 'GLA': ('Glasgow', 'United Kingdom', 55.8719, -4.4331),
 'GMP': ('Seoul Gimpo', 'South Korea', 37.5583, 126.7906),
 'HAN': ('Hanoi', 'Vietnam', 21.2212, 105.8072),
 'HKG': ('Hong Kong', 'Hong Kong', 22.3080, 113.9185),
 'HKT': ('Phuket', 'Thailand', 8.1132, 98.3169),
 'HND': ('Tokyo Haneda', 'Japan', 35.5494, 139.7798),
 'ICN': ('Seoul Incheon', 'South Korea', 37.4602, 126.4407),
 'IST': ('Istanbul', 'Turkey', 41.2753, 28.7519),
 'JFK': ('New York', 'United States', 40.6413, -73.7781),
 'KBV': ('Krabi', 'Thailand', 8.0991, 98.9862),
 'KLX': ('Kalamata', 'Greece', 37.0683, 22.0255),
 'KUL': ('Kuala Lumpur', 'Malaysia', 2.7456, 101.7099),
 'LGK': ('Langkawi', 'Malaysia', 6.3297, 99.7287),
 'LGW': ('London Gatwick', 'United Kingdom', 51.1537, -0.1821),
 'LHR': ('London Heathrow', 'United Kingdom', 51.4700, -0.4543),
 'LIS': ('Lisbon', 'Portugal', 38.7742, -9.1342),
 'LUX': ('Luxembourg', 'Luxembourg', 49.6233, 6.2044),
 'MAA': ('Chennai', 'India', 12.9941, 80.1709),
 'MIA': ('Miami', 'United States', 25.7959, -80.2870),
 'NGO': ('Nagoya', 'Japan', 34.8584, 136.8054),
 'NRT': ('Tokyo Narita', 'Japan', 35.7720, 140.3929),
 'PER': ('Perth', 'Australia', -31.9385, 115.9672),
 'PUS': ('Busan', 'South Korea', 35.1795, 128.9382),
 'PVG': ('Shanghai Pudong', 'China', 31.1443, 121.8083),
 'SGN': ('Ho Chi Minh City', 'Vietnam', 10.8188, 106.6519),
 'SHA': ('Shanghai Hongqiao', 'China', 31.1979, 121.3363),
 'SIN': ('Singapore', 'Singapore', 1.3644, 103.9915),
 'STN': ('London Stansted', 'United Kingdom', 51.8860, 0.2389),
 'SUB': ('Surabaya', 'Indonesia', -7.3798, 112.7869),
 'TPE': ('Taipei', 'Taiwan', 25.0797, 121.2342),
}

# Public trip titles, keyed by the vault ID of each trip's first flight. The
# vault keeps its own trip names; the site shows places only.
TRIPS = {
    "F002": "Glasgow",
    "F004": "Atlanta, Miami, New York",
    "F008": "Antalya",
    "F010": "Bali",
    "F016": "New York",
    "F018": "Mumbai and Chennai",
    "F022": "Tokyo",
    "F024": "Madeira",
    "F027": "Singapore",
    "F030": "Kuala Lumpur",
    "F031": "Phuket",
    "F033": "Da Nang, Busan, Seoul",
    "F039": "Bali",
    "F041": "Ho Chi Minh City",
    "F044": "Perth",
    "F046": "Tokyo, Nagoya, Sapporo",
    "F050": "Bangkok",
    "F052": "Tokyo",
    "F054": "Krabi",
    "F056": "Bali, Borneo, Java",
    "F060": "Kota Kinabalu",
    "F062": "Japan, Korea, Shanghai, Taipei, Hong Kong, Chongqing",
    "F069": "Home",
    "F070": "Kalamata",
    "F072": "Edinburgh",
    "F074": "Vietnam",
    "F079": "Luxembourg",
    "F081": "Ahmedabad",
}


# Cabin labels as printed on the stub
def cabin(raw):
    r = raw.lower()
    if "business" in r:
        return "Business"
    if "premium" in r:
        return "Premium Economy"
    return "Economy"


def airline(raw):
    return re.sub(r"\s*\(.*", "", raw).replace("  ", " ").strip()


def refresh(vault_csv):
    # nothing from the last week, so a refresh on a travel day never says where he is
    cutoff = (date.today() - timedelta(days=7)).isoformat()
    out, trip = [], None
    for r in csv.DictReader(open(vault_csv, encoding="utf-8")):
        if r["status"] == "cancelled" or not r["dep_date"] or r["dep_date"] > cutoff:
            continue
        if r["id"] in TRIPS:
            trip = TRIPS[r["id"]]
        elif trip is None or r["trip"] != last_trip:
            sys.exit(f"{r['id']} starts a new trip: add it to TRIPS")
        last_trip = r["trip"]
        if r["from_iata"] not in AIRPORTS or r["to_iata"] not in AIRPORTS:
            sys.exit(f"Add {r['from_iata']} or {r['to_iata']} to AIRPORTS first")
        out.append({
            "id": r["id"], "trip": trip, "date": r["dep_date"], "dep": r["dep_time"], "arr": r["arr_time"],
            "next_day": "1" if r["arr_date"] and r["arr_date"] > r["dep_date"] else "",
            "flight": r["flight_no"], "airline": airline(r["airline"]), "from": r["from_iata"], "to": r["to_iata"],
            "km": r["km"], "min": r["min"], "cabin": cabin(r["cabin"]), "aircraft": r["aircraft"],
        })
    with open(PUBLIC, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} flights written to {PUBLIC.name}")


def load():
    return list(csv.DictReader(open(PUBLIC, encoding="utf-8")))


if __name__ == "__main__":
    refresh(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "Documents/obsidan/Brain/Resources/Flight Log.csv")
