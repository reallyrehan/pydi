
import pickle
import sys
import socket
import os
import struct
from _thread import start_new_thread
import signal
import time

ip = '127.0.0.1'
port = 2000
newS = socket.socket()      
newS.connect((ip, port))


def myThread(char):
    global newS

    s=''
    for i in range(1,100):
        s= s + char

    s=s+'\n'

    

    count = 0

    while count<100:
        newS.send(s.encode())



start_new_thread(myThread,('a',))
start_new_thread(myThread,('b',))
start_new_thread(myThread,('c',))
start_new_thread(myThread,('d',))
myThread,('e')


time.sleep(15)