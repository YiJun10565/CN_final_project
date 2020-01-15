import socket
import selectors
import sys
import getpass
import types

fail = False
state = 'INITIAL'

def do_service(message):
    global state
    if message == 'command':
        print('-------Command list-------')
        if state == 'INITIAL':
            print('Sign up')
            print('Sign in')
        elif state == 'Sign in':
            print('asd')
        print('--------------------------')    
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
        
"""
def service_connection():
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('received', repr(recv_data), 'from connection', data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print('closing connection', data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
"""

HOST = socket.gethostbyname(socket.gethostname())
PORT = 1234
#print(f'Connection to {HOST}:{PORT}')

server_addr = (HOST, PORT)
print('starting connection to', server_addr)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if sock.connect_ex(server_addr) != 0:
    fail = True 
data = types.SimpleNamespace(outb = b'')

if fail == True:
    print('Failed to connect')
else:
    print('Success connect!')
    while True:
        message = input('please input command:')
        do_service(message)

"""
try:
    host, port = input('please enter host address like host:port: ').split(':')
except ValueError:
    print('the address is wrong')
    sys.exit(-1)

if len(host) == 0 or len(port) == 0:
    print('the address is wrong')
    sys.exit(-1)
else:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host), (int)port)
    client.sendall(b'Hello, world')
    data = s.recv(1024)
    print('Receiver', repr(data))
"""
