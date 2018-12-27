import sys
from socket import socket, AF_INET, SOCK_DGRAM

SERVER_IP   = '127.0.0.1'
PORT_NUMBER = 5000

print ("Test client sending packets to IP {0}, via port {1}\n".format(SERVER_IP, PORT_NUMBER))

mySocket = socket( AF_INET, SOCK_DGRAM )

while True:
        message = raw_input('What is your message?')
        mySocket.sendto(message,(SERVER_IP,PORT_NUMBER))

        (data,addr) = mySocket.recvfrom(SIZE)
        print data
sys.exit()





