import queue
import datetime

# synchronized queue for inter thread communication
thread_descriptors_q = queue.Queue()

descUploadEvents = []
descUploadedEvents = []
descCreatedEvents = []

"""
class for descriptor elements
"""


class descElement:
    def __init__(self, time_added, fingerprint):
        self.time_added = time_added
        self.fingerprint = fingerprint

    def getTime(self):
        return self.time_added

    def getFingerprint(self):
        return self.fingerprint


"""
callback handler when a DESC event takes place
"""


def descCallback(event):
    global descEvents
    # collected all required data, put it in a queue such that the main thread can read them
    # put new version into queue
    thread_descriptors_q.put(descCreatedEvents)
    thread_descriptors_q.put(descUploadEvents)
    thread_descriptors_q.put(descUploadedEvents)

    if event.action == "CREATED":
        descCreatedEvents.append(descElement(datetime.datetime.now(), None))
    elif event.action == "UPLOAD":
        descUploadEvents.append(descElement(datetime.datetime.now(), event.directory_fingerprint))
        print(f"[{datetime.datetime.now()}] action: {event.action} | descriptor: {event.descriptor_id} | replica: {event.replica}")
    elif event.action == "UPLOADED":
        descUploadedEvents.append(descElement(datetime.datetime.now(), event.directory_fingerprint))
        print(f"[{datetime.datetime.now()}] action: {event.action} | descriptor: {event.descriptor_id} | replica: {event.replica}")