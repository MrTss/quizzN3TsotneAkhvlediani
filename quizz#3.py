import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from win10toast import ToastNotifier

def scrape_data():
    url = "https://www.worldometers.info/coronavirus"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "main_table_countries_today"})

    data = []
    for row in table.find_all("tr"):
        row_data = {}
        columns = row.find_all("td")
        if len(columns) >= 13:
            row_data["Country"] = columns[1].text.strip()
            row_data["Total Cases"] = columns[2].text.strip()
            row_data["New Cases"] = columns[3].text.strip()
            row_data["Total Deaths"] = columns[4].text.strip()
            row_data["New Deaths"] = columns[5].text.strip()
            row_data["Total Recovered"] = columns[6].text.strip()
            row_data["New Recovered"] = columns[7].text.strip()
            row_data["Active Cases"] = columns[8].text.strip()
            row_data["Serious Critical"] = columns[9].text.strip()
            row_data["Cases/1M pop"] = columns[10].text.strip()
            row_data["Deaths/1M pop"] = columns[11].text.strip()
            row_data["Total Tests"] = columns[12].text.strip()
            row_data["Tests/1M pop"] = columns[13].text.strip()
            row_data["Population"] = columns[14].text.strip()
            data.append(row_data)

    return data


def write_to_json(data):
    with open("covid_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("მონაცემები წარმატებით შეინახა.")


def display_notification(deaths, cases):
    toaster = ToastNotifier()
    message = f"გარდაცვლილთა ოდენობა: {deaths}\n დაავადებულთა რაოდენობა: {cases}"
    toaster.show_toast("COVID-19 Update", message, duration=10)


def cxrili(connection):
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS CovidData (
                        Country TEXT,
                        TotalCases TEXT,
                        NewCases TEXT,
                        TotalDeaths TEXT,
                        NewDeaths TEXT,
                        TotalRecovered TEXT,
                        NewRecovered TEXT,
                        ActiveCases TEXT,
                        SeriousCritical TEXT,
                        CasesPerMillion TEXT,
                        DeathsPerMillion TEXT,
                        TotalTests TEXT,
                        TestsPerMillion TEXT,
                        Population TEXT
                    )''')

    connection.commit()


def insert(connection, data):
    cursor = connection.cursor()

    for row in data:
        values = [row['Country'], row['Total Cases'], row['New Cases'], row['Total Deaths'], row['New Deaths'],
                  row['Total Recovered'], row['New Recovered'], row['Active Cases'], row['Serious Critical'],
                  row['Cases/1M pop'], row['Deaths/1M pop'], row['Total Tests'], row['Tests/1M pop'], row['Population']]
        cursor.execute('INSERT INTO CovidData VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', values)

    connection.commit()

data = scrape_data()

write_to_json(data)

deaths = data[0]['Total Deaths']
cases = data[0]['Total Cases']
display_notification(deaths, cases)

connection = sqlite3.connect('covid_data.db')

cxrili(connection)

insert(connection, data)


connection.close()

print("მონაცემები წარმატებით შეინახა მონაცემთა ბაზაში.")