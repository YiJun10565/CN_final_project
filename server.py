import socket
import select
import types
import os
import base64

def accept_wrapper(s):
    #only deal with accept client
    conn, addr = s.accept()
    print('accept connection from', addr)
    conn.setblocking(False)
    addr_list[conn.fileno()] = addr
    readset.append(conn)

def sign_up_service(data):
    account = data[1]
    password = data[2]
    path = 'passwd'
    f = open(path,'r+')
    passwd_list = f.read()
    passwd_list = passwd_list.split(":")
    passwd_list = passwd_list[:-1]
    data_back_passwd = ''
    for j in passwd_list:
        data_back_passwd += str(j) + ":"

    if account in passwd_list:
        send_data = 'NAK'
        s.send(send_data.encode())
    else:
        send_data = 'ACK'
        s.send(send_data.encode())
        password = base64.b64encode(password.encode())
        password = password.decode()
        data_back_passwd += account + ":" + password + ":"
        print('register success')
    f.seek(0)
    f.write(data_back_passwd)
    f.close()

def sign_in_service(data):
    account = data[1]
    password = data[2]
    path = 'passwd'
    f = open(path, 'r')
    passwd_list = f.read()
    passwd_list = passwd_list.split(":")
    passwd_list = passwd_list[:-1]
    if account in passwd_list:
        idx = passwd_list.index(account)
        pwd_from_file = passwd_list[idx + 1]
        pwd_from_file = base64.b64decode(pwd_from_file.encode())
        pwd_from_file = pwd_from_file.decode()
        if pwd_from_file == password:
            send_data = 'ACK'
            s.send(send_data.encode())
        else:
            send_data = 'NAK'
            s.send(send_data.encode())
    else:
        send_data = 'NAK'
        s.send(send_data.encode())
    f.close()

def do_service(recv_data):
    recv_data = recv_data.decode()
    data = recv_data.split(":")
    if data[0] == 'Sign in':
        sign_in_service(data) 
    elif data[0] == 'Sign up':
        sign_up_service(data)
    # not done yet
    #
    #
    #
    #


def service_connection(s):
    # if client send a request. If the data of the request is none, close this client's fd
    data = s.recv(1024)
    if data:
        do_service(data)
    else:
        print('closing connection to', addr_list[s.fileno()])
        addr_list[s.fileno()] = ''
        readset.remove(s)
        s.close()

#-------Initialize all variable-------
HOST = socket.gethostbyname(socket.gethostname())
PORT = 1234
addr_list = []
for i in range(15):
    addr_list.append('')
    ##create server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
addr_list[server.fileno()] = HOST
    ##create select set
readset = [server]
writeset = []
exceptionset = []
server.setblocking(False)
#-------------------------------------

print(f'the server is listening at {HOST}:{PORT}')
print('waiting for connection...')

while True:
    readable,writable,exceptionable = select.select(readset,writeset,exceptionset,0)
    for s in readable:
        if s is server: # server get a request to create a fd for client
            accept_wrapper(s) 
        else:           # server serve a client reqeust
            service_connection(s)


