import socket
import selectors
import sys
import getpass
import types

#control the client status for command uses
state = 'INITIAL'

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
        

HOST = socket.gethostbyname(socket.gethostname())
PORT = 1234

server_addr = (HOST, PORT)
print('starting connection to', server_addr)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#check the connection whehter success
if sock.connect_ex(server_addr) != 0:
    fail = True 
if fail == True:
    print('Failed to connect')
else:
    print('Success connect!')
    #begin to interact with server
    while True:
        message = input('please input command:')
        do_service(message)
