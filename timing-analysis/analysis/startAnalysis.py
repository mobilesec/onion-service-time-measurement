import re
from analysis import start
from connection.utils import establish_connection
import sys

NOTICES_LOG_PATH = '/var/log/tor/notices.log'
BOOTSTRAP_REGEX = 'Bootstrapped 100\%'
PASSWORD = 'tor'

version = int(sys.argv[1])
ephemeral = sys.argv[2] == "true" or sys.argv[2] == "True" or sys.argv[2] == "TRUE"
timeout = int(sys.argv[3])
num_intro_points = int(sys.argv[4])

bootstrapped = False


def parseLog(file_path):
    global bootstrapped
    with open(file_path) as infile:
        for line in infile:
            if checkIfBoostrapped(line):
                bootstrapped = True

def checkIfBoostrapped(line):
    if re.search(BOOTSTRAP_REGEX, line) is not None:
        return True
    return False

while not bootstrapped:
    parseLog(NOTICES_LOG_PATH)

controller = establish_connection(password=PASSWORD)
print(f" * Number of circuits after bootstrapping: {len(controller.get_circuits())}")
print(" * Tor completely bootstrapped, starting analysis")

start(version, ephemeral, timeout, num_intro_points)
