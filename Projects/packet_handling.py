# packet_handling.py
# Madison Kellione

import struct

# This function creates the header for the data, it is safe to assume the type will be a 3 integer
# tuple for this program, so the header type defaults to a 3 unsigned int struct. This is a simple
# function, but might be useful?
def build_header(**kwargs):
    data = struct.pack('!I', seq_num) #pack the version
    data = struct.pack('!I', ack_num) #pack the acknowledgement number
    data += struct.pack("!c", ack) #pack the ACK
    data += struct.pack("!c", syn) #pack the SYN
    data += struct.pack("!c", fin) #pack the FIN

    return data

# This will handle the actual packet creation for sending across the network.
def create_packet(seq_num, ack_num, ack, syn, fin, payload = ''):
    # Encode message
    payload_encoded = payload.encode()
        
    # Use the python struct module to create a fixed length header
    header = build_header((seq_num, ack_num, ack, syn, fin))
    
    #Combine header and message
    packet = header + payload_encoded
        
    return packet
