import socket
import struct
from packet_handles import * # Same header as the client

# NOTE: this address would be '10.128.0.2'/'10.128.0.3' for my VMs to hit each
# other through the internal network they are on.
ADDRESS = "127.0.0.1"
PORT = 8080
KB = 1024

def unpack_packet(conn: socket, header_format: struct):

    # Attempting to recieve from client, not doing in a try..except so the main can catch the exception.
    packet = conn.recv(KB*KB)
    
    # Handle the packet breakdown and store as a tuple:
    data = handle_packet(packet, header_format)

    # NOTE: If I was to actually create the header as a string I would do so this way.
    header_string: str = '{},{},{},{}'.format(*data[0])
    # Then we can follow that up be tupling the header and payload.
    alt_data_format = (header_string, data[1])

    # I know it said return the payload, but then below said to return the header, so instead, I will use the tuple return.
    return data

if __name__ == '__main__':

    # Fixed length header -> Version (1 byte), Header Length (1 byte), Service Type (1 byte), Payload Length (2 bytes)
    header_format = struct.Struct('!3BH')  # TODO: Specify the header format using "struct"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ADDRESS, PORT))
        s.listen()
        while True: # Making sure the code actually continues to run after one connection closes:
            (conn, addr) = s.accept()
            with conn: # Had to research to understand this, and I really like the way "with" works.
                print(f"Connected by: {addr}")
                while True:
                    try: # Attempt to collect the packet data from the server:
                        (header_data, payload_data) = unpack_packet(conn, header_format)
                    except ValueError as exc: # If one of my function errors was hit:
                        print(exc) # Printing what the error was so that I can fix anything wrong.
                        break
                    except: # Otherwise we need to tell the user what happened:
                        print("Connection closed or an error occurred")
                        break

                    try: # This is to catch all the raises in the functions I created.

                        # Breaking up the tuple in case we need the data separately.
                        (version, header_length, service_type, payload_length) = header_data 

                        # Creating a new header from the header_data (NOTE this will end up the same as the other header).
                        header = header_format.pack(*header_data)

                        # Collecting the string of the payload from the data.
                        payload_string = payload_to_string(payload_data, service_type)

                        print('\nHere is the header information from the client:')
                        # Printing out all the header info seperated.
                        print('\nVersion: {}\nHeader length: {}\nService type: {}\nPayload size: {}'.format(*header_data))
                        # Printing out the packet data.
                        print('\nHere is the data the client sent in the packet:\n%s\n' % payload_string)

                        # Recreating the payload from the tuple.
                        payload = encode_payload(payload_string, service_type)

                        # Combining the parts into the packet.
                        packet = header + payload

                        # Sending the new packet back to the client.
                        conn.send(packet)

                    except Exception as exc: # This should handle the explanation of the errors.
                        print(exc)
