import socket
import select
import sys
import getpass
import types
import os
import test
fail = ''
#control the client status for command uses
state = 'INITIAL'
account = "Guest"
prefix = account + ": "
PORT = 0
file_list = []
tmp_data = []
tmp_account = ''
# --------------------------------------------



def Handling_argv():
    global PORT
    for i in range(1, len(os.sys.argv)):
        if(os.sys.argv[i] == '-p'):
            if(i == len(os.sys.argv) - 1):
                print('-p can\'t be the last argv') 
            else:
                PORT = int(os.sys.argv[i+1])

def printprefix():
    print(prefix, end = '')
    sys.stdout.flush()

def chmod(inp):
    global state
    if inp == 'Sign in':
        state = 'Sign in'
    elif inp == 'Sign up':
        state = 'Sign up'

def clean():
    global state
    global prefix
    if state == 'INITIAL':
        readset.remove(sock)
        sock.close()
    elif state == 'Login':
        readset.remove(sys.stdin)
        state = 'INITIAL'
        prefix = "Guest" + ": "
    elif state == 'Sign in' or state == 'Sign up':
        state = 'INITIAL'
        prefix = 'Guest' + ': '
    elif state == 'Chating':
        state = 'Login'
        os.system('clear')
    
def recv_from_server(s):
    global state
    global account
    global prefix
    global writeset
    global data
    global file_list
    global tmp_data
    global tmp_account
    data = s.recv(1024)
    if not data:
        print('server closing connection')
        readset.remove(sock)
        sock.close()
        if sys.stdin in readset:
            readset.remove(sys.stdin)
    else:
        data = data.decode()
        #when client A ask to chat with client B, we flush the input line of client B
        if ((state == 'Login') and (('wants to chat' in data) or ('ask to send' in data) or (data[0] == '[' and 'kick' in data))):
            tmp = '\b'
            for i in range(0, len(prefix)):
                tmp += '\b'
            print(tmp, end = '')
        if ((state == 'Chat to') and ('is not an existing account' not in data)):
            os.system('clear')
        
        #when client sign in successfully, we change client status to login
        if (state == 'Sign in' and 'Welcome Home' in data) or (state == 'Sign up' and 'Sign up Successfully' in data):
            os.system('clear')
            print(data)

            data = data.split()
            if state == 'Sign up':
                account = tmp_account
            else:
                account = data[2]
            prefix = account + ": "
            state = 'Login'
            readset.append(sys.stdin)
            
        #when client sena a request for sending file to another client
        #wait for 'ACK' or 'NAK' to take action, so we don't print 'ACK' 'NAK' on screen
        
        elif (data != 'NAK' and data != 'ACK'):
            print(data)
        if data[0] == '[' and 'kick' in data:
            if 'repeated' in data:
                state == 'INITIAL'
                readset.remove(sys.stdin)
                prefix = 'Guest: '
                printprefix()
                return
            else:
                inp = ''
                while inp == '':
                    if state == 'Chating':
                        inp = input('')
                    elif state == 'Login':
                        printprefix()
                        inp = input('')
                send_data = inp.encode()
                s.send(sedn_data)
                return
           
        #print(f'Welcome {account}')
        inp = ''
        #for login not yet
        if state == 'INITIAL' or state == 'Sign in' or state == 'Sign up':
            if data.find("Password") > 0 or data.find("password") > 0:
                while inp == '':
                    printprefix() 
                    inp = getpass.getpass('')
                    
            else:
                while inp == '':
                    printprefix()
                    inp = input('')
                if state == 'Sign up':
                    tmp_account = inp

            send_data = inp.encode()
            s.send(send_data)
            chmod(inp)
            if inp == '(Exit)':
                clean()
                return
        elif state == 'Login':#the base status of client
            if 'Help' not in data:
                if 'SendFile' in data:#if someone want to send file to me
                    tmp_data = inp.split()
                    file_list = tmp_data[2:] #storet the file name
            
                    while inp == '':# need to response to server 'ACK' or 'NAK'
                        printprefix()
                        inp = input('')
                    inp = inp.lower()
                    if inp == 'no' or inp == 'n':
                        state = 'Login'
                        send_data = 'NAK'
                    else:
                        state = 'Receive file'
                        send_data = 'ACK'
                    s.send(send_data.encode())                           
                else:
                    printprefix()
            else:
                printprefix()
                
        elif state == 'Send request':#If I want to send file to others
            
            if 'ACK' in data:#if receive 'ACK', begin to transfer file
                state = 'Sending'
                for i in range(0, len(file_list)):
                    filesize = os.path.getsize(file_list[i])
                    file_to_send = open(file_list[i], 'rb')
                    s.send(struct,pack('i', filesize))
                    l = file_to_send.read()
                    s.sendall(l)
                    file_to_send.close() 
                    print(f'{file_list[i]} has sent.')
                sys.stdin.flush()
                printprefix()
                state = 'Login'
            elif 'is not an exist account' in data:
                state = 'Login'
                printprefix()
            else:#if receive 'NAK'
                print('The target account rejects your sending request.')
                state = 'Login'
                printprefix()
        elif state == 'Chat to':#if we chat with somebody
            if 'is not an existing account' in data:
                state = 'Login'
                printprefix()
                return
            else:
                state = 'Chating'

