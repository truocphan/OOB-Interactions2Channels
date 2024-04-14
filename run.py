import os, time, re
import platform
import requests
import dload
import psutil


platformOS = platform.system().lower()
if platformOS == "darwin": platformOS = "macOS"

platformArch = platform.machine().lower()


for process in psutil.process_iter():
	if process.name() == "interactsh-client" + (".exe" if platformOS=="windows" else ""):
		process.kill()


if not os.path.isdir(f"./bin/interactsh-client/{platformOS}/{platformArch}"): os.makedirs(f"./bin/interactsh-client/{platformOS}/{platformArch}")
if not os.path.isdir(f"./bin/notify/{platformOS}/{platformArch}"): os.makedirs(f"./bin/notify/{platformOS}/{platformArch}")
if not os.path.isdir("./.config/interactsh-client"): os.makedirs("./.config/interactsh-client")
if not os.path.isdir("./.config/notify"): os.makedirs("./.config/notify")
if not os.path.isdir("./logs/interactsh-client"): os.makedirs("./logs/interactsh-client")


INTERACTSH_CLIENT =  os.path.normpath(f"./bin/interactsh-client/{platformOS}/{platformArch}/interactsh-client" + (".exe" if platformOS=="windows" else ""))
if not os.path.isfile(INTERACTSH_CLIENT):
	interactsh_ver = requests.get("https://api.github.com/repos/projectdiscovery/interactsh/releases/latest").json()["tag_name"][1:]
	dload.save_unzip(f"https://github.com/projectdiscovery/interactsh/releases/download/v{interactsh_ver}/interactsh-client_{interactsh_ver}_{platformOS}_{platformArch}.zip", f"./bin/interactsh-client/{platformOS}/{platformArch}")

NOTIFY =  os.path.normpath(f"./bin/notify/{platformOS}/{platformArch}/notify" + (".exe" if platformOS=="windows" else ""))
if not os.path.isfile(NOTIFY):
	notify_ver = requests.get("https://api.github.com/repos/projectdiscovery/notify/releases/latest").json()["tag_name"][1:]
	dload.save_unzip(f"https://github.com/projectdiscovery/notify/releases/download/v{notify_ver}/notify_{notify_ver}_{platformOS}_{platformArch}.zip", f"./bin/notify/{platformOS}/{platformArch}")


os.system(f"{INTERACTSH_CLIENT} -sf {os.path.normpath('./.config/interactsh-client/interactsh.session')} -v -o {os.path.normpath('./logs/interactsh-client/interactsh-logs.txt')} &")

while True:
	f = open("./logs/interactsh-client/interactsh-logs.txt", "r")
	content = f.read()
	f.close()

	if len(content) > 0:
		f = open("./logs/interactsh-client/interactsh-logs.txt", "w")
		f.write("")
		f.close()

		content = content.lstrip("\x00").rstrip("\n")
		records = re.split("\n\n\n(\[.+\] Received (?:DNS|HTTP|HTTPS|SMTP|SMTPS|LDAP) interaction)", content)

		f = open("./logs/interactsh-client/interactsh-record.txt", "w")
		f.write(records[0])
		f.close()
		os.system(f"{NOTIFY} -provider-config {os.path.normpath('./.config/notify/provider-config.yaml')} -silent -char-limit 10000 -bulk -data {os.path.normpath('./logs/interactsh/interactsh-record.txt')}")

		for i in range(1, len(records), 2):
			f = open("./logs/interactsh-client/interactsh-record.txt", "w")
			f.write(records[i] + records[i+1])
			f.close()
			os.system(f"{NOTIFY} -provider-config {os.path.normpath('./.config/notify/provider-config.yaml')} -silent -char-limit 10000 -bulk -data {os.path.normpath('./logs/interactsh-client/interactsh-record.txt')}")

	time.sleep(5)