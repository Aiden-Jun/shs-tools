# Tool for building JSON for lunch.json

import json, subprocess, sys, calendar
from datetime import date

DAILY_STATIONS = ["Comfort Food", "Mindful", "Sides"]
WEEKLY_STATIONS = ["Soup", "International Station"]

def is_school_day(d):
    if d.weekday() >= 5:

        return False
    return True

def title(raw):
    return [i.strip().title() for i in raw.split(",") if i.strip()]

def ask(prompt, idx):
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "back":
            if idx > 0:
                return None, idx - 1

            else:
                print("already at the beginning")
                continue
        return raw, idx + 1

while True:
    try:
        year  = int(input("Year: ").strip())
        month = int(input("Month: ").strip())
        if 1 <= month <= 12:
            break
    except ValueError:
        pass
    print("Invalid, try again.")

month_name = calendar.month_name[month]
print(f"Building menu for {month_name} {year}")

from collections import defaultdict
weeks = defaultdict(list)
for day_num in range(1, calendar.monthrange(year, month)[1] + 1):
    d = date(year, month, day_num)
    if is_school_day(d):
        weeks[d.isocalendar()[1]].append(d)

week_keys = sorted(weeks.keys())

menu = {}

inputs = []
for wk in week_keys:
    week_days = weeks[wk]
    monday = week_days[0]
    week_label = f"Week of {monday.strftime('%b %d')}"

    for station in WEEKLY_STATIONS:
        inputs.append({"prompt": f"[{week_label}] {station}: ", "kind": "weekly", "week": wk, "station": station})

    for d in week_days:
        day_label = d.strftime("%a %b %d")
        for station in DAILY_STATIONS:
            skip_hint = " (Enter to skip day)" if station == "Comfort Food" else ""
            inputs.append({"prompt": f"[{day_label}] {station}{skip_hint}: ", "kind": "daily", "date": d, "station": station})

answers = {}

i = 0
skip_until = None

while i < len(inputs):
    entry = inputs[i]

    if skip_until is not None:
        if entry.get("kind") == "daily" and entry.get("date") == skip_until:
            i += 1
            continue
        else:
            skip_until = None

    raw = input(entry["prompt"]).strip()

    if raw.lower() == "back":
        if i > 0:
            i -= 1

            answers.pop(i, None)
        else:
            print("  (already at the beginning)")
        continue

    if entry.get("kind") == "daily" and entry.get("station") == "Comfort Food" and not raw:
        skip_until = entry["date"]
        i += 1
        continue

    answers[i] = raw
    i += 1

weekly_data = defaultdict(dict)

daily_data  = defaultdict(dict)

for idx, entry in enumerate(inputs):
    raw = answers.get(idx, "")
    items = title(raw) if raw else []
    if entry["kind"] == "weekly":
        weekly_data[entry["week"]][entry["station"]] = items
    else:
        daily_data[entry["date"]][entry["station"]] = items

for wk in week_keys:
    for d in weeks[wk]:
        day_str = str(d.day)
        if d not in daily_data or "Comfort Food" not in daily_data[d]:
            continue

        menu[day_str] = {
            **daily_data[d],
            **weekly_data[wk],
        }

output = json.dumps(menu, indent=2)

print()
filename = input("Save as (default: menu.json): ").strip() or "menu.json"
with open(filename, "w") as f:
    f.write(output)
print(f"Saved to {filename}")

try:
    if sys.platform == "darwin":
        subprocess.run("pbcopy", input=output.encode(), check=True)
    elif sys.platform == "win32":
        subprocess.run("clip", input=output.encode(), check=True, shell=True)
    else:
        subprocess.run(["xclip", "-selection", "clipboard"], input=output.encode(), check=True)
    print("Copied to clipboard!")
except Exception:
    print("(Could not copy to clipboard)")
