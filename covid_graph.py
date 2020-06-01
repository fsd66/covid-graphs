import dateparser
import urllib.request as url_req
import pandas
import matplotlib.pyplot as plot
import sys

args = sys.argv

recalculate_mode = "--recalculate" in args or "-r" in args

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
filename = "c19-data.csv"

if not recalculate_mode:
    print("Downloading latest data from {}".format(url))

    url_req.urlretrieve(url, filename)

    print("Download successful...saving as {}".format(filename))

else:
    print("Recalculation mode...using existing data...")

csv_data = pandas.DataFrame(pandas.read_csv(filename))

state_data = {}

highest_number = 0
highest_delta = 0
lowest_delta = 0

case_memory = {}
death_memory = {}

use_delta = "--delta" in args or "-d" in args

for _, row in csv_data.iterrows():
    date_raw = row["date"]
    date = dateparser.parse(date_raw)
    state = row["state"]
    fips = row["fips"]
    cases = row["cases"]
    deaths = row["deaths"]

    if cases > highest_number:
        highest_number = cases

    if deaths > highest_number:
        highest_number = deaths

    if state not in state_data:
        state_data[state] = []

    if state not in case_memory:
        case_memory[state] = 0

    if state not in death_memory:
        death_memory[state] = 0

    case_delta = cases - case_memory[state]
    case_memory[state] = cases

    death_delta = deaths - death_memory[state]
    death_memory[state] = deaths

    if case_delta > highest_delta:
        highest_delta = case_delta
    if death_delta > highest_delta:
        highest_delta = death_delta

    if case_delta < lowest_delta:
        lowest_delta = case_delta
    if death_delta < lowest_delta:
        lowest_delta = death_delta

    state_data[state].append({"date": date, "date_raw": date_raw, "state": state, "fips": fips, "cases": cases, "deaths": deaths, "case_delta": case_delta, "death_delta": death_delta})

for state in state_data:
    data = state_data[state]
    data.sort(key = lambda entry: entry["date"])

subfigs = len(state_data)
subfigs_x = 1


while True:
    if subfigs % subfigs_x == 0 and int(subfigs / subfigs_x) <= subfigs_x:
        break

    subfigs_x += 1

subfigs_y = int(subfigs / subfigs_x)

fig_size = (12 * subfigs_x, 8 * subfigs_y)

fig, axs = plot.subplots(subfigs_y, subfigs_x, figsize=fig_size)

i = 0
for state in sorted(state_data):
    dates = []
    cases = []
    deaths = []

    for data in state_data[state]:
        dates.append("{}/{}".format(data["date"].month, data["date"].day))
        cases.append(data["cases"] if not use_delta else data["case_delta"])
        deaths.append(data["deaths"] if not use_delta else data["death_delta"])

    x = i % subfigs_x
    y = int(i / subfigs_x)

    axs[y][x].plot(dates, cases, color="blue", label="Cases")
    axs[y][x].plot(dates, deaths, color="red", label="Deaths")
    axs[y][x].set_title(state)
    axs[y][x].set_xticklabels(dates, rotation=90)

    if "--log" in args or "-l" in args:
        axs[y][x].set_yscale("log")

    if ("--normalize" in args or "-n" in args):
        if not use_delta:
            axs[y][x].set_ylim(bottom=0, top=highest_number * 1.05)
        elif use_delta:
            axs[y][x].set_ylim(bottom=lowest_delta * 1.05, top=highest_delta * 1.05)

    axs[y][x].legend()

    i += 1

plot.savefig("output.png", bbox_inches="tight", pad_inches=0.5)
