import socket
import select
import types
import os
import base64
import csv

# string
# -------------

interface_postfix = "\n Enter 'Sign in' to sign in, 'Sign up' to sign up"
exit_postfix = "\nYou can enter '(Exit)' to exit whenever you want."

# -------------

def accept_wrapper(s):
    #only deal with accept client
    conn, addr = s.accept()
    print('accept connection from', addr)
    conn.setblocking(False)
    addr_list[conn.fileno()] = addr
    State_list[conn.fileno()] = "Idle"
    readset.append(conn)
    send_data = "Connected to the server"
    send_data += interface_postfix
    conn.send( send_data.encode())


def sign_up_service(fileno, data):
    #get the account and password from client sending
    if(sub_State_list[fileno] == "Enter Account"):
        invalid_name = 0
        for x in data:
            if not x.isdigit() and not x.isalpha():
                invalid_name = 1
                break
        if invalid_name:
            send_data = "Invalid account, please enter a valid one (only contains 0~9, a~z, A~Z)"
        else:
            if data in Account_Dict:
                send_data = "Account has already existed:"
            else:
                tmp_acc[fileno] = data
                sub_State_list[fileno] = "Enter Password"
                send_data = "Please enter the password you want:"

    elif(sub_State_list[fileno] == "Enter Password"):
        tmp_pwd[fileno] = data
        send_data = "Please enter the password again:"
        sub_State_list[fileno] = "Enter Password again"
    
    elif(sub_State_list[fileno] == "Enter Password again"):
        if data == tmp_pwd[fileno]:
            encrypted_pwd = base64.b64encode(data.encode()).decode()
            Account_Dict.update( {tmp_acc[fileno]:encrypted_pwd})
            send_data = "Sign up Successfully" + tmp_acc[fileno]
            with open('Account.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for key in Account_Dict:
                    writer.writerow( [key, Account_Dict[key]] )
            State_list[fileno] = "Idle"
            sub_State_list[fileno] = ""
        else:
            send_data = "Wrong\nPlease enter the Account you want:"
            sub_State_list[fileno] = "Enter Account"
            tmp_pwd[fileno] = ""
            tmp_acc[fileno] = ""
    else :
        print("sign up error")
    s.send(send_data.encode())

def sign_in_service(fileno, data):

    #get the account and password from client sending
    if data == '(Exit)':
        send_data = "Back to login interface"
        send_data += interface_postfix
        State_list[fileno] = "Idle"
        sub_State_list[fileno] = "Idle"

    #print("Sign in : ",sub_State_list[fileno] , "data = ", data)
    if sub_State_list[fileno] == "Enter Account":
        if data in Account_Dict:
            tmp_acc[fileno] = data
            sub_State_list[fileno] = "Enter Password"
            send_data = "Enter Password:"
        else:
            send_data = "Account not exists, please enter a valid account"

    elif sub_State_list[fileno] == "Enter Password":
        if base64.b64encode(data.encode()).decode() == Account_Dict[tmp_acc[fileno]] :
            send_data = "Login successfully " + tmp_acc[fileno]
            #logging_list.append( tmp_acc[fileno] )
            Login_list[fileno] = True
            State_list[fileno] = "Idle"
            sub_State_list[fileno] = ""
        else :
            send_data = "Wrong password, please enter again."
    else :
        print("sign in error")
    send_data += exit_postfix
    s.send(send_data.encode())
    
def Login_service(s, data):
    fileno = s.fileno()
    print(data, State_list[fileno])
    if(State_list[fileno] == "Idle"):
        print("Idle", data)
        if(data == "Sign in"):
            send_data = "Please enter your account:"
            State_list[fileno] = "Sign in"
            sub_State_list[fileno] = "Enter Account"
        elif(data == "Sign up"):
            send_data = "Please enter the account you want:"
            State_list[fileno] = "Sign up"
            sub_State_list[fileno] = "Enter Account"
        elif(data == "(Exit)"):
            close_connection(s)

        else :
            send_data = "Login unknown command, please try again\n"
            send_data += "Enter 'Sign in' to sign in, 'Sign up' to sign up."
        s.send(send_data.encode())

    elif(State_list[fileno] == "Sign in"):
        sign_in_service(fileno, data)        
    elif(State_list[fileno] == "Sign up"):
        sign_up_service(fileno, data)
    else:
        print("Unknown state when loging")

def Check(fileno, account):
    send_data = ""
    if account not in Account_Dict:
        send_data = "Not existing account"
    #elif 

def After_Login_service(s, data):
    fileno = s.fileno()
    if(State_list[fileno] == "Idle"):
        if(data == "Check"):
            send_data = "Please enter the account you want to check if it is online"
            State_list[fileno] = "Check"

        elif(data == "Communicate"):
            send_data = "Please enter the account you want to communicate with"
            State_list[fileno] = "Communicate"

        elif(data == "Send file"):
            send_data = "Please enter the account you want to send file to"
            State_list[fileno] = "Sendfile"
        elif(data == "(Exit)"):
            send_data = "Back to login interface"
            Login_list[fileno] = false
            State_list[fileno] = "Idle"
            sub_State_list[fileno] = "Idle"

    elif(State_list[fileno] == "Check"):
        Check(fileno, data)
    #elif(State_list[fileno] == "Commnicate"):
    #    Communicate(fileno, data)
    #elif(State_list[fileno] == "Send file"):
    #    Send_file(fileno, data)

def do_service(s, recv_data):
    
    if(Login_list[s.fileno()] == False):
        print("Login_service")
        Login_service(s, recv_data)
    else:
        print("After Login service")
        After_Login_service(s, recv_data)


def close_connection(s):
    print('closing connection to', addr_list[s.fileno()])
    addr_list[s.fileno()] = ''
    State_list[s.fileno()] = "Idle"     
    sub_State_list[s.fileno()] = "Idle"
    readset.remove(s)
    s.close()



def service_connection(s):
    # if client send a request. If the data of the request is none, close this client's fd
    data = s.recv(1024)
    if data:
        do_service(s, data.decode())
    else:
        close_connection(s)

def Change_Port(PORT):
    for i in range(1, len(os.sys.argv)):
        if(os.sys.argv[i] == "-p"):
            if i == len(os.sys.argv) -1:
                print("-p can't be the last argv")
            else :
                print("Change port to ", os.sys.argv[i+1])
                PORT = int(os.sys.argv[i+1])
    return PORT
        


if __name__ == "__main__":
    #-------Initialize all variable-------
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 1234
    
    PORT = Change_Port(PORT)

    # a fileno -> a state and a substate
    addr_list = []

    # boolean for whether it is login
    Login_list = []
    # Potential State_list = [ "Idle", "Sign in", "Sign up", "Check", "Communicate"]
    State_list = []
    # Potential sub_State_list = [ "", "Disconnected"(?), "Enter Account", "Enter Password", "Enter Password again", "Receive Offline message", "Start talking"]
    sub_State_list = []
    
    # these 2 lists are for the server to store msg
    # due to there will be 2 different pkg for the 2 msg
    tmp_acc = []
    tmp_pwd = []
    
    #logging_list = []

    for i in range(1500):
        addr_list.append('')
        tmp_acc.append('')
        tmp_pwd.append('')
        Login_list.append(False)
        State_list.append('Idle')
        sub_State_list.append('Idle')
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

    
    Account_Dict = {}
    # read Account file in csv 
    with open("./Account.csv", newline='') as csvfile:
        # rows is a 2-dim list, [ [acnt0, pswd0],[acnt1, pswd1], ... ]
        rows = csv.reader(csvfile)     
        for row in rows:
            # Save accounts info into a local dictionary
            Account_Dict.update({row[0]: row[1]})
            # print(row)
    
    #-------------------------------------


    print(f'the server is listening at {HOST}:{PORT}')
    print('waiting for connection...')

    for acc in Account_Dict:
        print(acc, Account_Dict[acc])

    while True:
        readable,writable,exceptionable = select.select(readset,writeset,exceptionset,0)
        for s in readable:
            if s is server: # server get a request to create a fd for client
                accept_wrapper(s) 
            else:           # server serve a client reqeust
                service_connection(s)

    