def After_login(s):#reading from standardinput when in state = Login
    global state
    global tmp_data
    global file_list
    inp = input('')
    if inp == '':
        printprefix()
        return
    if 'SendFile' in inp:
        state == 'Send request'
        tmp_data = inp.split()
        if len(tmp_data) < 3:
            print('Usage: SendFile [account id] [file_name1] [file_name2] ...')
            state = 'Login'
            printprefix()
            return
        else: 
            file_list = tmp_data[2:]
            flag = False
            for i in range(0, len(file_list)):
                if not os.path.isfile(file_list[i]): 
                    print('{} is not exist', format(file_list[i]))
                    flag = true
            if flag:
                state = 'Login'
                printprefix()
                return
    elif 'Chat' in inp:
        state = 'Chat to'
    send_data = inp.encode()
    sock.send(send_data)
    if inp == '(Exit)':
        clean()



def chat_status(s):#This function is used when client chat with somebody
    global state
    inp = input('')
    if inp == '':
        return
    send_data = inp.encode()
    sock.send(send_data)
    if inp == '(Exit)':
        clean()

def recvfile(s): #This function deal with client receiving data
    state = 'Sending'
    print('Waiting for transfer data')
    for i in range(0, len(file_list)):
        file_to_write = open(file_list[i], 'wb')
        filesize = s.recv(4)
        filesize = struct.unpack('i', filesize)[0]
        chunksize = 1024
        time = 1
        while filesize > 0:
            if filesize < chunksize: 
                chunksize = filesize
            data = s.recv(chunksize)
            file_to_write.write(data)
            filesize -= len(data)
            print(f'{file_list[i]} was writed {time} chunk')
            time += 1
        file_to_write.close()
        print(f'{file_list[i]} has already received.')
    sys.stdin.flush()
    printprefix()
    state = 'Login'


if __name__ == "__main__":
    os.system('clear')
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 1234
    Handling_argv()
    server_addr = (HOST, PORT)
    print('starting connection to', server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    readset = [sock]
    writeset = []
    exceptionset = []
    data = ''
    #check the connection whehter success
    if sock.connect_ex(server_addr) != 0:
        print('Failed to connect')
    else:
        print('Connection succeed!')
        #begin to interact with server
        while True:
            readable, writable, exceptionable = select.select(readset, writeset, exceptionset, 0)
            for s in readable:
                #message = input('please input command:')
                #do_service(message)
                if s is sock:
                    if state != 'Receive file':
                        recv_from_server(s)
                    else:
                        recv_for_file(s)
                elif state == 'Login':
                    After_login(s)
                elif state == 'Chating':
                    chat_status(s)
            if not readset:
                break
