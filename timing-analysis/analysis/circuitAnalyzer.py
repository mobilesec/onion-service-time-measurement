import datetime
import re
import queue

# global dictionary for circuits
circuits = {}

# regex for fingerprint
FINGERPRINT_REGEX = '[A-z0-9]{40}'

# synchronized queue for inter thread communication
thread_circuit_list_q = queue.Queue()

# synchronized queue for tor upload circuits
thread_upload_circuit_q = queue.Queue()

"""
class for circuit elements
"""


class circuitElement:
    def __init__(self, time_added, fingerprint):
        self.__time_added = time_added
        self.__fingerprint = fingerprint

    def getTime(self):
        return self.__time_added

    def getFingerprint(self):
        return self.__fingerprint


"""
callback handler when a CIRC event takes place
"""


def circCallback(event):
    global circuits
    # save timestamp of the event
    timestamp = datetime.datetime.now()

    # write to queue such that the main thread has access to the circuit list
    if len(circuits) > 0:
        # put new version into queue
        thread_circuit_list_q.put(circuits)

    # circuits for finding introduction points
    if event.purpose == "HS_SERVICE_INTRO":
        # Circuit is new, add new entry to global circuit dictionary
        if event.status == "LAUNCHED":
            circuits[event.id] = []
        # circuit is extended
        elif event.status == "EXTENDED":
            circuits[event.id].append(circuitElement(timestamp, extractFingerprint(event.path)))
        # circuit failed or closed, delete entry from dictionary
        elif event.status == "FAILED" or event.status == "CLOSED":
            circuits.pop(event.id)

    if event.purpose == "HS_SERVICE_HSDIR":
        if event.status == "LAUNCHED":
            print(f"[{datetime.datetime.now()}] CircuitEvent: {event.id} | status: {event.status} | purpose: {event.purpose} | path: {event.path}")
        if event.status == "BUILT":
            # in this case the fingeprint attribute is misued for the upload circuit path
            thread_upload_circuit_q.put(circuitElement(timestamp, event.path))
            print(f"[{datetime.datetime.now()}] CircuitEvent: {event.id} | status: {event.status} | purpose: {event.purpose} | path: {event.path}")
        elif event.status == "FAILED":
            # One Upload failed, so a new attempt will be made.
            # thread_upload_circuit_q.put("FAIL")
            print(f"[{datetime.datetime.now()}] CircuitEvent: {event.id} | status: {event.status} | purpose: {event.purpose} | path: {event.path}")


"""
callback handler when a CIRC MINOR event takes place
"""


def circMinorCallback(event):
    global circuits
    if not event.id in circuits:
        if event.event == 'CANNIBALIZED':
            path_list = extractFingerprint(event.path, cannibalized=True)
            circuits[event.id] = []
            for elem in path_list:
                circuits[event.id].append(circuitElement(str(datetime.datetime.now()) + " (CAN)", elem))


"""
extracts the fingerprint from a path string that is not yet in the specific circuits lists

:param path: Path string of the CIRC event
:return: Fingerprint
"""


def extractFingerprint(path, cannibalized=False):
    fingerprint_re = re.compile(FINGERPRINT_REGEX)
    path_list = re.findall(fingerprint_re, str(path))

    if len(path_list) > 0 and not cannibalized:
        return path_list[-1]
    elif len(path_list) > 0 and cannibalized:
        return path_list


"""
print all the circuits and their paths
"""


def printCircuitList():
    for circuit in circuits:
        print(f"# {circuit}")
        for relay in circuits[circuit]:
            print(f" {relay.getTime()}: [{relay.getFingerprint()}]")
        print("\n")
