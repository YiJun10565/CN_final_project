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
file_list = []
tmp_data = []
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
        prefix = "Guest" + " : "
    elif state == 'Sign in' or state == 'Sign up':
        state = 'INITIAL'
        prefix = 'Guest' + ' : '
    elif state == 'Chat':
        state = 'Login'

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
        if state == 'Login' and 'Communicate' in data:
            tmp = '\b'
            for i in range(0, len(prefix)):
                tmp += '\b'
            print(tmp, end = '')
        print(data)
        #print(data + '\n' + prefix, end='')
        if state == 'Sign in' and 'Login successfully' in data:
            state = 'Login'
            data = data.split()
            account = data[2]
            prefix = account + " : "
            readset.append(sys.stdin)
            os.system('clear')
            print(f'Welcome {account}')
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
                return
        elif state == 'Login':
            if 'Communicate' in data: #if someone want to chat with me
                while inp == '':
                    printprefix()
                    inp = input('')
                send_data = inp.encode()
                inp = inp.lower()
                if inp == 'no' or inp == 'n':
                    state = 'Login'
                else:
                    state = 'Chating'
                    os.system('clear')
                s.send(send_data)
            elif 'Send' in data: #if someone want to send file to me
                while inp == '':
                    printprefix()
                    inp = input('')
                send_data = inp.encode()
                inp = inp.lower()
                if inp == 'no' or inp == 'n':
                    state = 'Login'
                else:
                    state = 'Receive file'
                                        

                
            else:
                printprefix()
        elif state == 'Send request':
            if 'ACK' in data:
                state = 'Sending'
                for i in range(0, len(file_list)):
                    file_to_send = open(file_list[i], 'rb')
                    l = file_to_send.read()
                    s.sendall(l)
                    file_to_send.close()
                    print(f'{file_list[i]} has sent.')
                printprefix()
                state = 'Login'
            else:
                state = 'Login'
        elif state == 'Chat to':
            print(123)            

def After_login(s):
    global state
    global tmp_data
    global file_list
    inp = input('')
    if inp == '':
        printprefix()
        return
    if 'Send' in inp:
        state == 'Send request'
        tmp_data = inp.split()
        if len(tmp_data) < 3:
            print('Usage : Send [account id] [file_name1] [file_name2] ...')
            state = 'Login'
            printprefix()
            return
        else :
            file_list = tmp_data[2:]
            flag = False
            for i in range(0, len(file_list)):
                if not os.path.isfile(file_list) :
                    print('{} is not exist', format(file_list[i]))
                    flag = true
            if flag:
                state = 'Login'
                printprefix()
                return
    elif 'Communicate' in inp:
        state = 'Chat to'
    send_data = inp.encode()
    sock.send(send_data)
    if inp == '(Exit)':
        clean()



def chat_status(s):
    global state
    inp = input('')
    if inp == '':
        return
    send_data = inp.encode()
    sock.send(send_data)
    clean()
    if inp == '(Exit)':
        clean()



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
        print('Success connect!')
        #begin to interact with server
        while True:
            readable, writable, exceptionable = select.select(readset, writeset, exceptionset, 0)
            for s in readable:
                #message = input('please input command:')
                #do_service(message)
                if s is sock:
                    serve(s)
                elif state == 'Login' or state == 'Send request':
                    After_login(s)
                elif state == 'Chating':
                    chat_status(s)
            if not readset:
                break
