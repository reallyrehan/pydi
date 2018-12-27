# Import socket module
import socket               
import webbrowser
from tkinter import *
from tkinter.filedialog   import asksaveasfilename
from tkinter.simpledialog import askstring
from tkinter.messagebox import askokcancel
from _thread import start_new_thread
import sys
import struct
import os
import signal




def handler(signum,frame):
    print('Terminating all threads')
    os.system('kill -9 %d' % os.getpid())
    


signal.signal(signal.SIGINT, handler)




ip = ''
port = 0

class ServerList:
    def __init__(self,ip,data):
        self.ip = ip
        self.mesg = data.split(' ')
        self.port = int(self.mesg[1])
        self.name= self.mesg[0]
        

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
            serverList.append(ServerList(server[0],data.decode()))
        except socket.timeout:
            break
        else:
            a=1

    sock.close()

    
    return serverList



def runFileSenderThread(threadName,fileInfo):
    global ip,port

    if os.path.exists(fileInfo[1]) == False:
        print('The file does not exist in your working directory')
        return 


    fSock = socket.socket()  
    try:    
        fSock.connect((ip, port))
    except:
        serverList = checkUDP()
        newIP = serverList[0].ip
        newPORT = serverList[0].port
        fSock.connect((newIP,newPORT)) 
    
    

    fSock.send('serverclient'.encode())
    fSock.recv(1024)
    #SENDING FILE
    try:
        toSend = 'incoming '+fileInfo[1]+' '+str(os.stat(fileInfo[1]).st_size)+' '+fileInfo[3]+' '+fileInfo[4]+' '+fileInfo[5]
    except:
        print('The given filename does not exist')
    # fSock.send(toSend.encode())

    fSock.send(toSend.encode())

    if(fSock.recv(1024).decode()=='ready'):

        
        f = open(fileInfo[1],'rb')
        


        l = f.read(1024)
        
        while len(l)>0:
            
            fSock.send(l)
            l = f.read(1024)

        f.close()
        
        confirm = fSock.recv(1024).decode()
        
        
        print('Uploaded Successfully')

        

    return






#EDITOR CODE------------------------------------------------------------------------------------------------------------------


#http://code.activestate.com/recipes/578569-text-editor-in-python-33/
################################################################################

class ScrolledText(Frame):

    def __init__(self, parent=None, text='', file=None):
        super().__init__(parent)
        self.pack(expand=YES, fill=BOTH)
        self.makewidgets()
        self.settext(text, file)

    def makewidgets(self):
        sbar = Scrollbar(self)
        self.text = Text(self, relief=SUNKEN, wrap=WORD)
        sbar['command'] = self.text.yview
        self.text['yscrollcommand'] = sbar.set
        sbar.pack(side=RIGHT, fill=Y)
        self.text.pack(side=LEFT, expand=YES, fill=BOTH)

    def settext(self, text='', file=None):
        if file:
            with open(file, 'r') as stream:
                text = stream.read()
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()

    def gettext(self):
        return self.text.get('1.0', END + '-1c')

################################################################################

