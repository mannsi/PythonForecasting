from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import forecast.data_manipulation.group as grp

date1 = datetime.now() + timedelta(days=1)
date2 = datetime.now() + timedelta(days=2)
date3 = datetime.now() + timedelta(days=3)
date4 = datetime.now() + timedelta(days=4)
date5 = datetime.now() + timedelta(days=5)
date6 = datetime.now() + timedelta(days=6)
date7 = datetime.now() + timedelta(days=7)
date8 = datetime.now() + timedelta(days=8)
date9 = datetime.now() + timedelta(days=9)

times = [date1,date2,date3,date4,date5,date6,date7,date8,date9]
values = [5,10,13,7,18,8,22,13,7]
values2 = [None,None,None,74,75,8,22,13,7]
fig, ax = plt.subplots(1)
fig.autofmt_xdate()

weeks, values = grp.by_week_sums(times, values)
weeks2, values2 = grp.by_week_sums(times, values2)

plt.plot(weeks, values, label="Real", marker='o')
plt.plot(weeks, values2, label="AGR predict", marker='o')
plt.legend(bbox_to_anchor=(0.8, 1), loc=2, borderaxespad=0.)

xfmt = mdates.DateFormatter('%d-%m-%y')
ax.xaxis.set_major_formatter(xfmt)
plt.show()