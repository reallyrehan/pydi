import socket
import struct
import sys

multicast_group = '224.1.1.3'
server_address = ('', 10000)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_ADD_MEMBERSHIP,
    mreq)

# Receive/respond loop
while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(1024)

    name = address[0]
    print(address[0])

    if name== '192.168.43.218':
        print('Emaan')
    elif name == '192.168.43.167':
        print('Sunila')
    elif name == '192.168.43.38' or name == '127.0.0.1':
        print('Khud')
    elif name == '192.168.43.152':
        print('Mahnur')        

    print('received {} bytes from {}'.format(
        len(data), address))
    print(data)

    print('sending acknowledgement to', address)
    sock.sendto(b'ack', address)