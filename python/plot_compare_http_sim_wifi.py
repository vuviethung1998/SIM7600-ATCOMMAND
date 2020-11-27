import sys
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.function_base import average

fileName = 'http_sim_wifi.txt'
if len(sys.argv) >= 2:
    fileName = sys.argv[1]

field1 = []
field2 = []
field3 = []
info = ''

with open(fileName, mode="r", encoding="utf-8") as f:
    data = f.readlines()
    for d in data[:-1]:
        d = d.split(",")
        field1.append(int(d[0]))
        field2.append(int(d[1]))
        field3.append(int(d[2]))
    info = data[-1]
        
field1 = np.array(field1)
field2 = np.array(field2)
field3 = np.array(field3)

plt.ylabel("time (ms)")
plt.xlabel("")
plt.title(info)

plt.plot(field1, color="orange")
plt.plot(field2, color="blue")
plt.plot(field3, color="green")

maximum1 = np.max(field1)
minimum1 = np.min(field1)
maximum2 = np.max(field2)
minimum2 = np.min(field2)
maximum3 = np.max(field3)
minimum3 = np.min(field3)

legend1 = 'WiFi (ms): min={} max={} avr={}'.format(minimum1, maximum1, int(average(field1)))
legend2 = 'SIM  (ms): min={} max={} avr={}'.format(minimum2, maximum2, int(average(field2)))
legend3 = 'Sum  (ms): min={} max={} avr={}'.format(minimum3, maximum3, int(average(field3)))

plt.legend([legend1, legend2, legend3])
plt.grid(color="grey", linewidth=1, axis="x", alpha=0.1)
plt.show()
