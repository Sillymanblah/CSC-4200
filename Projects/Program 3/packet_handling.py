import struct

# A function to encode the data before we send it over the network, we can assume it will
# be a character string at most 8 characters.
def encode(data, data_encoder = struct.Struct('!8s')):
    return data_encoder.pack(data) # This can have errors, but we can catch those in our server/client

# A function for dencoding the data after it has been received, we can again assume it
# will be a character bytes set of at most 8 bytes, starting after the header (which should be 
# 12 bytes long in this case).
def decode(packet: bytes, data_decoder = struct.Struct('!8s')):
    return data_decoder.unpack(packet)

# This function creates the header for the data, it is safe to assume the type will be a 3 integer
# tuple for this program, so the header type defaults to a 3 unsigned int struct. This is a simple
# function, but might be useful?
def build_header(*header_data, header_encoder: struct = struct.Struct('!3I')):
    return header_encoder.pack(header_data)

# To deconstruct the header, we send in bytes and can send in a header type (though in this program
# it is safe to assume the packet header is 12 bytes long and is made up of 3 unsigned integers).
# Which is why the default value for the header_type is a 3 unsigned int struct. This might not have 
# needed to be a function...
def break_header(header: bytes, header_decoder: struct = struct.Struct('!3I')):
    return header_decoder.unpack(header) # Unpack and send to user.
