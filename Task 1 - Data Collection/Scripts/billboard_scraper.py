import csv
import sys
import billboard
import datetime
import asyncio

charts_data = {}

async def add_chart(chart_name, date):
    chart = billboard.ChartData(chart_name, date=date)
    for song in chart:
        if (song.title, song.artist) not in charts_data:
            charts_data[(song.title, song.artist)] = {}
        charts_data[(song.title, song.artist)][date] = song.rank
    print(date)

async def main(chart_names, beg_date, end_date):
    date = datetime.datetime.fromisoformat(end_date)
    date_f = date.strftime("%Y-%m-%d")
    week = datetime.timedelta(days=7)
    dates = []

    while date_f > beg_date:
        dates.append(date_f)
        date -= week
        date_f = date.strftime("%Y-%m-%d")

    for chart_name in chart_names:
        await asyncio.gather(*(add_chart(chart_name,i) for i in dates))

    result = [['title', 'artist']+[date for date in dates]+['count']]
    date2index = {key:value for key,value in [(date,result[0].index(date)) for date in dates]}

    for k, v in charts_data.items():
        new_row = [k[0], k[1]] + [-1]*len(dates)
        for d, r in v.items():
            new_row[date2index[d]] = r
        new_row.append(sum(i > -1 for i in new_row[2:]))
        result.append(new_row)

    with open("billboard.csv", "w", newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(result)

if __name__ == "__main__":
    asyncio.run(main(["hot-100"],sys.argv[1],sys.argv[2]))