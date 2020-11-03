#! env python

import requests
import re
import os.path as path
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

####
# strikes and protests days:
# * https://es.wikipedia.org/wiki/Protestas_en_Argentina_de_2020
#
###


class Covid:
    def __init__(self, covid_data=None):
        self.covid_data = covid_data if covid_data is not None\
            else 'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/Argentina_medical_cases'
        self.tmp_covid_data = './raw_data_tmp'
        self.special_dates = ['2020-03-23', '2020-03-24',
                              '2020-03-31', '2020-04-09',
                              '2020-04-10', '2020-04-24',
                              '2020-05-01', '2020-05-25',
                              '2020-06-15', '2020-07-09',
                              '2020-07-10', '2020-08-17',
                              '2020-10-12', '2020-11-23',
                              '2020-12-07', '2020-12-08',
                              '2020-12-25', '2020-06-20',
                              '2020-08-26', '2020-09-02',
                              '2020-09-13', '2020-09-19']

    def proc(self):
        covid = dict()
        if not path.exists(self.tmp_covid_data) or (time.time() - int(path.getmtime(self.tmp_covid_data))) > 84600:
            raw_data = requests.get(self.covid_data)
            raw_data = raw_data.text
            with open(self.tmp_covid_data, 'w') as fd:
                fd.write(raw_data.encode('utf-8').decode('ascii', 'ignore'))
        else:
            with open(self.tmp_covid_data, 'r', encoding='utf-8') as fd:
                raw_data = ""
                for line in fd.readlines():
                    raw_data += line
        line_flag = False
        day_flag = False
        day_counter = 0
        date_tmp = ""
        for line in raw_data.splitlines():
            if re.search(r'Confirmed cumulative infections', line):
                line_flag = True
            if line_flag:
                if re.search(r'wikitable', line):
                    line_flag = True
                if line_flag:
                    rsearch = re.search(r'<th>(\d+ \w{3})\s*$', line)
                    if rsearch:
                        date_tmp = rsearch.group(1)
                        date_tmp = re.sub(r'(\d \D{3})', r'\1', date_tmp)
                        date_tmp = datetime.datetime.strptime(date_tmp + " 2020", "%d %b %Y").strftime("%Y-%m-%d")
                        covid[date_tmp] = dict()
                        day_flag = True
                        day_counter = 0

                    if day_flag:
                        day_counter += 1

                        if day_counter == 29:
                            tmp = re.sub(r'\D+(\d+)\D*', r'\1', line)
                            if not tmp.isdigit():
                                tmp = 0
                            covid[date_tmp]["C"] = tmp
                        elif day_counter == 30:
                            tmp = re.sub(r'\D+(\d+)\D*', r'\1', line)
                            if not tmp.isdigit():
                                tmp = 0
                            covid[date_tmp]["D"] = tmp
        covid_dates = dict()
        for t in covid.keys():
            #covid[t]["date"] = t
            if t in self.special_dates:
                covid_dates[t] = dict()
                covid_dates[t]["S"] = covid[t]['C']

        covid_df = pd.DataFrame.from_dict(covid, dtype="int32")
        covid_df = covid_df.transpose()
        covid_df = covid_df.sort_index()
        covid_df = covid_df.astype(int)
        covid_df_dates = pd.DataFrame.from_dict(covid_dates, dtype="int32")
        covid_df_dates = covid_df_dates.transpose()
        covid_df_dates = covid_df_dates.sort_index()
        covid_df_dates = covid_df_dates.astype(int)
        print(covid_df_dates)
        covid_df_dates.index.name = "dates"

        covid_df.index.name = "dates"
        print(covid_df_dates)
        print(covid_df.info())
        fig, ax = plt.subplots()
        covid_df["C"].plot()
        covid_df['D'].plot()
        #covid_df_dates.plot()
        plt.show()



if __name__ == '__main__':
    cv = Covid()
    cv.proc()