class Quitter(Frame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pack()
        widget = Button(self, text='Quit', command=self.quit)
        widget.pack(expand=YES, fill=BOTH, side=LEFT)

    def quit(self):
        if askokcancel('Verify exit', 'Really quit?'):
            self._root().destroy()

################################################################################
class SimpleEditor(ScrolledText):
    

    def __init__(self, parent=None,text='',fileInfo=None,file=None): 
        frm = Frame(parent)
        frm.pack(fill=X)
        Button(frm, text='Save',  command=self.onSave).pack(side=LEFT)
        Button(frm, text='Cut',   command=self.onCut).pack(side=LEFT)
        Button(frm, text='Paste', command=self.onPaste).pack(side=LEFT)
        Button(frm, text='Find',  command=self.onFind).pack(side=LEFT)
        Quitter(frm).pack(side=LEFT)
        super().__init__(parent,text=text, file=file)
        self.text['font'] = 'courier', 9, 'normal'
        self.target = ''
        self.fileInfo = fileInfo

    def onSave(self):

       
        master = Tk()
        e = Entry(master)
        
        e.pack()
        
        e.insert(0,self.fileInfo[1])
        e.focus_set()
        def callback():
            
            if(self.fileInfo[5]=='old' and e.get()!=self.fileInfo[1]):
                self.fileInfo[5]='new'
                

            
            
            self.fileInfo[1]=e.get()
            myText = self.gettext()

            f = open(self.fileInfo[1],'w')
            f.write(myText)
            f.close()

            start_new_thread( runFileSenderThread, ("File Sender Thread",self.fileInfo))
            master.destroy()

        b = Button(master, text = "SAVE", width = 10, command = callback)
        b.pack()
        mainloop()
        
        

        

    def onCut(self):
        self.clipboard_clear()
        self.clipboard_append(self.text.get(SEL_FIRST, SEL_LAST))
        self.text.delete(SEL_FIRST, SEL_LAST)

    def onPaste(self):
        try:
            self.text.insert(INSERT, self.selection_get(selection='CLIPBOARD'))
        except TclError:
            pass

    def onFind(self):
        self.target = askstring('SimpleEditor', 'Search String?',
                                initialvalue=self.target)
        if self.target:
            where = self.text.search(self.target, INSERT, END, nocase=True)
            if where:
##                print(where)
##                self.text.tag_remove(SEL, '1.0', END)
                pastit = '{}+{}c'.format(where, len(self.target))
                self.text.tag_add(SEL, where, pastit)
                self.text.mark_set(INSERT, pastit)
                self.text.see(INSERT)
                self.text.focus()

################################################################################




def runEditorThread(threadName,delay,fileInfo):
    
    
    try:
        if(fileInfo[5]=='new'):
            SimpleEditor(text='',fileInfo=fileInfo,file=sys.argv[1] if len(sys.argv) > 1 else None).mainloop()
            print('File Editor Closed')

        else:
            f = open(fileInfo[1],'r')
            l = f.read()
            SimpleEditor(text=l,fileInfo=fileInfo,file=sys.argv[1] if len(sys.argv) > 1 else None).mainloop()
            print('File Editor Closed')
    except:
        print('Not a String file - Editor can\'t open this file\nOpening it in the default application')
        webbrowser.open_new_tab(fileInfo[1])

    return







#EDITOR CODE ------------------------------------------------------------------------------------------------------------------

















# sample instruction
# incoming fileName fileSize fileBName path



def switchServer(instruct):
    #chServer name\ninstruction user sent

    sList = checkUDP()
    if(len(sList)!=0):
        ip = sList[0].ip
        port = sList[0].port
        newS = socket.socket()      
        newS.connect((ip, port))
        newS.send('client'.encode())


        helloI = newS.recv(1024)


        newS.send(instruct.encode())


        response = newS.recv(1024).decode()


        printR,pathS,newS = responseProcessing(response,newS)
        return printR,pathS,newS






def responseProcessing(response,fSock):
    
    p = response.split()
    path = p[len(p)-1]
    
    if (p[0]=='incoming'):
        p.append('old')
        fSock.send('ready'.encode())
        
        fName = p[1]
        fSize = int(p[2])
        fBName = p[3]
        fPath = p[4]
        
        f = open(fName,'wb')
        #print('f '+str(fSize))
        
        cSize = 0
        while fSize > cSize:
            fileContent = fSock.recv(1024)
            cSize = cSize + len(fileContent)
            f.write(fileContent)
        
        f.close()

        fSock.send('T'.encode())
        response = fSock.recv(1024).decode()

        cmd = input('File Downloaded - do you want to open the file?\nEnter \'yes\' to Open in Text Editor: ')
        if(cmd=='yes'):
            response = 'Opening...'
            start_new_thread( runEditorThread, ("Thread-"+str(2), 0,p) )
            
        
    elif(p[0]=='create'):
        newInfo = ['incoming',p[1],0,'0',p[2],'new'] 
        response = 'Opening...'
        start_new_thread( runEditorThread, ("Thread-"+str(2), 0,newInfo) )
        

    elif(p[0]=='upload'):
        
        newInfo = ['incoming',p[1],0,'0',p[2],'new'] 
        response = 'Uploading...'

        start_new_thread( runFileSenderThread, ("File Sender Thread",newInfo))
    elif(p[0]=='chServer'):
        #chServer name\ninstruction user sent
        newI = response.split('\n')
        serverInfo = newI[0].split(' ')

        sList = checkUDP()

        if(len(sList)!=0):
            
            for i in sList:
                if i.name == serverInfo[1] or i.name == serverInfo[2]:
                    ip = i.ip
                    port = i.port
                    newS = socket.socket()      
                    newS.connect((ip, port))
                    newS.send('client'.encode())
                    newS.send(newI[1])
                    response = newS.recv(1024).decode()
                    printR,pathS,newS = responseProcessing(response,newS)
                    return printR,pathS,newS
        
        response = 'File not available right now'



        

    return response,path,fSock




#MAIN CODE STARTING
# incoming fileName fileSize fileBName path

# fileInfo = ['incoming','abc.png','365017','abc','home/Work']
# runFileSenderThread('thread1',fileInfo)



serverList = checkUDP()

if(len(serverList)==0):
    print('System Down')
    exit()

ip = serverList[0].ip
port = serverList[0].port
s = socket.socket()      
s.connect((ip, port))

s.send('client'.encode())


sendCommand = ''



while True:

    try:
        response = s.recv(1024).decode()
        printR,pathS,s = responseProcessing(response,s)

        print(printR)

        command = input()
        while len(command)==0 or len(command)>600:
            print('Invalid Command - Enter Again')
            command = input()

        if(command == 'exit'):
            print('Terminating Connection with Server')
            s.close()
            break

        sendCommand = command+' '+pathS

    
        s.send(sendCommand.encode())
    except:
        printR,pathS,s = switchServer(sendCommand)
        
        print(printR)

        command = input()
        while len(command)==0:
            print('Invalid Command - Enter Again')
            command = input()

        if(command == 'exit'):
            print('Terminating Connection with Server')
            s.close()
            break

        sendCommand = command+' '+pathS

    
        s.send(sendCommand.encode())

        

# close the connection
s.close()