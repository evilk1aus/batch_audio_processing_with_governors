import matplotlib.pyplot as plt
import json

stats = []
count = -1

with open("stats.json") as f:
    stats = json.loads(f.read())
    count = stats["count"]

x = [x + 1 for x in range(count)]
y = stats["host"]

plt.plot(x, y, marker='o', linestyle='-', color='blue')
plt.xlabel("Time (s)")
plt.ylabel("Energy (W)")
plt.title("Host Power Consumption")
plt.grid(True)

plt.show()

colors = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#7f7f7f",  # gray
    "#bcbd22",  # olive
    "#17becf",  # cyan

    "#000000",  # black
    "#ffd700",  # gold
    "#00ff00",  # lime
    "#ff00ff",  # magenta
    "#00ffff",  # aqua
    "#ff1493",  # deep pink
]

for core_num in stats["frequency"]:
	plt.plot(x, stats["frequency"][core_num], label=f"Core {int(core_num)+1}", marker='o', linestyle='-', color=colors[int(core_num) % len(colors)])
plt.xlabel("Time (s)")
plt.ylabel("Frequency (GHz)")
plt.title("Frequency over Time")

plt.legend()
plt.grid(True)

plt.show()

y = stats["temperature"]["acpitz"]

plt.plot(x, y, marker='o', linestyle='-', color='blue')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("CPU Temperature over Time")
plt.grid(True)

plt.show()


for core_num, core_usages in enumerate(stats["cpu_usage"]):
    plt.plot(x, core_usages, label=f"Core {int(core_num)+1}", marker='o', linestyle='-', color=colors[int(core_num) % len(colors)])

plt.xlabel("Time (s)")
plt.ylabel("Usage %")
plt.title("cpu_usage over Time")

plt.legend()
plt.grid(True)

plt.show()
