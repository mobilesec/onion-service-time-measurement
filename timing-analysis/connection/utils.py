import sys
import stem.control
import stem.connection

"""
Establish a connection to the control port of tor and authenticate
"""
CONTROL_PORT = 9051
CONTROL_ADDRESS = '127.0.0.1'


def establish_connection(address=CONTROL_ADDRESS, port=CONTROL_PORT, password=None):
    # Get connection to tor via the control port
    try:
        # the explicit declaration of the port isn't necessary since it's the default port
        controller = stem.control.Controller.from_port(address, port)
    except stem.SocketError as exc:
        print(f" * Unable to connect to port control port 9051 ({exc})")
        sys.exit(1)

    if controller:
        # authenticate
        try:
            if (password != None):
                controller.authenticate(password=password)
            else:
                controller.authenticate()
            print(" * Connection established and authenticated")
            return controller
        except stem.connection.PasswordAuthFailed:
            print(" * Unable to authenticate, password is incorrect")
            sys.exit(1)
        except stem.connection.AuthenticationFailure as exc:
            print(f" * Unable to authenticate: {exc}")
            sys.exit(1)


"""
Create new ephemeral Hidden Service and return its onion id
"""


def create_ephemeral_hidden_service(controller, source_port, target_port, version):
    try:
        if version == 2:
            hs = controller.create_ephemeral_hidden_service({source_port: target_port}, await_publication=False,
                                                            key_type="NEW", key_content="RSA1024", detached=False)
        else:
            hs = controller.create_ephemeral_hidden_service({source_port: target_port}, await_publication=False,
                                                            detached=False)
        if (hs.service_id):
            return hs.service_id
        else:
            return -1

    except stem.ControllerError as exc:
        print(f"Unable to create the hidden service ({exc})")
        sys.exit(1)


def create_hidden_service(controller, path, port):
    try:
        controller.create_hidden_service(path, port, target_address='127.0.0.1')
    except stem.ControllerError as exc:
        print(f"Unable to create the hidden service ({exc})")
        sys.exit(1)