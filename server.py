import socket
import select
import types
import os
import base64
import csv

# string
# -------------

interface_postfix = "\nEnter 'Sign in' to sign in, 'Sign up' to sign up"
exit_postfix = "\nYou can enter '(Exit)' to exit whenever you want."
Idle_state = "Idle"
Sign_in_state = "Sign in"
Sign_up_state = "Sign up"
Enter_acc_state = "Enter Account"
Enter_pwd_state = "Enter Password"
Enter_pwd_again_state = "Enter Password again"

Chat_state = "Chat"
Check_state = "Check"

# -------------

def accept_wrapper(s):
    #only deal with accept client
    conn, addr = s.accept()
    print('accept connection from', addr)
    conn.setblocking(False)
    Socket_list[conn.fileno()] = conn
    addr_list[conn.fileno()] = addr
    State_list[conn.fileno()] = Idle_state
    sub_State_list[conn.fileno()] = Idle_state
    readset.append(conn)
    send_data = "Connected to the server"
    send_data += interface_postfix
    conn.send( send_data.encode())


def sign_up_service(s, data):
    fileno = s.fileno()
    #get the account and password from client sending
    if(sub_State_list[fileno] == Enter_acc_state):
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
                Account_list[fileno] = data
                sub_State_list[fileno] = Enter_pwd_state
                send_data = "Please enter the password you want:"

    elif(sub_State_list[fileno] == Enter_pwd_state):
        Password_list[fileno] = data
        send_data = "Please enter the password again:"
        sub_State_list[fileno] = Enter_pwd_again_state
    
    elif(sub_State_list[fileno] == Enter_pwd_again_state):
        if data == Password_list[fileno]:
            encrypted_pwd = base64.b64encode(data.encode()).decode()
            Account_Dict.update( {Account_list[fileno]:encrypted_pwd})
            send_data = "Sign up Successfully " + Account_list[fileno]
            with open('Account.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for key in Account_Dict:
                    writer.writerow( [key, Account_Dict[key]] )
            State_list[fileno] = Idle_state
            sub_State_list[fileno] = ""
        else:
            send_data = "Wrong\nPlease enter the Account you want:"
            sub_State_list[fileno] = Enter_acc_state
            Account_list[fileno] = ""
            Password_list[fileno] = ""
    else :
        print("sign up error")
    s.send(send_data.encode())

def sign_in_service(s, data):
    fileno = s.fileno()
    #get the account and password from client sending

    #print("Sign in : ",sub_State_list[fileno] , "data = ", data)
    if sub_State_list[fileno] == Enter_acc_state:
        if data in Account_Dict:
            Account_list[fileno] = data
            sub_State_list[fileno] = Enter_pwd_state
            send_data = "Enter Password:"
        else:
            send_data = "Account not exists, please enter a valid account"

    elif sub_State_list[fileno] == Enter_pwd_state:
        if base64.b64encode(data.encode()).decode() == Account_Dict[Account_list[fileno]] :
            print("Login successfully")
            send_data = "Login successfully " + Account_list[fileno]
            #logging_list.append( Account_list[fileno] )
            Login_list[fileno] = True
            State_list[fileno] = Idle_state
            sub_State_list[fileno] = Idle_state
        else :
            print("Login fail")
            send_data = "Wrong password, please enter again."
    else :
        print("sign in error")
    send_data += exit_postfix
    s.send(send_data.encode())
    
def Login_service(s, data):
    fileno = s.fileno()
    if(State_list[fileno] == Idle_state):        
        send_data = "Login unknown command, please try again\n"
        send_data += "Enter 'Sign in' to sign in, 'Sign up' to sign up."
        if(data == "Sign in"):
            send_data = "Please enter your account:"
            State_list[fileno] = Sign_in_state
            sub_State_list[fileno] = Enter_acc_state
        elif(data == "Sign up"):
            send_data = "Please enter the account you want:"
            State_list[fileno] = Sign_up_state
            sub_State_list[fileno] = Enter_acc_state
        elif(data == "(Exit)"):
            close_connection(s)
            return
        s.send(send_data.encode())

    elif data == '(Exit)':
        send_data = Back_to_login_interface(fileno)
        s.send(send_data.encode())
        return

    elif(State_list[fileno] == Sign_in_state):
        sign_in_service(s, data)        
    elif(State_list[fileno] == Sign_up_state):
        sign_up_service(s, data)
    else:
        print("Unknown state when loging")

def Check(s, account):
    fileno = s.fileno()
    send_data = account + " is not online"
    if account not in Account_Dict:
        send_data = account + " is not a existing account"
    for i in range(len(Account_list)):
        if Account_list[i] == account and Login_list[i] == True:
            send_data = account + " is online"
    return send_data

def List(fileno):
    send_data = ""
    for i in range(len(Account_list)):
        if Login_list[i] == True and i != fileno:
            send_data += Account_list[i] + " is online.\n"
    if send_data == "":
        send_data = "Only you are online."
    else:
        send_data = send_data[:-1]
    return send_data

# A's socket wanna talk to B
# filenoA is A's fileno
# A, B are there account
def Start_Offline_Chat(filenoA, B):
    A = Account_list[filenoA]
    filename = ""
    if A < B:
        filename = A + B + ".log"
    else:
        filename = B + A + ".log"
    Chat_History[fileno] = []
    try :
        Wf_list[filenoA] = open( filename, "r")
        Chat_History[filenoA] = []
        for i, line in enumerate(Wf_list[filenoA].readlines()):
            line = line.strip()
            Chat_History[filenoA] = ([])
            cut = line.find(":")
            Chat_History[filenoA][i].append(line[:cut])
            Chat_History[filenoA][i].append(line[cut+1:])
    except :
        Wf_list[filenoA] = open( filename, "w")
        
'''
def Chat(s, data):
    fileno = s.fileno()
    if data == "(Exit)":
    # leaving
        send_data = "(Exit)" + "Back to menu"
        State_list[fileno] = Idle_state
        sub_State_list[fileno] = Idle_state
    # tell the other that this one is leaving
    # Change to offline Chat 
    if(sub_State_list[fileno] == "Offline Chat"):
        
    elif(sub_State_list[fileno] == "Online Chat"):
        
    else:
        print("Unknown State while chatting, Back to Idle State")
        State_list[fileno] = Idle_state
        sub_State_list[fileno] = Idle_state
'''     

# def log_offline_data(fileno, accountB):
    



def After_Login_service(s, data):
    fileno = s.fileno()
    if(State_list[fileno] == Idle_state):
        data = data.split()
        sub_State_list[fileno] = Idle_state
        if(data[0] == "Help"):
            send_data =  "-------Help--------"
            send_data += "\ncommand:"
            send_data += "\nCheck [account]"
            send_data += "\nChat [account]"
            send_data += "\nList"
            send_data += "\nSendFile [account] [file1] [file2] ..."
            send_data += "\n(Exit)"
            send_data += "\n--------------------"

        elif(data[0] == "Check"):
            if(len(data) != 2) : send_data = "Please enter as the following type:\nCheck [account]"
            else : send_data = Check(s, data[1])

        elif(data[0] == "List"):
            if(len(data) != 1) : send_data = "Please enter as the following type:\nList"
            send_data = List(fileno)

        elif(data[0] == "Chat"):
            chat_object = data[1]
            if(len(data) != 2) : 
                send_data = "Please enter as the following type:\nChat [account]"
            elif chat_object not in Account_Dict : 
                send_data = data[1] + " is not an existing account"
            elif chat_object == Account_list[fileno]:
                send_data = "Though you're a outsider, you still can't talk to yourself!"
            else:
                log_offline_data(fileno, chat_object)
                State_list[fileno] = Chat_state
                Chat_object_list[fileno] = account
                # Check if online
                online_flag = False
                send_data = ""
                for i in range(len(Account_list)):
                    if Account_list[i] == chat_object and Login_list[i] == True:
                        Chat_object_fileno_list[fileno] = i
                        online_flag = True
                        break
                #     if online, ask B if he wants to chat
                if online_flag:
                #   if B is communicating through offline chat
                #   -> online chat for them
                    filenoB = Chat_object_fileno_list[fileno]
                    if State_list[filenoB] == Chat_State and sub_State_list[filenoB] == "Offline Chat" and Chat_object_list[filenoB] == Account_list[fileno]:
                        Start_Online_chat( fileno, filenoB)
                        sub_State_list[fileno] = "Online Chat"
                    # asking 
                    else:
                        send_data = "Asking " + account + " if he/she wants to chat with you ..."
                        send_data += "\nYou can still sent send messages as you want"
                        sub_State_list[fileno] = "Offline Chat"
                        Start_Offline_chat(Account_list[fileno], account)
                #         yes: online chat
                #         no : offline chat
                #     else offline chat
                else :
                    send_data = account + " is not online\nStart offline chatting"
                    sub_State_list[fileno] = "Offline Chat"
                    Start_Offline_chat(Account_list[fileno], account)
                

            

        elif(data[0] == "SendFile"):
            send_file_object = data[1]
            if( len(data) <= 2 ) send_data = "Please enter as the following type:\nSendFile [account] [file1] [file2] ..."
            elif send_file_object not in Account_Dict : 
                send_data = data[1] + " is not an existing account"
            elif send_file_object == Account_list[fileno]:
                send_data = "Though you're a outsider, you still can't send a file to yourself!"
            # check if online
            online_flag = False
            send_data = "NAK"
            for i in range(len(Account_list)):
                if Account_list[i] == send_file_object and Login_list[i] == True:
                    online_flag = True
                    Chat_object_fileno_list[fileno] = i
                    Chat_object_list[fileno] = send_file_object
                    send_data = "ACK"
                    break
            if online_flag:
                Transfer_file_list = data[2:]
                Chat_object_list[fileno] = send_file_object
                State_list[fileno] = "Sendfile"
                Transfer_file(Socket_list[fileno], Socket_list[Chat_object_fileno_list[fileno]], Transfer_file_list)
        
        elif(data[0] == "(Exit)"):
            send_data = Back_to_login_interface(fileno)
        else:
            send_data = "Unknown command, please enter again"
        s.send(send_data.encode())
    elif(State_list[fileno] == Chat_state):
        Chat(fileno, data)
    else:
        print("Unknown State, Maybe a bug or undone")
        Back_to_login_interface(fileno)
        

def do_service(s, recv_data):
    if(Login_list[s.fileno()] == False):
        print("Login_service")
        Login_service(s, recv_data)
    else:
        print("After Login service")
        After_Login_service(s, recv_data)
    Print_State(s.fileno())


def close_connection(s):
    fileno = s.fileno()
    print('closing connection to', addr_list[s.fileno()])
    addr_list[fileno] = ''
    Chat_object_fileno_list[fileno] = -1
    try:
        Wf_list[fileno].close()
    except:
        pass
    Wf_list[fileno] = None
    Login_list[fileno] = False
    State_list[fileno] = Idle_state     
    sub_State_list[fileno] = Idle_state
    readset.remove(s)
    s.close()

def Back_to_login_interface(fileno):
    send_data = "Back to login interface." + interface_postfix
    Chat_object_fileno_list[fileno] = -1
    Wf_list[fileno] = None
    Login_list[fileno] = False
    Account_list[fileno] = ""
    State_list[fileno] = Idle_state
    sub_State_list[fileno] = Idle_state
    return send_data


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


def Print_State(fileno):
    print("--- print state ----")
    print("fileno    =", fileno)
    print("Account   =", Account_list[fileno])
    x = ""
    if Login_list[fileno] == True:
        x = "Yes"
    else:
        x = "No"
    print("Log in?    ", x)
    print("State     =", State_list[fileno])
    print("sub State =", sub_State_list[fileno])



if __name__ == "__main__":
    #-------Initialize all variable-------
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 1234
    
    PORT = Change_Port(PORT)

    Sock_list = []

    # a fileno -> a state and a substate
    addr_list = []

    # boolean for whether it is login
    Login_list = []
    # Potential State_list = [ Idle_state, Sign_in_state, Sign_up_state, Check_state, Chat_state]
    State_list = []
    # Potential sub_State_list = [ "", "Disconnected"(?), Enter_acc_state, Enter_pwd_state, Enter_pwd_again_state, "Receive Offline message", "Start talking"]
    sub_State_list = []
    
    # these 2 lists are for the server to store msg
    # due to there will be 2 different pkg for the 2 msg
    Account_list = []
    Password_list = []
    
    Transfer_file_list = []
    # writefile list
    Wf_list = []
    # Chat object list (account), fileno_list : if online, then its fileno
    Chat_object_list = []
    Chat_object_fileno_list = []
    Chat_History_data = []

    for i in range(1500):
        Transfer_file_list.append([])
        Sock_list.append(None)
        addr_list.append('')
        Account_list.append('')
        Password_list.append('')
        Wf_list.append(None)
        Chat_object_list.append("")
        Chat_object_fileno_list.append(-1)
        Chat_History_data.append([])
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

    
