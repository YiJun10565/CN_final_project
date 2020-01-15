import socket
import select
import types

def accept_wrapper(s):
    #only deal with accept client
    conn, addr = s.accept()
    print('accept connection from', addr)
    conn.setblocking(False)
    addr_list[conn.fileno()] = addr
    readset.append(conn)


def do_service(recv_data):
    if recv_data == 'Sign in':
        print('asd') 
    elif recv_data == 'Sign up':
        print('ad')
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


