import time
import csv
import re
import datetime

# default timeout after 5 minutes (300s)
TIMEOUT = 300

# default number of intro points is currently 3
NUM_OF_INTRO_POINTS = 3

from connection.utils import establish_connection
from stem.control import EventType
from circuitAnalyzer import circCallback
from logAnalyzer import logCallback_v3
from logAnalyzer import logCallback_v2
from descriptorAnalyzer import descCallback
from logAnalyzer import thread_intro_circuit_q
from circuitAnalyzer import thread_circuit_list_q
from circuitAnalyzer import thread_upload_circuit_q
from descriptorAnalyzer import thread_descriptors_q
from circuitAnalyzer import circMinorCallback
from connection.utils import create_ephemeral_hidden_service
from connection.utils import create_hidden_service

# password for control port authentication
PASSWORD = 'tor'

# regex for ipv4 address in desc event
UPLOAD_REGEX = '([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ([0-9]{3,4})'

# V3
NUM_OF_CREATE_EVENT_V3 = 2
NUM_OF_UPLOAD_EVENTS_V3 = 16
NUM_OF_UPLOADED_EVENTS_V3 = 16

# V2
NUM_OF_CREATE_EVENT_V2 = 2
NUM_OF_UPLOAD_EVENTS_V2 = 6
NUM_OF_UPLOADED_EVENTS_V2 = 6

controller = None

# filepath of output csv file
CSV_PATH = "/tmp/provisioning_time_" + time.strftime("%Y_%m_%d_%H_%M", time.localtime()) + ".csv"


def checkDictEntries(dictionary, csv_field_name):
    for entry in csv_field_name:
        if entry not in dictionary:
            dictionary[entry] = "FAIL"


