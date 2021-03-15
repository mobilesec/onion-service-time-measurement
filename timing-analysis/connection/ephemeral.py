import os
import shutil
import sys
import stem.control
import stem.connection
from flask import Flask
from utils import establish_connection

app = Flask(__name__)

# data structure for keeping track of the deployed identities
service_list = []

# constants
SOURCE_PORT = 80
TARGET_PORT = 5000
PASSWORD = 'tor'


@app.route('/')
def index():
    hs = create_ephemeral_hidden_service()
    return str(hs)+'\n' if hs != -1 else " * Unable to create the hidden service"


"""
Creates a new hidden service in a random directory inside the tor directory (/var/lib/tor)
and returns the hostname of the hiddenservice in case of a successful creation, -1 instead.
"""


def create_ephemeral_hidden_service():
    try:
        if (controller):
            hs = controller.create_ephemeral_hidden_service({SOURCE_PORT: TARGET_PORT}, await_publication=True, key_type='NEW', key_content='ED25519-V3')
            if (hs.service_id):
                print(f" * Service with id {hs.service_id} created")
                # add service_id to the service list
                service_list.append(hs.service_id)
                return hs.service_id + '.onion'
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
        for service_id in service_list:
            try:
                controller.remove_ephemeral_hidden_service(service_id)
            except stem.ControllerError as exc:
                print(f" * Unable to delete the hidden service ({exc})")
                sys.exit(1)
