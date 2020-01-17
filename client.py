import socket
import select
import sys
import getpass
import types
import os
fail = ''
#control the client status for command uses
state = 'INITIAL'
account = "Guest"
prefix = account + " : "
PORT = 0
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
        prefix = "Guest" + " : "
    elif state == 'Sign in' or state == 'Sign up':
        state = 'INITIAL'
        prefix = 'Guest' + ' : '


def serve(s):
    global state
    global account
    global prefix
    global writeset
    global data
    data = s.recv(1024)
    if not data:
        print('server closing connection')
        readset.remove(sock)
        sock.close()
        if sys.stdin in readset:
            readset.remove(sys.stdin)
    else:
        data = data.decode()
        print(data)
        #print(data + '\n' + prefix, end='')
        if state == 'Sign in' and 'Login successfully' in data:
            state = 'Login'
            data = data.split()
            account = data[2]
            prefix = account + " : "
            readset.append(sys.stdin)
            state == 'Login':
            printprefix()
            return
        inp = ''
        if state == 'INITIAL' or state == 'Sign in' or state == 'Sign up':
            if data.find("Password") > 0 or data.find("password") > 0:
                while inp == '':
                    printprefix()
                    inp = getpass.getpass('')
                    
            else:
                while inp == '':
                    printprefix()
                    inp = input('')
        send_data = inp.encode()
        s.send(send_data)
        chmod(inp)
        if inp == '(Exit)':
            clean()

def communicate(s):
    global state
    if state == 'Login':
        inp = input('')
        if inp == '':
            print(prefix, end = '')
            sys.stdout.flush()
            return
        send_data = inp.encode()
        sock.send(send_data)
        if inp == '(Exit)':
            clean()


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
    print('Success connect!')
    #begin to interact with server
    while True:
        readable, writable, exceptionable = select.select(readset, writeset, exceptionset, 0)
        for s in readable:
            #message = input('please input command:')
            #do_service(message)
            if s is sock:
                serve(s)
            elif state == 'Login':
                communicate(s)
        if not readset:
            break
