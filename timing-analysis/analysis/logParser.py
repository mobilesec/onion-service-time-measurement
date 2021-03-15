import threading, queue, re, time

DEBUG_LOG_PATH = '/var/log/tor/debug.log'
INTRO_ESTABLISHED_REGEX = '([A-Za-z]{2,3} [0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}.[0-9]{0,}) \[info\] service_handle_intro_established\(\): Successfully received an INTRO_ESTABLISHED cell on circuit ([0-9]{1,}) \(id: ([0-9]{1,})\)'
START_SERVICE_NON_EPHEMERAL_REGEX = 'build_descriptors_for_new_service\(\): Hidden service ([a-z0-9]{56})'
START_SERVICE_EPHEMERAL_REGEX = 'hs_service_add_ephemeral\(\): Added ephemeral v[0-9] onion service: ([a-z0-9]{0,})'

# synchronized queue to get results back from thread
circuit_queue = queue.Queue()


def extractCircuitID(line):
    circuit_id = re.search(INTRO_ESTABLISHED_REGEX, str(line))

    # if there is a match, extract the circuit ID
    if circuit_id is not None:

        return [circuit_id.group(1), circuit_id.group(3)]
    else:
        return None


def parseLog(file_path, circuit_queue):
    with open(file_path) as infile:
        for line in infile:
            circuit_id = extractCircuitID(line)
            if circuit_id is not None:
                # we found a circuit ID from an introduction circuit
                circuit_queue.put(circuit_id)


def startParsing():
    if circuit_queue.empty():
        log_t = threading.Thread(target=parseLog, args=(DEBUG_LOG_PATH, circuit_queue))
        log_t.start()
        log_t.join()
        return list(circuit_queue.queue)
