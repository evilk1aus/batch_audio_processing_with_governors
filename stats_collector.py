import subprocess
import time
import json
import pty
import os

import pprint
import fcntl
import psutil

stats = {}
count = 0

master, slave = pty.openpty()

proc = subprocess.Popen(["sudo", "scaphandre", "json", "--timeout", "60", "-s", "1"],
		stdout=slave,
		stderr=subprocess.STDOUT,
		text=True
	)
os.close(slave)

new_reading = False

str_buff = ""

def parse_reading(json_result):
	if not "host" in stats:
		stats["host"] = []

	stats["host"].append(
		json_result["host"]["consumption"] * 1e-6 # convert to watts 
	)

	for socket in json_result["sockets"]:
		if not "sockets" in stats:
			stats["sockets"] = {}
			for s in json_result["sockets"]:
				stats["sockets"][s["id"]] = []

		socket["consumption"] *= 1e-6 # also convert to watts
		for domain in socket["domains"]:
			domain["consumption"] *= 1e-6

		stats["sockets"][socket["id"]].append(socket)

fcntl_flags = fcntl.fcntl(master, fcntl.F_GETFL)
fcntl.fcntl(master, fcntl.F_SETFL, fcntl_flags | os.O_NONBLOCK)

extract_and_augment_process = subprocess.Popen(["bash", "./extract_and_augment.sh"])

while True:
	if extract_and_augment_process.poll() is not None:
		print("Extract and augment process exited with:", extract_and_augment_process.returncode)
		proc.terminate()
		break

	try:
		data = os.read(master, 8192)
	except BlockingIOError:
		time.sleep(0.1)
		continue
	except OSError:
		break
	data = data.decode()
	if data.startswith("[1;31mScaphandre json exporter"):
		continue

	# New reading
	if data.startswith(",{\"host\":{"):
		if str_buff.startswith("{\"host\":{"):
			json_result = json.loads(str_buff)
			#print(json.dumps(json_result, indent=2).replace("\n","\r\n"))
			parse_reading(json_result)

			# Read frequencies
			freq_result = [int(x) / 1_000_000 # To GHz
							for x in subprocess.run(["sh", "-c", "cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq"],
									capture_output=True,
									text=True,
								) \
									.stdout \
									.split()
							]

			if not "frequency" in stats:
				stats["frequency"] = {}
				for i in range(len(freq_result)):
					stats["frequency"][i] = []

			for i in range(len(freq_result)):
				stats["frequency"][i].append(freq_result[i])

			# and temperature too
			temp_result = [x.split()
							for x in subprocess.run(["bash", "-c", "paste <(cat /sys/class/thermal/thermal_zone*/type) <(cat /sys/class/thermal/thermal_zone*/temp)"],
									capture_output=True,
									text=True,
								) \
									.stdout \
									.strip()
									.split("\n")
							]

			if not "temperature" in stats:
				stats["temperature"] = {}

			for result in temp_result:
				# Check if device temperature name is in stats
				if not result[0] in stats["temperature"]:
					stats["temperature"][result[0]] = []

				# temperature in celsius is in result[0]
				stats["temperature"][result[0]].append(int(result[1]) / 1000) # to Celsius

			# and CPU usage too
			usage_per_core = psutil.cpu_percent(interval=None, percpu=True)

			if not "cpu_usage" in stats:
				stats["cpu_usage"] = [[] for x in range(len(usage_per_core))]

			for i, usage in enumerate(usage_per_core):
				stats["cpu_usage"][i].append(usage)

			#print(stats["cpu_usage"], end="\r\n")

			#print(stats["temperature"])

			count += 1
		#print("====================================\r")
		str_buff = data[1:]
	else:
		str_buff += data

print("scaphandre exit code:", proc.wait())

stats["count"] = count

print("Saving to stats.json...")

import datetime

# Save stats to json files
with open(f"stats-{datetime.datetime.now().isoformat().replace(":", "_")}.json", "w") as f:
	f.write(json.dumps(stats, indent=2))

with open("stats.json", "w") as f:
	f.write(json.dumps(stats, indent=2))

print("stats.json saved!")