def start(version, ephemeral, timeout, num_intro_points):
    global controller, TIMEOUT, NUM_OF_INTRO_POINTS
    csv_dict = {}
    startTime = time.time()

    # placeholder for the lists
    intro_point_list = []
    descriptor_create_list = []
    descriptor_upload_list = []
    descriptor_uploaded_list = []
    hsdir_upload_circuit_list = []

    # if timeout is provided by parameters use this one, otherwise the default timeout (360s) is used
    if timeout is not None and isinstance(timeout, int):
        TIMEOUT = timeout

    # if a custom number of intro points is provided, use it, otherwise use the default (3)
    if num_intro_points is not None and isinstance(timeout, int):
        NUM_OF_INTRO_POINTS = num_intro_points

    # csv header names
    CSV_FIELD_NAME_V3 = ['service_initiated']

    for i in range(1, NUM_OF_INTRO_POINTS + 1):
        CSV_FIELD_NAME_V3.append('intro_' + str(i) + '_build_start')
        CSV_FIELD_NAME_V3.append('intro_' + str(i) + '_build_end')

    for i in range(1, NUM_OF_INTRO_POINTS + 1):
        CSV_FIELD_NAME_V3.append('intro_' + str(i) + '_established')

    CSV_FIELD_NAME_V3.extend(['desc_1_created', 'desc_2_created', 'upload_hs_1',
                              'uploaded_hs_1',
                              'upload_hs_2', 'uploaded_hs_2', 'upload_hs_3', 'uploaded_hs_3', 'upload_hs_4',
                              'uploaded_hs_4',
                              'upload_hs_5', 'uploaded_hs_5', 'upload_hs_6', 'uploaded_hs_6', 'upload_hs_7',
                              'uploaded_hs_7',
                              'upload_hs_8', 'uploaded_hs_8', 'upload_hs_9', 'uploaded_hs_9', 'upload_hs_10',
                              'uploaded_hs_10', 'upload_hs_11', 'uploaded_hs_11', 'upload_hs_12', 'uploaded_hs_12',
                              'upload_hs_13',
                              'uploaded_hs_13', 'upload_hs_14', 'uploaded_hs_14', 'upload_hs_15', 'uploaded_hs_15',
                              'upload_hs_16',
                              'uploaded_hs_16', 'upload_hs_1_hsdir_addr', 'upload_hs_2_hsdir_addr',
                              'upload_hs_3_hsdir_addr',
                              'upload_hs_4_hsdir_addr', 'upload_hs_5_hsdir_addr', 'upload_hs_6_hsdir_addr',
                              'upload_hs_7_hsdir_addr', 'upload_hs_8_hsdir_addr', 'upload_hs_9_hsdir_addr',
                              'upload_hs_10_hsdir_addr', 'upload_hs_11_hsdir_addr', 'upload_hs_12_hsdir_addr',
                              'upload_hs_13_hsdir_addr', 'upload_hs_14_hsdir_addr', 'upload_hs_15_hsdir_addr',
                              'upload_hs_16_hsdir_addr'])

    for i in range(1, 17):
        CSV_FIELD_NAME_V3.append(f"upload_hs_{i}_path")
        CSV_FIELD_NAME_V3.append(f"upload_hs_{i}_circuit_built")

    CSV_FIELD_NAME_V2 = ['service_initiated']

    for i in range(1, NUM_OF_INTRO_POINTS + 1):
        CSV_FIELD_NAME_V2.append('intro_' + str(i) + '_build_start')
        CSV_FIELD_NAME_V2.append('intro_' + str(i) + '_build_end')

    for i in range(1, NUM_OF_INTRO_POINTS + 1):
        CSV_FIELD_NAME_V2.append('intro_' + str(i) + '_established')

    CSV_FIELD_NAME_V2.extend(['desc_1_created', 'desc_2_created', 'upload_hs_1', 'uploaded_hs_1',
                              'upload_hs_2', 'uploaded_hs_2', 'upload_hs_3', 'uploaded_hs_3', 'upload_hs_4',
                              'uploaded_hs_4',
                              'upload_hs_5', 'uploaded_hs_5', 'upload_hs_6', 'uploaded_hs_6', 'upload_hs_1_hsdir_addr',
                              'upload_hs_2_hsdir_addr', 'upload_hs_3_hsdir_addr',
                              'upload_hs_4_hsdir_addr', 'upload_hs_5_hsdir_addr', 'upload_hs_6_hsdir_addr'])

    for i in range(1, 7):
        CSV_FIELD_NAME_V2.append(f"upload_hs_{i}_path")
        CSV_FIELD_NAME_V3.append(f"upload_hs_{i}_circuit_built")

    # connect and authenticate
    controller = establish_connection(password=PASSWORD)
    csv_dict['service_initiated'] = datetime.datetime.now()

    # add event listeners
    controller.add_event_listener(circCallback, EventType.CIRC)
    controller.add_event_listener(descCallback, EventType.HS_DESC)
    controller.add_event_listener(circMinorCallback, EventType.CIRC_MINOR)
    if version == 3:
        controller.add_event_listener(logCallback_v3, EventType.DEBUG)
    else:
        controller.add_event_listener(logCallback_v2, EventType.DEBUG)

    # create hidden service
    if ephemeral == False and version == 3:
        create_hidden_service(controller, '/var/lib/tor', 80)
    else:
        create_ephemeral_hidden_service(controller, 80, 80, version)

    print(" * Onion Service created")

    # number of required events for V2/V3
    if version == 3:
        createEvent = NUM_OF_CREATE_EVENT_V3
        uploadEvents = NUM_OF_UPLOAD_EVENTS_V3
        uploadedEvents = NUM_OF_UPLOADED_EVENTS_V3
    else:
        createEvent = NUM_OF_CREATE_EVENT_V2
        uploadEvents = NUM_OF_UPLOAD_EVENTS_V2
        uploadedEvents = NUM_OF_UPLOADED_EVENTS_V2

    # loop while the required data is received
    while True:
        if time.time() - startTime > TIMEOUT:
            print(" * One of many of the uploads timed out")
            break

        if thread_circuit_list_q.qsize() > 1:
            circuit_list = thread_circuit_list_q.get()
            thread_circuit_list_q.queue.clear()

        if thread_intro_circuit_q.qsize() > 1:
            intro_point_list = thread_intro_circuit_q.get()
            thread_intro_circuit_q.queue.clear()

        if thread_descriptors_q.qsize() > 3:
            descriptor_create_list = thread_descriptors_q.get()
            descriptor_upload_list = thread_descriptors_q.get()
            descriptor_uploaded_list = thread_descriptors_q.get()
            thread_descriptors_q.queue.clear()

        if not thread_upload_circuit_q.empty():
            hsdir_upload_circuit_list.append(thread_upload_circuit_q.get())

        if len(intro_point_list) >= 3 and len(descriptor_create_list) == 2 and len(
                descriptor_upload_list) == uploadEvents and len(descriptor_uploaded_list) == uploadedEvents:
            print(" * All required data available, starting correlation")
            break

    # clean up, remove event listeners (commented, because it was blocking some times, don't know why)
    controller.remove_event_listener(circCallback)
    controller.remove_event_listener(descCallback)
    controller.remove_event_listener(circMinorCallback)
    if version == 3:
        controller.remove_event_listener(logCallback_v3)
    else:
        controller.remove_event_listener(logCallback_v2)

    """
    correlates an element form the uploaded list with a provided fingerprint and returns the matched element

    :param uploaded_list: List of uploaded descriptors
    :param fingerprint: Fingerprint from the upload list to correlate
    :return: Element from the uploaded list that has the same fingerprint as the element from the upload list
    """

    def correlateFingerprint(uploaded_list, fingerprint):
        for elem in uploaded_list:
            if elem.fingerprint == fingerprint:
                return elem
        return None

    # read data from the various lists and put the into a dict uniformly that their values can be written to a CSV file
    for i in range(0, createEvent):
        csv_dict["desc_" + str(i + 1) + "_created"] = (descriptor_create_list[i]).getTime()
        i += 1

    for i in range(0, uploadEvents):
        if i <= len(descriptor_upload_list) - 1:
            csv_dict["upload_hs_" + str(i + 1)] = descriptor_upload_list[i]
            try:
                hsdir_addr = re.search(UPLOAD_REGEX, str(
                    controller.get_network_status(relay=descriptor_upload_list[i].getFingerprint())))
                if hsdir_addr:
                    csv_dict["upload_hs_" + str(i + 1) + "_hsdir_addr"] = str(hsdir_addr.group(1)) + ":" + str(
                        hsdir_addr.group(2))
                else:
                    csv_dict["upload_hs_" + str(i + 1) + "_hsdir_addr"] = "FAIL"
            except:
                csv_dict["upload_hs_" + str(i + 1) + "_hsdir_addr"] = "FAIL"
        else:
            csv_dict["upload_hs_" + str(i + 1)] = 'FAIL'
            csv_dict["upload_hs_" + str(i + 1) + "_hsdir_addr"] = 'FAIL'

    for i in range(0, len(hsdir_upload_circuit_paths)):
        # to upload circuit path is contained in the fingerprint attribute, while the upload circuit built timestamp is contained in the objects time stamp
        csv_dict[f"upload_hs_{i + 1}_circuit_built"] = hsdir_upload_circuit_list[i].getTime()
        csv_dict[f"upload_hs_{i + 1}_path"] = str(hsdir_upload_circuit_list[i].getFingerprint())

    for i in range(0, uploadedEvents):
        if i <= len(descriptor_uploaded_list) - 1:
            if csv_dict["upload_hs_" + str(i + 1)] != 'FAIL' and correlateFingerprint(descriptor_uploaded_list, str(
                    csv_dict["upload_hs_" + str(i + 1)].getFingerprint())):
                csv_dict["uploaded_hs_" + str(i + 1)] = correlateFingerprint(descriptor_uploaded_list, str(
                    csv_dict["upload_hs_" + str(i + 1)].getFingerprint())).getTime()
                csv_dict["upload_hs_" + str(i + 1)] = csv_dict["upload_hs_" + str(i + 1)].getTime()
            else:
                csv_dict["upload_hs_" + str(i + 1)] = "FAIL"
        else:
            if csv_dict["upload_hs_" + str(i + 1)] != 'FAIL':
                csv_dict["upload_hs_" + str(i + 1)] = csv_dict["upload_hs_" + str(i + 1)].getTime()
            csv_dict["uploaded_hs_" + str(i + 1)] = 'FAIL'

    for i in range(0, NUM_OF_INTRO_POINTS):
        if i <= len(intro_point_list) - 1:
            csv_dict["intro_" + str(i + 1) + "_established"] = intro_point_list[i][0]
            csv_dict["intro_" + str(i + 1) + "_build_start"] = circuit_list[str(intro_point_list[i][1])][0].getTime()
            csv_dict["intro_" + str(i + 1) + "_build_end"] = circuit_list[str(intro_point_list[i][1])][-1].getTime()
        else:
            csv_dict["intro_" + str(i + 1) + "_established"] = "FAIL"
            csv_dict["intro_" + str(i + 1) + "_build_start"] = "FAIL"
            csv_dict["intro_" + str(i + 1) + "_build_end"] = "FAIL"

            # write output to csv file
    print(" * Correlation performed, writing results to CSV file")

    # check if all mandatory fields are set, if not set them to FAIL
    if version == 3:
        checkDictEntries(csv_dict, CSV_FIELD_NAME_V3)
    else:
        checkDictEntries(csv_dict, CSV_FIELD_NAME_V2)

    if version == 3:
        with open(CSV_PATH, 'w', newline='') as csvfile:
            logwriter = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                       fieldnames=CSV_FIELD_NAME_V3)
            logwriter.writeheader()
            logwriter.writerow(csv_dict)
    else:
        with open(CSV_PATH, 'w', newline='') as csvfile:
            logwriter = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                       fieldnames=CSV_FIELD_NAME_V2)
            logwriter.writeheader()
            logwriter.writerow(csv_dict)
