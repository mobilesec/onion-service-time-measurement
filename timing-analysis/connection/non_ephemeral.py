import os
import shutil
import sys
import secrets
import stem.control
import stem.connection
from flask import Flask
from utils import establish_connection

app = Flask(__name__)
# random number generator
rng = secrets.SystemRandom()
# data structure for keeping track of the deployed identities
service_list = []

# constants
SOURCE_PORT = 80
TARGET_PORT = 5000
PASSWORD = 'tor'


@app.route('/')
def index():
    hs = create_hidden_service()
    return str(hs)+'\n' if hs != -1 else " * Unable to create the hidden service"


"""
Creates a new hidden service in a random directory inside the tor directory (/var/lib/tor)
and returns the hostname of the hiddenservice in case of a successful creation, -1 instead.
"""


def create_hidden_service():
    dir = rng.randint(0, sys.maxsize)

    # if name duplication, new random value
    while dir in service_list:
        dir = rng.randint(0, sys.maxsize)

    # add directory name to the service list
    service_list.append(dir)

    try:
        if (controller):
            hs_dir = os.path.join(controller.get_conf('DataDirectory'), 'tmp', str(dir))
            hs = controller.create_hidden_service(path=hs_dir, port=SOURCE_PORT, target_port=TARGET_PORT)
            if (hs.hostname):
                print(f" * Service with directory {hs_dir} created")
                return hs.hostname
            else:
                return -1

    except stem.ControllerError as exc:
        print(f" * Unable to create the hidden service ({exc})")
        sys.exit(1)


try:
    # create handle for communication with tor process
    controller = establish_connection(password=PASSWORD)
    # run flask web server as thread, otherwise ipc necessary for the exchange of service_list
    app.run(threaded=True)

finally:
    # Shut down the hidden service and clean it off disk
    print(" * Shutting down the hidden services")
    if controller:
        for dir in service_list:
            hs_dir = os.path.join(controller.get_conf('DataDirectory'), 'tmp', str(dir))
            try:
                controller.remove_hidden_service(hs_dir)
            except stem.ControllerError as exc:
                print(f" * Unable to delete the hidden service ({exc})")
                sys.exit(1)
            try:
                shutil.rmtree(os.path.join(controller.get_conf('DataDirectory'), 'tmp', str(dir)), ignore_errors=True)
            except (OSError, os.error) as exc:
                print(f" * Unable to remove the hidden service folder ({exc})")
                sys.exit(1)
