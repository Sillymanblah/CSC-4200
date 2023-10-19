# Title: Client.py
# Authors: John Grzegorczyk
# Date: 10/19/2023
# Description: Client file for Program 3 of CSC-4200 (Networks)
# Purpose: Establish a connection to a server and send a command for the program to run.
# Required files:
#       connection_handling.py  packet_handling.py 

import argparse
import socket
import struct
import logging
import connection_handling
import packet_handling

