"""
callback handler when a LOG event takes place
"""

import datetime
import queue
import re

# regex for intro points
INTRO_ESTABLISHED_REGEX_V3 = 'service_handle_intro_established\(\): Successfully received an INTRO_ESTABLISHED cell on circuit ([0-9]{1,}) \(id: ([0-9]{1,})\)'
INTRO_ESTABLISHED_REGEX_V2 = 'rend_service_intro_established\(\): Received INTRO_ESTABLISHED cell on circuit ([0-9]{1,}) \(id: ([0-9]{1,})\)'

intro_circuit_list = []

# synchronized queue for inter thread communication
thread_intro_circuit_q = queue.Queue()

"""
callback handler when a LOG event takes place
"""


def logCallback_v2(event):
    global intropoints_extracted

    timestamp = datetime.datetime.now()
    # extractIntroEstablishedCircuit(event.message)
    int_tmp = extractCircuitID(event.message, timestamp, 2)
    if int_tmp is not None:
        intro_circuit_list.append(int_tmp)
        # put new version into queue
        thread_intro_circuit_q.put(intro_circuit_list)


def logCallback_v3(event):
    global intropoints_extracted

    timestamp = datetime.datetime.now()
    # extractIntroEstablishedCircuit(event.message)
    int_tmp = extractCircuitID(event.message, timestamp, 3)
    if int_tmp is not None:
        intro_circuit_list.append(int_tmp)
        # put new version into queue
        thread_intro_circuit_q.put(intro_circuit_list)


"""
extract the circuit ID from a intro established log message and return a list with its timestamp and id
:param line: Log string
:param timestamp: timestamp when the controller received the log message
:return: list of timestanp and ID of intro circuit (global ID)
"""


def extractCircuitID(line, timestamp, version):
    if version == 3:
        circuit_id = re.search(INTRO_ESTABLISHED_REGEX_V3, str(line))
    else:
        circuit_id = re.search(INTRO_ESTABLISHED_REGEX_V2, str(line))

    # if there is a match, extract the circuit ID
    if circuit_id is not None:
        return [timestamp, circuit_id.group(2)]
    else:
        return None
