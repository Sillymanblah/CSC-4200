import struct

# This function creates the header for the data, it is safe to assume the type will be a 3 integer
# tuple for this program, so the header type defaults to a 3 unsigned int struct. This is a simple
# function, but might be useful?
def build_header(header_data: tuple, header_encoder: struct = struct.Struct('!3I')):
    return header_encoder.pack(*header_data)

# This will handle the actual packet creation for sending across the network.
def create_packet(version, message_type, message_length, message):
    # Encode message
    message_encoded = message.encode()
        
    # Use the python struct module to create a fixed length header
    header = build_header((version, message_type, message_length))
    
    #Combine header and message
    packet = header + message_encoded
        
    return packet