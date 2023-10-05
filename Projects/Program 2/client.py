import argparse
import socket
import struct
from packet_handles import * # A "header" I made to reuse functions

# NOTE: this address would be '10.128.0.2'/'10.128.0.3' for my VMs to hit each
# other through the internal network they are on.
ADDRESS = '127.0.0.1'
PORT = 8080
KB = 1024

# Not sure why this function takes header_length as an argument, when we are using a set length of header, so I am using it for NULL buffer bits.
def create_packet(version: int, header_length: int, service_type: int, payload: str):
    if (header_length < 5): # If the header length is less than our minimum header size:
        argument_issue = 'Argument for --header_length was too small (make sure it is >= 5).'
        raise ValueError(header_length).add_note(argument_issue) # Value exception to catch in main.

    # Creating the fixed length header template with 3 unsigned integer bytes of data, and one 2 byte unsigned integer,
    # plus the header_length - 5 bytes of buffer space we need.
    header_template = struct.Struct('!3BH' + str(header_length - 5) + 'x')

    try:
        encoded_payload = encode_payload(payload, service_type)
    except TypeError: # This was already explained in the function, so simply rethrow.
        print('It appears the data could not be converted, to bytes, try again later.')

    # Creating a variable to store the size of the payload after we have encoded the payload.
    payload_length = len(encoded_payload)
    # NOTE: This is the number of BYTES, not number of values. For a string number of characters
    # is equal to number of bytes, but for int and float, that is not the case.

    # Creating the header based on the parameters.
    header = header_template.pack(version, header_length, service_type, payload_length)

    # NOTE: This could have also been done by using pack_into() to directly pack the payload into the header.
    packet = header + encoded_payload

    return packet

## MAIN BELOW:

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client for packet creation and sending.")
    parser.add_argument('--version', type=int, required=True, help='Packet version')
    parser.add_argument('--header_length', type=int, required=True, help='Length of the packet header')
    parser.add_argument('--service_type', type=int, required=True, help='Service type of the payload (1 for int, 2 for float, 3 for string)')
    parser.add_argument('--payload', type=str, required=True, help='Payload to be packed into the packet')
    parser.add_argument('--host', type=str, default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=12345, help='Server port')

    args = parser.parse_args()

    try: # Trying something new this time, I want to handle the exceptions at the end based on type.
        packet = create_packet(args.version, args.header_length, args.service_type, args.payload)

        with socket.socket() as client: # Trying this implementation

            for connect_attempts in range(1, 6): # Try to connect up to 5 times:
                try:
                    client.connect((ADDRESS, PORT)) # Connecting to the server.
                    break # If we manage to connect, hit this line and break out of the loop early.
                except socket.error as exc:
                    print('ATTEMPT %s: Failed to connect to server...' % connect_attempts)
                    print('Explanation:\n', exc)

            if (connect_attempts == 5): # If we failed to connect 5 times:
                raise ConnectionRefusedError('Server does not appear to be online, try again later.')

            try: # Try to do a communication cycle:
                client.send(packet)
                packet = client.recv(KB*KB)
            except socket.error as exc:
                raise ConnectionError('Failed to communicate with the server.') from exc

        # After we have handled everything with the socket, now we can focus on the data:

        # Handle the decoding of the packet and get the data, or an error code.
        data = handle_packet(packet)

        (header_data, payload_data) = data # Break the tuple so we can print.

        (version, header_length, service_type, payload_length) = header_data # Breaking the header tuple

        payload_string = payload_to_string(payload_data, service_type)

        print('\nHere is the header information from the server:')
        # Print the header tuple with the information separated.
        print('\nVersion: {}\nHeader length: {}\nService type: {}\nPayload size: {}'.format(*header_data))
        # Print the data string to the user.
        print('\nData: %s' % payload_string)
        # NOTE: I wanted to try doing a single tuple print, but I think this handle is clean as is.
        
    except ConnectionError as exc: # This will catch any errors with the sockets that we rethrew.
        print('Program ran into an error with the socket connection:')
        print(exc)
    except ValueError as exc: # This will catch most of the errors we raised due to bad calls
        print('It appears there was an issue within one of the function calls values:')
        print(exc)
    except BaseException as exc: # This catches all remaining exceptions that We missed.
        print('An unexpected error occured:')
        print(exc)