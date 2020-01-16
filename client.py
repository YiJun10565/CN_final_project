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

def serve(s):
    global state
    global account
    global prefix

    data = s.recv(1024)
    data = data.decode()
    print(data)
    if state == 'INITIAL' and 'Login successfully' in data:
        state = 'Login'
        data = data.split()
        account = data[2]
        prefix = account + " : "
    sys.stdin.flush()
    if state == 'INITIAL':
        if data.find("Password") > 0 or data.find("password") > 0:
            inp = getpass.getpass(prefix)
        else:
            inp = input(prefix)
    else:
        inp = input(prefix)
    send_data = inp.encode()
    s.send(send_data)

HOST = socket.gethostbyname(socket.gethostname())
PORT = 1234
Handling_argv()
server_addr = (HOST, PORT)
print('starting connection to', server_addr)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
readset = [sock]
writeset = []
exceptionset = []
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
            serve(s)
