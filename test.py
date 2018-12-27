import pickle
import sys
import socket
import os
import struct
from _thread import start_new_thread
import signal
import threading


if os.path.exists('files') == False:
    os.mkdir('files')

if os.path.exists('code') == False:
    os.mkdir('code')






def handler(signum,frame):
    pickle.dump(bNameCount,open('code/fileCount.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    print('saving structure')
    pickle.dump(root, open('code/root.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    print('Terminating all threads')
    os.system('kill -9 %d' % os.getpid())
    
print('NOTE: The server with the latest file system state should be started first or there is a risk of data loss.')


signal.signal(signal.SIGINT, handler)

if (os.path.exists('code/serverDict.pkl')):
    serverDict = pickle.load(open('code/serverDict.pkl','rb'))
else:
    print('ERROR: Server Name Configuration file not found')
    print('Starting Server for the first time')
    print('Start at least two servers when starting the system FOR THE FIRST TIME to add backup server for replication.')
    print('Server Names should be unique')

    myInp = input('Enter Server Number: ')
    #s1Inp = input('Enter Backup Server Number: ')
    #serverDict = {'myName':'sv'+str(myInp),'server1':'sv'+str(s1Inp)}
    while True:
        try:
            inpNumb = int(myInp)
            
            break
        except:
            myInp = input('Invalid Format.\nEnter Server Number: ')       

    serverDict = {'myName':'sv'+str(inpNumb)}
    pickle.dump(serverDict,open('code/serverDict.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)



ip = ''
port = 0
bNameCount = 0
if(os.path.exists('code/fileCount.pkl')):
    bNameCount = pickle.load(open('code/fileCount.pkl','rb'))
else:
    mCo = int(serverDict['myName'][2])
    bNameCount = mCo*100000
    pickle.dump(bNameCount,open('code/fileCount.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    
instruct = ['help','dir','delete','upload','download','edit']


root = None
activeServers = None


class ServerList:
    def __init__(self,ip,data):
        self.ip = ip
        self.mesg = data.split(' ')
        self.port = int(self.mesg[1])
        self.name= self.mesg[0]
        self.active = False
        self.socket = None
        print(self.mesg)

def checkUDP():
    serverList = []

    message = b'client name'
    multicast_group = ('224.1.1.6', 10006)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.settimeout(0.2)

    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    sent = sock.sendto(message, multicast_group)

    while True:
        try:
            data, server = sock.recvfrom(16)
            if data.decode().split()[0]!=serverDict['myName']:
                serverList.append(ServerList(server[0],data.decode()))
        except socket.timeout:
            break
        else:
            a=1

    sock.close()

    
    return serverList




class Node:
    def __init__(self,name,t,bName,size,sList = None):
        self.name = name
        self.type = t
        self.nbors = []
        self.bName = str(bName)
        self.parent = None
        self.size = size
        if t==False:
            self.servers = sList

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def getNbors(self):
        return self.nbors

    def getBName(self):
        return self.bName

    def getParent(self):
        return self.parent

    def getNodeByName(self,name):
        for i in self.nbors:
            if(i.getName()==name):
                return i
    
    def rmFileByName(self,name):
        for i in self.nbors:
            if(i.getName()==name and i.type==False):
                self.nbors.remove(i)
                return True,i

        return False,i

    def rmDirByName(self,name):
        for i in self.nbors:
            if(i.getName()==name and i.type==True):
                
                if(len(i.nbors)>0):
                    return False

                self.nbors.remove(i)
                return True

        return False
            

    def addNode(self,name,t,bName,size,sList=None):
        node = Node(name,t,bName,size,sList)
        node.parent = self
        self.nbors.append(node)
        return node

    def searchNode(self,node,myList,sName,xName):
        
        if node.type == False:
            
            if sName == node.servers[0] or sName == node.servers[1]:
                if os.path.exists('files/'+node.bName)==False:
                    if xName == node.servers[0] or xName == node.servers[1]:
                        myList.append(node.bName)
        for i in node.nbors:
            self.searchNode(i,myList,sName,xName)

    def searchAllNodes(self,node,myList):
        
        if node.type == False and serverDict['myName'] in node.servers:
            myList.append(node.bName)
        for i in node.nbors:
            self.searchAllNodes(i,myList)

    def searchAllNodesCommand(self,node,myList):
        
        if node.type == False:
            myList.append(node.bName)
        for i in node.nbors:
            self.searchAllNodesCommand(i,myList)

    def findMin(self):
        global serverDict
        mynewDict = {}

        for xy in serverDict.values():
            if xy != serverDict['myName']:
                mynewDict[xy]=0
        
        root.getMinimumFileServer(root,mynewDict,serverDict['myName'])
        
        
        if(len(mynewDict)!=0):
            v = list(mynewDict.values())
            k = list(mynewDict.keys())
            k[v.index(min(v))]
            
            print('FILE TO BE REPLICATED ON SERVER '+k[v.index(min(v))])
            return k[v.index(min(v))]
        return None
        #TEST



    def getMinimumFileServer(self,node,myDict,myName):

        if node.type == False:
            for i in node.servers:
                if i != myName:
                    if i in myDict:
                        myDict[i] = myDict[i]+1
                    else:
                        myDict[i] = 1

        for i in node.nbors:
            self.getMinimumFileServer(i,myDict,myName)
    
    def getNodeByAnyName(self,node,name):

        if node.name==name or str(node.bName)==name:
            print(node.name+ ' '+node.bName +' s1:'+node.servers[0]+' +s2'+node.servers[1])

        for i in node.nbors:
            self.getNodeByAnyName(i,name)







# root = Node('home',True,str(1),0)
# root.addNode('notes.txt',False,str(2),0)
# root.addNode('Work',True,str(11),10)
# root.addNode('Games',True,str(3),10)
# root.nbors[2].addNode('NFS',True,str(4),10)
# root.nbors[2].addNode('COD',True,str(5),10)
# root.nbors[1].addNode('Office',True,str(6),10)
# root.nbors[1].addNode('document.txt',False,str(7),10)
# pickle.dump(root, open('code/root.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


def searchFiles():
    global root







def doServerStuff(sConnected,initiator):
    print('awaiting instruction from server '+sConnected.name)
    
    
    try:
        while True:
            instruct = sConnected.socket.recv(1024).decode()
            x = instruct.split('\n')

            for i in x:
                p = i.split()

                if(p[0]=='create'):
                    commandAns(i,xType = True)

                elif(p[0]=='rm'):
                    commandAns(i,xType = True )

                elif (p[0]=='incoming'):
                    
                    
                    fName = p[1]
                    fSize = int(p[2])
                    fBName = p[3]
                    fPath = p[4]
                    fNew = p[5]=='new'
                    nameSERVER = p[6]
                    nameSERVER2 = p[7]
            
                    spList = [nameSERVER,nameSERVER2]
                    binaryN = int(fBName)

            
                    path = fPath.split('\\')
                    head = root
                    for i in range(2,len(path)):
                        
                        if(len(path[i])==0):
                            continue
                        
                        head = head.getNodeByName(path[i])
            
            # - decide which server to send t

                    if fNew:
                        cCount = 1

                        some = head.getNodeByName(fName)

                        sName= ''

                        while some != None:
                            sName = fName+'('+str(cCount)+')'
                            cCount = cCount +1
                            some = head.getNodeByName(sName)
                            fName = sName
                        

                        head.addNode(fName,False,binaryN,fSize,spList) 
                        
                    else:

                        try:
                            tempNode = head.getNodeByName(fName)
                            if os.path.exists('files/'+tempNode.bName):
                                os.remove('files/'+tempNode.bName)
                            head.nbors.remove(head.getNodeByName(fName))
                        except:
                            a=1

                        head.addNode(fName,False,binaryN,fSize,spList)



    except:
        print('SERVER '+sConnected.name+'DISCONNECTED')
        print('Closing socket and removing from active list')

        for i in activeServers:
            if i.name == sConnected.name:
                activeServers.remove(i)

        sConnected.socket.close()


        if initiator:

            pickle.dump(bNameCount,open('code/fileCount.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            print('saving structure')
            pickle.dump(root, open('code/root.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            startupProtocol()

        else:
            print('SERVER '+sConnected.name+'DISCONNECTED')
            print('Closing socket')

        return


        
                        #DO STARTUP STUFF AGAIN







#STARTUP PROTOCOL
def startupProtocol():
    global root, activeServers,serverDict



   

    activeServers = checkUDP()
    if len(activeServers)==0:
        #root = Node('home',True,str(1),0)
        if(os.path.exists('code/root.pkl')):
            root = pickle.load(open('code/root.pkl','rb'))
        else:
            root = Node('home',True,str(1),0)
            delList = os.listdir('files/')

            for sc in delList:
                os.remove('files/'+sc)

            pickle.dump(root, open('code/root.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
        
        

         
    else:
        
        if len(serverDict)==1:
            serverDict['server1']=activeServers[0].name
            print('Backup Server Found')
            pickle.dump(serverDict,open('code/serverDict.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


        for i in activeServers:
            
            myIP = i.ip
            myPORT = i.port
            serverSock = socket.socket()
            
            serverSock.connect((myIP,myPORT))
            print('CONNECTED TO SERVER')
            #i.active = True
            i.socket = serverSock

            serverSock.send(serverDict['myName'].encode())
            serverSock.recv(1024)
            serverSock.send('startup'.encode())

            fileN = int(serverSock.recv(1024).decode())
            print('SENDING '+str(fileN)+' files to server '+i.name)
            serverSock.send('ready'.encode())
            print('RECEIVING FILES')
            print('WAITING FOR FIRST FILE NAME')
            for nM in range (0,fileN):
                fileName = serverSock.recv(1024).decode()
                f = open('files/'+fileName,'rb')
                fileSize = str(os.stat('files/'+fileName).st_size)
                serverSock.send(fileSize.encode())

                serverSock.recv(1024)
                
                l = f.read(1024)
                    
                while len(l)>0:
                    
                    serverSock.send(l)
                    l = f.read(1024)

                f.close()

            print('FILE RECEIVING FINISHED')


            print('RECEIVING STRUCTURE')

            fileN = str(1)

            while(int(fileN)!=0):
                root = pickle.loads(serverSock.recv(60000))
                
                fileList = []
                root.searchNode(root,fileList,serverDict['myName'],i.name)

                allFiles = []
                root.searchAllNodes(root,allFiles)

                weHaveFiles = os.listdir('files/')

                for xF in weHaveFiles:
                    if xF not in allFiles:
                        os.remove('files/'+xF)



                fileN = str(len(fileList))

                serverSock.send(fileN.encode())

                serverSock.recv(1024)

                print('SENDING FILES')
                for j in fileList:
                    serverSock.send(j.encode())

                    fSize = serverSock.recv(1024).decode()
                    fSize = int(fSize)

                    serverSock.send('ready'.encode())

                    f = open('files/'+j,'wb')

                    cSize = 0
                    while fSize > cSize:
                        fileContent = serverSock.recv(1024)
                        cSize = cSize + len(fileContent)
                        f.write(fileContent)
                    
                    f.close()
                
                serverSock.send('files sending finished'.encode())

            print('ACTIVATING SERVER')
            i.active = True
            start_new_thread(doServerStuff,(i,True))
            
            

        
        
startupProtocol()














def runBroadcastThread(threadName,port):
    
    multicast_group = '224.1.1.6'
    server_address = ('', 10006)

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

        print('received {} bytes from {}'.format(
            len(data), address))
        print(data)

        print('sending acknowledgement to', address)
        mesg = serverDict['myName'] + ' '+str(port)
        sock.sendto(mesg.encode(), address)









def getListString(myList,c = '\n'):
        
        ans=''

        for i in myList:
            ans = ans + c+i

        return ans

def getListStringNodes(myList,c='\n'):
        
        ans=''

        for i in myList:
            ans = ans + c+i.getName()

        return ans






def commandAns(query,fSock = None,xType = None):
    global bNameCount, root


    if(xType!=None):
        print('AT SERVER REQUEST - RUNNING QUERY '+query)
    


    head = root

    modified = 'true'
    

    q = query.split()
    qPath = q.pop()
    sPath = qPath.split('\\')
    path = []
    path.append(head)

    for i in range(2,len(sPath)):
        
        if(len(sPath[i])==0):
            continue

        head = head.getNodeByName(sPath[i])
        path.append(head)


    #TESTING
    if(head == None):
        head=root
        path=[]
        path.append(head)
        return 'Directory you were in was deleted',path,head
        print('CAUGHT')
    #TESTING
    

    # print(head.getName())
    # print(qPath)
    # print(sPath)
    

    cmd = q[0]
    if(cmd == 'help'):
        
        return getListString(instruct),path,head

    elif(cmd == 'dir'):
        if(len(head.getNbors())>0):
            
            return getListStringNodes(head.getNbors()),path,head
        else:
            return 'Directory is currently empty',path,head

    elif(cmd == 'cd'):
        if(len(q)<2):
            return 'Incomplete - Write more',path,head
        
        if(q[1]=='..'):
            if(head==root):
                return 'You are already at the root directory',path,head
            else:
                head=head.getParent()
                path.remove(path[len(path)-1])
                return 'Directory Changed',path,head


        newDir = q[1]
        newHead = head.getNodeByName(newDir)
        if(newHead==None):
            return 'Invalid Directory Name',path,head
        
        elif(newHead.type == False):
            return 'Cant switch - the given name is a file',path,head
        else:
            head=newHead
            path.append(head)
            return 'Directory head now at '+head.getName(),path,head

    
    elif(cmd =='download'):
        if(len(q)<2):
            return 'Incomplete - Write more',path,head
        
        newDir = q[1]
        newHead = head.getNodeByName(newDir)
        if(newHead==None):
            return 'Invalid File Name',path,head
        
        elif(newHead.type):
            return 'Cant open - the given name is a directory',path,head
        else:

            if os.path.exists('files/'+newHead.getBName()):
            
                toSend = 'incoming '+newHead.getName()+' '+str(os.stat('files/'+newHead.getBName()).st_size)+' '+newHead.getBName()+' '+getListStringNodes(path,'\\')
                # fSock.send(toSend.encode())
                fSock.send(toSend.encode())

                if(fSock.recv(1024).decode()=='ready'):
                    f = open('files/'+newHead.getBName(),'rb')

                    l = f.read(1024)
                    
                    while len(l)>0:
                        
                        fSock.send(l)
                        l = f.read(1024)

                    f.close()

                    confirm = fSock.recv(1024).decode()
                    if(confirm == 'T'):

                        return 'File Opened',path,head
                    
                    else:
                        return 'File failed to open',path,head

                    


                return 'File Not Opened',path,head
            else:
                return 'chServer '+newHead.servers[0]+' '+newHead.servers[1]+'\n'+query,path,head

    elif(cmd == 'create'):
        if(len(q)<3):
            return 'Incomplete - Write more',path,head
        

        newHead = head.getNodeByName(q[2])
        if(newHead!=None):
            return 'A File or Directory already exists by this name',path,head

        if(q[1]=='file'):
            
            
            return 'create '+q[2]+' '+getListStringNodes(path,'\\'),path,head
        elif(q[1]=='dir'):
            head.addNode(q[2],True,bNameCount,0)
            bNameCount+=1


            if(xType == None):
                runUpdateDir(instruct =query)


            return '\''+q[2]+'\' Created in the Current Directory',path,head
        else:
            return 'Incorrect Command',path,head
    elif(cmd == 'upload'):
        if(len(q)<3):
            return 'Incomplete - Write more',path,head
        

        newHead = head.getNodeByName(q[2])
        if(newHead!=None):
            return 'A File or Directory already exists by this name',path,head

        if(q[1]=='file'):
            
            
            return 'upload '+q[2]+' '+getListStringNodes(path,'\\'),path,head
       
        else:
            return 'Incorrect Command',path,head

    elif(cmd == 'rm'):
        if(len(q)<3):
            return 'Incomplete - Write more',path,head
        
        if(q[1]=='file'):
            
            delCheck, tempNode = head.rmFileByName(q[2])

            if(delCheck):
                if os.path.exists('files/'+tempNode.bName):
                    os.remove('files/'+tempNode.bName)
                
                if(xType == None):
                    runUpdateDir(instruct =query)

                    
                return '\''+q[2]+'\' Deleted',path,head
            else:
                return 'File doesn\'t Exist',path,head

        elif(q[1]=='dir'):
            
            if(head.rmDirByName(q[2])):
                if(xType == None):
                    runUpdateDir(instruct=query)
                return '\''+q[2]+'\' Deleted',path,head
            else:
                return 'Directory doesn\'t Exist or may not be empty',path,head

        else:
            return 'Incorrect Command',path,head
    
    else:
        return 'Invalid Command',path,head





def runUpdateDir(fileInfo=None,instruct = None):

    
    for i in activeServers:
        if i.active:
            if instruct == None and i.name !=fileInfo[7]:
                

                toSend = 'incoming '+fileInfo[1]+' '+str(os.stat('files/'+str(fileInfo[3])).st_size)+' '+str(fileInfo[3])+' '+fileInfo[4]+' '+fileInfo[5]+' '+fileInfo[6]+' '+fileInfo[7]
                i.socket.send(toSend.encode())
                
                print('X SENT')
            elif instruct != None:
                try:
                    i.socket.send(instruct.encode())
                except:
                    print('NOT SENT')
        

            





def runFileSender(fileInfo,serverSend):
    
    sList = checkUDP()

    confirm = 'fail'

    if(len(sList)==0):
        print('No Servers Found')
        return

    for i in sList:
        
        if i.name == serverSend:
            ip = i.ip
            port = i.port
            fSock = socket.socket()      
            fSock.connect((ip, port))
            fSock.send(serverDict['myName'].encode())
            fSock.recv(1024)
#SENDING FILE
            
            toSend = 'incomingServer '+fileInfo[1]+' '+str(os.stat('files/'+str(fileInfo[3])).st_size)+' '+str(fileInfo[3])+' '+fileInfo[4]+' '+fileInfo[5]
            
                
            # fSock.send(toSend.encode())

            fSock.send(toSend.encode())

            if(fSock.recv(1024).decode()=='ready'):

                
                f = open('files/'+str(fileInfo[3]),'rb')
                


                l = f.read(1024)
                
                while len(l)>0:
                    
                    fSock.send(l)
                    l = f.read(1024)

                f.close()
                
                confirm = fSock.recv(1024).decode()
                
                
                if(confirm == 'success'):

                    print('File Successfully Saved')
                else:
                    print('Failed')

                fSock.close()



    return confirm





def serverComm(threadName,delay,fSock,addr,nameSERVER):
    global bNameCount,root, serverDict

    

    fSock.send('connected'.encode())


   

    head = root
    status= 'fail'
    
    
    #pathString= getListStringNodes(path,'\\')

    status = 'success'

    instruct = fSock.recv(1024).decode()
    p = instruct.split()
   
    # if(serverDict['myName']=='sv2'):
    #     print('hi3')

    if(p[0]=='startup'):
        if len(serverDict)==1:
            serverDict['server1']=nameSERVER
            print('Backup Server Found')
            pickle.dump(serverDict,open('code/serverDict.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)




        print('RECEIVED CONNECTION FROM SERVER')

        fileList = []
        root.searchNode(root,fileList,serverDict['myName'],nameSERVER)

        noOfFiles = str(len(fileList))
        print('Requesting '+noOfFiles + 'from server '+nameSERVER)
        fSock.send(noOfFiles.encode())

        fSock.recv(1024)

        for j in fileList:
            fSock.send(j.encode())

            fSize = fSock.recv(1024).decode()
            fSize = int(fSize)

            fSock.send('ready'.encode())

            f = open('files/'+j,'wb')

            cSize = 0
            while fSize > cSize:
                fileContent = fSock.recv(1024)
                cSize = cSize + len(fileContent)
                f.write(fileContent)
            
            f.close()
        
            
    
        fileN = str(1)

        while(int(fileN)!=0):

            mesg = pickle.dumps(root)
            print('SENT STRUCTURE')
            fSock.send(mesg)
            print('WAITING FOR NUMBER OF FILES TO RECEIVE')
            fileN = int(fSock.recv(1024).decode())
            print('SENDING '+str(fileN)+' files to server '+nameSERVER)
            fSock.send('ready'.encode())
            print('WAITING FOR FIRST FILE NAME')
            for i in range (0,fileN):
                fileName = fSock.recv(1024).decode()
                f = open('files/'+fileName,'rb')
                fileSize = str(os.stat('files/'+fileName).st_size)
                fSock.send(fileSize.encode())

                fSock.recv(1024)
                
                l = f.read(1024)
                    
                while len(l)>0:
                    
                    fSock.send(l)
                    l = f.read(1024)

                f.close()
            fSock.recv(1024)
            
        newServer = ServerList(addr,nameSERVER+' 0')
        newServer.socket = fSock
        newServer.active = True
        activeServers.append(newServer)

        doServerStuff(newServer,False)


    elif(p[0]=='rm'):

        
        print('IS THIS CODE RUNNING?')
        q = instruct.split()
        qPath = q.pop()
        sPath = qPath.split('\\')
        path = []
        path.append(head)

        for i in range(2,len(sPath)):
            
            if(len(sPath[i])==0):
                continue

            head = head.getNodeByName(sPath[i])
            path.append(head)        
        

        delCheck, tempNode = head.rmFileByName(q[2])

        if(delCheck):
            if os.path.exists('files/'+tempNode.bName):
                os.remove('files/'+tempNode.bName)
                fSock.send('successful delete'.encode())
            else:
                fSock.send('unsuccessful delete'.encode())
        else:
            fSock.send('unsuccessful delete'.encode())

        
            
    


    elif (p[0]=='incoming' or p[0]=='incomingServer'):
        
        fSock.send('ready'.encode())
        fName = p[1]
        fSize = int(p[2])
        
        fBName = p[3]
        
        fPath = p[4]
        
        fNew = p[5]=='new'

        if(p[0]=='incoming'):
            print('INCOMING FILE '+fName+' FROM CLIENT')

            xsName = root.findMin()
            if xsName == None:
                print('File Not Replicated - Connect at least one server')
                xsName = 'nv'
        
            spList = [serverDict['myName'],xsName]

            while os.path.exists('files/'+str(bNameCount)):
                bNameCount = bNameCount + 1
                
            binaryN = bNameCount
            bNameCount = bNameCount + 1
            p[3]=str(binaryN)
        else:
            print('INCOMING FILE '+fName+' FROM SERVER')
            spList = [nameSERVER,serverDict['myName']]
            binaryN = int(fBName)
            



        f = open('files/'+str(binaryN),'wb')
        
        cSize = 0
        while fSize > cSize:
            fileContent = fSock.recv(1024)
            cSize = cSize + len(fileContent)
            f.write(fileContent)
        
        f.close()

        
        path = fPath.split('\\')
        
        for i in range(2,len(path)):
            
            if(len(path[i])==0):
                continue
            
            head = head.getNodeByName(path[i])
        
        # - decide which server to send to 

        


        if fNew:
            cCount = 1

            some = head.getNodeByName(fName)

            sName= ''

            while some != None:
                sName = fName+'('+str(cCount)+')'
                cCount = cCount +1
                some = head.getNodeByName(sName)
                fName = sName
            

            head.addNode(fName,False,binaryN,fSize,spList) 
            
        else:

            try:
                tempNode = head.getNodeByName(fName)
                if os.path.exists('files/'+tempNode.bName):
                    os.remove('files/'+tempNode.bName)
                head.nbors.remove(head.getNodeByName(fName))
            except:
                a=1

            head.addNode(fName,False,binaryN,fSize,spList)
            
        if p[0]=='incoming':

            if fNew:
                xvar = 'new'
            else:
                xvar = 'old'
            
            myFileInfo=['incoming',p[1],p[2],binaryN,p[4],p[5],spList[0],spList[1]]
            
            
            status = runFileSender(myFileInfo,spList[1])
            runUpdateDir(fileInfo = myFileInfo)

            if(status == None):
                status='replication failed'
                print(status)
            if(status == None):
                status='directory replication failed'
                print(status)


 
                #DELETE FILE FROM SERVER

        fSock.send(status.encode()) #FILE SUCCESSFULLY WRITTEN
    
    fSock.close()

    return




def clientComm(threadName,delay,sock,addr):
    global root
    head = root
    path = []
    path.append(head)
    pathString= getListStringNodes(path,'\\')
    initiate = 'Connected\n\n\n'+pathString+'\nEnter a command or type \'help\': '+pathString
    sock.send(initiate.encode())

    #print('SENT '+initiate)
    
    while True:
        
        command = sock.recv(1024).decode()
        #print('RECEIVED '+command)

        if(len(command)==0):
            break

        ans,path,head = commandAns(command,sock)
        print('ANSWER FOR CLIENT '+ans)
        pathString= getListStringNodes(path,'\\')
        ans = ans+'\n\n'+pathString+'\nEnter a command or type \'help\': '+pathString
        
        
        sock.send(ans.encode())

        #print('SENT '+ans)

    print('Connection dropped with ',addr)
    sock.close()

    return

#MAIN CODE STARTING HERE ----

#STARTUP PROTOCOL













s = socket.socket()
port = 12357
portCheck = True

while portCheck:
    try:
        s.bind(('',port))
        print("socket binded to",port)
        portCheck = False
    except:
        port = port +1    
    
start_new_thread( runBroadcastThread, ("Thread Broadcast",port) )



s.listen(5)
print("socket is listening")            

i=0

def testingConsole(tName):
    while True:
        command = input()
        if(command == 'save'):
            pickle.dump(bNameCount,open('code/fileCount.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            pickle.dump(root, open('code/root.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
        elif(command == 'files'):
            tempList = []
            root.searchAllNodesCommand(root,tempList)
            print(tempList)
        elif(command == 'servers'):
            for i in activeServers:
                if i.active:
                    x='True'
                print(i.name)
        elif(command == 'exit'):
            handler(0,0)

        else:
            root.getNodeByAnyName(root,command)
            




start_new_thread(testingConsole,('a',))





while True:
    c,addr = s.accept()
    print('Got connection from', addr)
    typeC = c.recv(1024).decode()

    if(typeC==serverDict['myName']):
        print('Connected to myself')
        c.close()
    elif(typeC[0] == 'c'):
        start_new_thread( clientComm, ("Thread-"+str(i), 0, c,addr) )
    elif(typeC[0] == 's'):
        start_new_thread( serverComm, ("Thread-"+str(i), 0, c,addr,typeC) )
    else:
        print("INTRUDER at "+str(addr[0]))
        c.close()
    