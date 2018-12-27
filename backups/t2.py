import pickle
import sys
import socket
import os
import struct
from _thread import start_new_thread
import signal

s = socket.socket()

s.bind(('',2000))

s.listen(5)

c,addr = s.accept()

command = input('connected')

ans = c.recv(60000).decode()

print(ans)