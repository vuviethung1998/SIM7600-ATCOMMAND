import sys
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.function_base import average

fileName = 'http_sim.txt'
if len(sys.argv) >= 2:
    fileName = sys.argv[1]

start_time = []
end_time = []
interval = []
statusCode = []
info = ''
info_cqs = ''

with open(fileName, mode="r", encoding="utf-8") as f:
    data = f.readlines()
    for d in data[:-2]:
        d = d.split(",")
        start_time.append(int(d[0]))
        end_time.append(int(d[1]))
        interval.append(int(d[2]))
        statusCode.append(int(d[3]))
    info = data[-1]
    info_cqs = data[-2]

start_time = np.array(start_time)
end_time = np.array(end_time)
interval = np.array(interval)
statusCode = np.array(statusCode)

maximum1 = np.max(interval)
minimum1 = np.min(interval)
legend1 = '(ms): min={} max={} avr={}'.format(minimum1, maximum1, int(average(interval)))

plt.ylabel("time (ms)")
plt.xlabel("")
plt.title(info + '\n' + info_cqs + legend1)

# plt.plot(interval, color="orange")
plt.legend([legend1])
plt.grid(color="grey", linewidth=1, axis="x", alpha=0.1)

colormap = np.array(['r', 'g'])
plt.scatter(start_time, interval, 3, c=colormap[statusCode])

plt.show()

