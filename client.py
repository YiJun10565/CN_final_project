import socket
import select
import sys
import getpass
import types
import os
fail = ''
#control the client status for command uses
state = 'INITIAL'
account = ''
PORT = 0
def Handling_argv():
    for i in range(1, len(os.sys.argv)):
        if(os.sys.argv[i] == '-p'):
            if(i == len(os.sys.argv) - 1):
                print('-p can\'t be the last argv') 
            else:
                PORT = int(os.sys.argv[i+1])
def do_service(message):
    global state #get global variable state
    
    #list all the command can be used currently for client
    if message == 'command':
        print('-------Command list-------')
        if state == 'INITIAL':
            print('Sign up')
            print('Sign in')
        elif state == 'Sign in':
            print('asd')
        print('--------------------------')    
    #send a message to server for sign up service
    elif state == 'INITIAL' and message == 'Sign up':
        account = input('please input wanted account id : ')
        password = getpass.getpass('please input wanted password : ')
        data = 'Sign up' + ':' + account + ':' + password
        sock.send(data.encode())
        check = sock.recv(1024)
        check = check.decode()
        if check == 'ACK':
            print('Register successfully!')
        else:
            print('The account is exist!')
    #send a message to server for sign in service
    elif state == 'INITIAL' and message == 'Sign in':
        account = input('please input your account id : ')
        password = getpass.getpass('please input your password : ')
        data = 'Sign in' + ':' + account + ':' + password
        sock.send(data.encode())
        check = sock.recv(1024)
        check = check.decode()
        if check == 'ACK':
            print('Sign in successfully!')
            state = 'Sign in'
        else:
            print('Account id/password wrong!!')
def serve(s):
    global state
    global account
    data = s.recv(1024)
    data = data.decode()
    print(data)
    if 'Login successfully' in data:
        state = 'Login'
        data = data.split(" ")
        account = data[2] + " : "
    sys.stdin.flush()
    if state == 'INITIAL':
        if 'Password' in data:
            inp = getpass.getpass('')
        else:
            inp = input('')
    else:
        inp = input(account)
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
    fail = True 
if fail == True:
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
