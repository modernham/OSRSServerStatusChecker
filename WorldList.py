from bs4 import BeautifulSoup
from threading import Thread
import subprocess
import collections
import requests
import queue
import re

ServerList = {}

class OSRSWorldPinger():
    def __init__(self):
        self.num_threads = 8
        self.ping_queue = queue.Queue()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        self.result = requests.get(url="http://oldschool.runescape.com/slu?order=WMLPA", headers=self.headers)
        self.soup = BeautifulSoup(self.result.content, "html.parser")

        self.server_list = {}

    # worker thread to ping servers with system command
    def thread_pinger(self, i, q):
        while True:
            world = q.get()
            address = "oldschool{}.runescape.com".format(world)

            command = "ping {} -n 1".format(address)
            try:
                output = subprocess.check_output(command, shell=True).decode('utf-8')
            except:
                print("Error")
            matches = re.findall("time=([\d.]+)ms", output)
            self.server_list[world]['ping'] = int(matches[0])

            q.task_done()

    # initiates server list with info pulled from osrs world selection website.
    def init_server_list(self):
        table = self.soup.findAll("tr", "server-list__row")

        for row in table:
            data = row.find_all("td", class_="server-list__row-cell")

            w = data[0].text.split()[-1]
            if not data[1].text:
                p = "FULL"
            else:
                p = data[1].text.split()[0]

            c, t, a = data[2].text, data[3].text, data[4].text
            self.server_list[w] = {"players": p, "country": c, "type": t, "activity": a, "ping": 0}

    # displays the top five servers with the lowest latencies.
    def get_best_servers(self):

        # sort server_list in ascending order by ping value
        d = collections.OrderedDict(sorted(self.server_list.items(), key=lambda t: t[1]['ping']))

        Worlds = []
        Pings = []
        Players = []
        Type = []
        Activity = []

        count = 0
        for key, value in d.items():
            if count < 230:
                Worlds.append((str(int(key) + 300)))
                Pings.append((value["ping"]))
                Type.append(value['type'])
                Players.append((value["players"]))
                Activity.append((value["activity"]))
                count += 1

        return[Worlds, Pings, Players, Type, Activity]



def pingWorlds():
    wp = OSRSWorldPinger()
    wp.init_server_list()

    # if user input is empty, ping all worlds
    for key in sorted(wp.server_list.keys()):
        wp.ping_queue.put(key)

    # start the thread pool
    for i in range(wp.num_threads):
        worker = Thread(target=wp.thread_pinger, args=(i, wp.ping_queue))
        worker.setDaemon(True)
        worker.start()

    # wait until worker threads are done to exit
    wp.ping_queue.join()

    # display info for all servers


    return wp.server_list


def getBest():
    wp = OSRSWorldPinger()
    wp.init_server_list()

    # if user input is empty, ping all worlds
    for key in sorted(wp.server_list.keys()):
        wp.ping_queue.put(key)

    # start the thread pool
    for i in range(wp.num_threads):
        worker = Thread(target=wp.thread_pinger, args=(i, wp.ping_queue))
        worker.setDaemon(True)
        worker.start()

    # wait until worker threads are done to exit
    wp.ping_queue.join()

    # display info for all servers

    return (wp.get_best_servers())

