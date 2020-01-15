import socket
import select
import types
first = 0
def accept_wrapper(s):
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

def service_connection(s):
    # if there are some contexts coming
    data = s.recv(1024)
    if data:
        do_service(data)
    if not data:
        print('closing connection to', addr_list[s.fileno()])
        addr_list[s.fileno()] = ''
        readset.remove(s)
        s.close()


HOST = socket.gethostbyname(socket.gethostname())
PORT = 1234
addr_list = []
for i in range(15):
    addr_list.append('')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
addr_list[server.fileno()] = HOST
readset = [server]
writeset = []
exceptionset = []
server.setblocking(False)
#sel.register(server, selectors.EVENT_READ, data=None)
print(f'the server is listening at {HOST}:{PORT}')
print('waiting for connection...')
"""conn, addr = server.accept()

print(f'connect success addr={addr}')
print('waiting for message')
while True:
    msg = conn.recv(1024)
    print('the client send:', msg.decode())
    response = input('enter your response: ')
    conn.send(response.encode())
    print('waiting for answer')
"""

while True:
    readable,writable,exceptionable = select.select(readset,writeset,exceptionset,0)
    for s in readable:
        if s is server:
            accept_wrapper(s)
        else:    
            service_connection(s)


