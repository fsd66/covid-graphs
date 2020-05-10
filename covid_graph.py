import dateparser
import urllib.request as url_req
import pandas
import matplotlib.pyplot as plot
import sys

args = sys.argv

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
filename = "c19-data.csv"
print("Downloading latest data from {}".format(url))

url_req.urlretrieve(url, filename)

print("Download successful...saving as {}".format(filename))

csv_data = pandas.DataFrame(pandas.read_csv(filename))

state_data = {}

highest_number = 0

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


    state_data[state].append({"date": date, "date_raw": date_raw, "state": state, "fips": fips, "cases": cases, "deaths": deaths})

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
        cases.append(data["cases"])
        deaths.append(data["deaths"])

    x = i % subfigs_x
    y = int(i / subfigs_x)

    axs[y][x].bar(dates, cases, color="blue", label="Cases")
    axs[y][x].bar(dates, deaths, color="red", label="Deaths")
    axs[y][x].set_title(state)
    axs[y][x].set_xticklabels(dates, rotation=90)

    if "--log" in args or "-l" in args:
        axs[y][x].set_yscale("log")

    if "--normalize" in args or "-n" in args:
        axs[y][x].set_ylim(bottom=0, top=highest_number)

    axs[y][x].legend()

    i += 1

plot.savefig("output.png", bbox_inches="tight", pad_inches=0.5)
