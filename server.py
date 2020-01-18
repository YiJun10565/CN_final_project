import socket
import select
import types
import os
import base64
import csv

# string
# -------------

interface_postfix = "\nEnter 'Sign in' or 'Sign up'"
exit_postfix = "\nYou can enter '(Exit)' to exit whenever you want."
Idle_state = "Idle"
Sign_in_state = "Sign in"
Sign_up_state = "Sign up"
Enter_acc_state = "Enter Account"
Enter_pwd_state = "Enter Password"
Enter_pwd_again_state = "Enter Password again"

repeat_login_state = "Repeat Login"
Chat_state = "Chat"
Team_Chat_state = "TeamChat"
Check_state = "Check"
Offline_Chat_state = "Offline Chat"
Online_Chat_state = "Online Chat"
Sending_File_state = "Sending File"
Receive_state = "Receiving File"

# -------------

class Client:
    def __init__(self):
        self.socket = None
        self.address = ""
        self.login = False
        self.state = Idle_state
        self.substate = Idle_state
        self.emgstate = Idle_state
        self.account = ""
        self.password = ""
        self.friend_account = ""
        self.friend_ID = -1
        self.friend_history_data = []

    def build_Connection(self, socket, address):
        self.socket = socket
        self.address = address

    def close_Connection(self):
        self.Log_out()
        self.socket.close()
        self.address = ""

    def Log_out(self):
        self.login = False
        self.state = Idle_state
        self.substate = Idle_state
        self.account = ""
        self.password = ""
        self.friend_account = ""
        self.friend_ID = -1
        self.friend_history_data = []

    def start_Chat(self, substate):
        self.state = Chat_state
        self.substate = substate

    def Log_in(self):
        self.login = True
        self.state = Idle_state
        self.substate = Idle_state
        self.friend_account = ""
        self.friend_ID = -1
        self.friend_history_data = []

    def print_State(self):
        print("--- print state ----")
        print("fileno    =", self.socket.fileno())
        print("Account   =", self.account)
        print("Log in?    ", self.login)
        print("State     =", self.state)
        print("sub State =", self.substate)
        print("emg State =", self.emgstate)
        print("-------------------")

def accept_wrapper(s_server):
    #only deal with accept client
    conn, addr = s_server.accept()
    print('accept connection from', addr)
    ID = conn.fileno()

    clients[ID].build_Connection(conn, addr)
    clients[ID].socket.setblocking(False)

    readset.append(clients[ID].socket)

    send_data = "Connected to the server" + interface_postfix + exit_postfix
    clients[ID].socket.send(send_data.encode())

def sign_up_service(ID, data):
    #get the account and password from client sending
    if(clients[ID].substate == Enter_acc_state):
        invalid_name = False
        for x in data:
            if not x.isdigit() and not x.isalpha():
                invalid_name = True
                break

        if invalid_name:
            send_data = "Invalid account, please enter a valid one (only contains 0~9, a~z, A~Z)"
        else:
            if data in Account_Dict:
                send_data = "Account has already existed:"
            else:
                clients[ID].account = data
                clients[ID].substate = Enter_pwd_state
                send_data = "Please enter the password you want:"

    elif clients[ID].substate == Enter_pwd_state:
        if data == "(Exit)":
            clients[ID].Log_out()
            send_data = "(Exit)"
        else:
            clients[ID].password = data
            send_data = "Please enter the password again:"
            clients[ID].substate = Enter_pwd_again_state
    
    elif clients[ID].substate == Enter_pwd_again_state:
        if data == clients[ID].password:
            encrypted_pwd = base64.b64encode(data.encode()).decode()
            newAccount = {clients[ID].account : encrypted_pwd}
            Account_Dict.update(newAccount)

            send_data = "Sign up Successfully, " + clients[ID].account

            with open('Account.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([clients[ID].account, encrypted_pwd])

            clients[ID].password = encrypted_pwd
            clients[ID].Log_in()

        else:
            send_data = "Wrong password.\nPlease enter the Account you want:"
            clients[ID].substate = Enter_acc_state
            clients[ID].account = ""
            clients[ID].password = ""
    else:
        print("sign up error")
    
    return send_data

def sign_in_service(ID, data):

    if clients[ID].substate == Enter_acc_state:
        if data in Account_Dict:
            clients[ID].account = data
            clients[ID].substate = Enter_pwd_state
            send_data = "Enter Password:"
        else:
            send_data = "Account not exists, please enter a valid account."

    elif clients[ID].substate == Enter_pwd_state:
        if base64.b64encode(data.encode()).decode() == Account_Dict[clients[ID].account] :
            print("Login successfully")
            send_data = "Welcome Home, " + clients[ID].account \
                + "\nPlease enter your command.\nType 'Help' to check the details of commands."
            clients[ID].Log_in()
            check_repeat_login(ID)
        else :
            print("Login fail")
            send_data = "Wrong password, please enter again."
    else:
        print("sign in error")

    #send_data += exit_postfix
    return send_data
    
def Login_service(ID, rawdata):
    print("Login_service")

    data = rawdata.decode()
    send_data = ""

    if clients[ID].state == Idle_state:        

        if data == "Sign in":
            send_data = "Please enter your account:"
            clients[ID].state = Sign_in_state
            clients[ID].substate = Enter_acc_state

        elif data == "Sign up":
            send_data = "Please enter the account name you want:"
            clients[ID].state = Sign_up_state
            clients[ID].substate = Enter_acc_state

        elif data == "(Exit)":
            clients[ID].socket.sendall("Byebye~~".encode())
            close_connection(clients[ID].socket)
            return

        else:
            send_data = "Unknown command, please try again.\nEnter 'Sign in' or 'Sign up'."

    elif data == '(Exit)':
        send_data = "Back to login interface."
        clients[ID].Log_out()

    elif clients[ID].state == Sign_in_state:
        send_data = sign_in_service(ID, data)   

    elif clients[ID].state == Sign_up_state:
        send_data = sign_up_service(ID, data)

    else:
        clients[ID].Log_out()
        print("Unknown state when logging in.")

    clients[ID].socket.sendall(send_data.encode())

def check_Account_Status(account):
    if account not in Account_Dict:
        return -1
    for i, client in enumerate(clients):
        if client.account == account and client.login == True:
            return i
    return 0

def find_Filename(ID):
    A = clients[ID].account
    B = clients[ID].friend_account
    filename = ""
    if A < B:
        filename = A + '_' + B + ".log"
    else:
        filename = B + '_' + A + ".log"

    return filename

def load_History_Data(ID):
    clients[ID].friend_history_data = []

    filename = find_Filename(ID)

    if os.path.isfile(filename):
        with open(filename, 'r+') as CH:
            for i, line in enumerate(CH.readlines()):
                clients[ID].friend_history_data.append(line)
        
        send_data = ""
        for line in clients[ID].friend_history_data:
            send_data += line
        send_data = send_data[:-1]
        print(send_data)
        clients[ID].socket.sendall(send_data.encode())

    else:
        print("no file")

def start_Offline_Chat(ID):
    clients[ID].start_Chat(Offline_Chat_state)

def start_Online_Chat(ID):
    clients[ID].start_Chat(Online_Chat_state)
    clients[clients[ID].friend_ID].start_Chat(Online_Chat_state)

    send_data = "*** " + clients[ID].account + " has entered the room!! ***"
    clients[clients[ID].friend_ID].socket.sendall(send_data.encode())

def getID(account):
    for i, client in enumerate(clients):
        if client.account == account:
            return i
    return -1

def Help_service(ID):
    send_data =  "------ Help -------"
    send_data += "\ncommand:"
    send_data += "\nCheck [account]"
    send_data += "\nChat [account]"
    send_data += "\nTeamChat [teamname](if not exist, create one)"
    send_data += "\nlist Online Account"
    send_data += "\nSendFile [account] [file1] [file2] ..."
    send_data += "\n(Exit)"
    send_data += "\n-------------------"

    clients[ID].socket.send(send_data.encode())

def Check_service(ID, friend_account):
    acc_stat = check_Account_Status(friend_account)
    if acc_stat > 0:
        send_data = friend_account + " is online."
    elif acc_stat == 0:
        send_data = friend_account + " is offline."
    else:
        send_data = friend_account + " not exists."

    clients[ID].socket.sendall(send_data.encode())

def list_Online_Accounts_service(ID):
    send_data = ""
    for i, client in enumerate(clients):
        if client.login == True and i != ID:
            send_data += client.account + " is online.\n"

    if send_data == "":
        send_data = "Only you are online."
    else:
        send_data = send_data[:-1]

    clients[ID].socket.sendall(send_data.encode())

def Check_for_Chat_service(ID, friend_account):
    acc_stat = check_Account_Status(friend_account)

    if acc_stat == -1: 
        clients[ID].socket.sendall((friend_account + " is not an existing account.").encode())

    elif acc_stat == ID:
        clients[ID].socket.sendall("Though you're a outsider, you still can't talk to yourself!".encode())

    elif acc_stat == 0:
        clients[ID].friend_account = friend_account
        clients[ID].friend_ID = getID(friend_account)
        load_History_Data(ID)
        start_Offline_Chat(ID)

    else: # friend is online
        friend_ID = acc_stat

        clients[ID].friend_account = friend_account
        clients[ID].friend_ID = friend_ID
        
        # inform chat 

        if clients[friend_ID].state == Chat_state \
            and clients[friend_ID].substate == "Offline Chat" \
            and clients[friend_ID].friend_ID == ID:
            clients[ID].socket.sendall("Start Online Chat!!!".encode())
            load_History_Data(ID)
            start_Online_Chat(ID)

        else:
            clients[ID].socket.sendall("Start Offline Chat...".encode())
            load_History_Data(ID)
            start_Offline_Chat(ID)

def Chat(ID, data):
    if data == "(Exit)":
        clients[ID].Log_in()
        return

    chat_line = clients[ID].account + ": " + data

    clients[ID].friend_history_data.append([clients[ID].account, data])
    if clients[ID].substate == Online_Chat_state:
        clients[clients[ID].friend_ID].friend_history_data.append([clients[ID].account, data])
        clients[clients[ID].friend_ID].socket.sendall(chat_line.encode())

    filename = find_Filename(ID)
    with open(filename, 'a+') as CH:
        CH.write(chat_line + "\n")

def check_repeat_login(ID):
    for i, client in enumerate(clients):
        if i != ID and client.login and client.account == clients[ID].account and client.emgstate == Idle_state:
            client.emgstate = repeat_login_state
            send_data = "[Sysyem Message]Your account '"+ client.account + "' has been logged in from "+ clients[ID].address[0] + ":"+ str(clients[ID].address[1])
            send_data += "\nType 'Kick' to kick or do any other thing to forgive it."
            client.socket.sendall(send_data.encode())

def transfer_Files(s_sender, s_receiver, filenames):
    # send filenames
    s_receiver.sendall(struct.pack('i', len(filenames)))
    s_receiver.sendall(pickle.dumps(filenames))
    
    # send files' content
    for file in range(len(filenames)):
        size = struct.unpack('i', s_sender.recv(4))[0]
        print(size)
        content = s_sender.recv(size)
        
        s_receiver.sendall(struct.pack('i', size))
        s_receiver.sendall(content)

def Create_Team(ID, Team_name):
    filename = Team_name + ".teamlog"
    open(filename, "w").close()
    filename = Team_name + ".teamset"
    with open(filename, "w") as teamsetfile:
        teamsetfile.write( "0000\n")
        teamsetfile.write(clients[ID].account + "\n")

def get_Team_password(Team_name):
    filename = Team_name + ".teamset"
    pwd = ""
    with open(filename, "r") as teamsetfile:
        pwd = teamsetfile.readline().strip()
    return pwd

def Start_Team_Chat(ID):
    clients[ID].substate = "chat"
    clients[ID].friend_history_data = []
    filename = clients[ID].friend_account + ".teamlog"
    if os.path.isfile(filename):
        with open(filename, 'r+') as CH:
            for i, line in enumerate(CH.readlines()):
                clients[ID].friend_history_data.append(line)
        
        send_data = ""
        for line in clients[ID].friend_history_data:
            send_data += line
        send_data = send_data[:-1]
        print(send_data)
        clients[ID].socket.sendall(send_data.encode())

def Team_Chat(ID, data):
    if data == "(Exit)":
        clients[ID].Log_in()
        return
    

    chat_line = clients[ID].account + ": " + data

    clients[ID].friend_history_data.append([clients[ID].account, data])
    
    for i, client in enumerate(clients):
        if client.login \
            and i != ID\
            and client.state == Team_Chat_state \
            and client.substate == "chat" \
            and client.friend_account == clients[ID].friend_account:

            client.friend_history_data.append([clients[ID].account, data])
            client.socket.sendall(chat_line.encode())        
    filename = clients[ID].friend_account + ".teamlog"
    print(filename)
    with open(filename, 'a') as CH:
        CH.write(chat_line + "\n")

def Home_service(ID, rawdata):
    print("Home_service")

    if not hasattr(Home_service, "first"):
        Home_service.first = True

    data = rawdata.decode()
    
    if clients[ID].emgstate == repeat_login_state:
        if "Kick" in data:
            for i, client in enumerate(clients):
                if i != ID and client.login and client.account == client.account:
                    clients[i].Log_out()
                    send_data = "[System Message]You have been kicked out due to the repeated login."
                    client.socket.sendall(send_data.encode())
        clients[ID].emgstate = Idle_state
        return

    if clients[ID].state == Idle_state:
        data1 = data
        data = data.split()

        if data[0] == "Help":
            Help_service(ID)

        elif data[0] == "Check":
            if len(data) != 2: 
                send_data = "Please enter as the following format:\nCheck [account]"
                clients[ID].socket.sendall(send_data.encode())
                return

            Check_service(ID, data[1])

        elif data1 == "list Online Accounts":
            list_Online_Accounts_service(ID)

        elif data[0] == "Chat":
            friend_account = data[1]
            if len(data) != 2: 
                send_data = "Please enter as the following type:\nChat [account]"
                clients[ID].socket.sendall(send_data)
                return

            Check_for_Chat_service(ID, friend_account)

        elif data[0] == "TeamChat":
            if len(data) == 2 :
                clients[ID].state = Team_Chat_state
                Team_name = data[1]
                clients[ID].friend_account = Team_name
                filename = Team_name + ".teamlog"
                if not os.path.isfile(filename):
                    Create_Team(ID, Team_name)
                password = "0000"
                in_Team_flag = False
                filename = Team_name + ".teamset"
                with open(filename, "r") as teamsetfile:
                    lines = teamsetfile.readlines()
                    accounts = []
                    for i, line in enumerate(lines):
                        if i != 0 and clients[ID].account == line.strip():
                            in_Team_flag = True
                            break
                if in_Team_flag == True:
                    Start_Team_Chat(ID)
                else :
                    clients[ID].substate = "Enter Team Password"
                    send_data = "Please enter password to join the team"
                    clients[ID].socket.sendall(send_data.encode())
            else :
                send_data = "Length error!\nPlease enter:TeamChat [team]"
                clients[ID].socket.sendall(send_data.encode())
        elif data[0] == "(Exit)":
            clients[ID].Log_out()
            clients[ID].socket.sendall("Logged out.".encode())

        elif data[0] == "SendFile":
            friend_account = data[1]
            if len(data) <= 2:
                clients[ID].socket.sendall("Please enter as the following type:\nSendFile [account] [file1] [file2] ...".encode())
                return
            
            acc_stat = check_Account_Status(friend_account)

            if acc_stat == -1: 
                clients[ID].socket.sendall((data[1] + " is not an existing account.").encode())
            
            elif acc_stat == ID:
                clients[ID].socket.sendall("Though you're a outsider, you still can't send a file to yourself!".encode())
          
            elif acc_stat == 0:
                clients[ID].socket.sendall((data[1] + " is offline so that he/she cannot receive the file QQ").encode())

            else: # friend is online
                friend_ID = acc_stat

                filenames = []
                for filename in filenames:
                    filenames.append(filename)

                clients[ID].state = Sending_File_state
                clients[friend_ID].state = Recieving_File_state
                transfer_Files(clients[ID].socket, clients[friend_ID].socket, filenames)
                clients[ID].state = Idle_state
                clients[friend_ID].state = Idle_state

        else:
            clients[ID].socket.sendall("Unknown command, please enter again.".encode())

    elif clients[ID].state == Chat_state:
        Chat(ID, data)
        Home_service.first = True

    elif clients[ID].state == Receive_state:
        receive_File(ID)

    elif clients[ID].state == Team_Chat_state:
        if clients[ID].substate == "Enter Team Password":
            if data == "(Exit)":
                clients[ID].Log_in()
                return 
            print(get_Team_password(clients[ID].friend_account))
            if get_Team_password(clients[ID].friend_account) == data:
                filename = clients[ID].friend_account + ".teamset"
                with open(filename, "a") as teamsetfile:
                    teamsetfile.write(clients[ID].account + "\n")
                send_file = "Correct Password!\nNow you are a member of " + clients[ID].friend_account
                clients[ID].socket.sendall(send_file.encode())
                Start_Team_Chat(ID)
                  
        elif clients[ID].substate == "chat":
            Team_Chat(ID, data)
        else :
            print("Unknown state while team chat")
            clients[ID].log_in()

    else:
        print("Unknown State, Maybe a bug or undone > <")
        clients[ID].Log_out()
        
def do_service(ID, rawdata):
    if clients[ID].login == False:
        Login_service(ID, rawdata)
    else:
        Home_service(ID, rawdata)

    clients[ID].print_State()

def close_connection(ID):
    print('closing connection to', clients[ID].address)
    
    readset.remove(clients[ID].socket)

    if (clients[ID].substate == Online_Chat_state):
        clients[clients[ID].friend_ID].substate = Offline_Chat_state
        send_data = clients[ID].account + " has left..."
        clients[clients[ID].friend_ID].socket.sendall(send_data)

    clients[ID].close_Connection()

def service_connection(ID):
    # if client send a request. If the data of the request is none, close this client's fd
    data = clients[ID].socket.recv(1024)
    if data:
        do_service(ID, data)
    else:
        close_connection(ID)

def Change_Port(PORT):
    for i in range(1, len(os.sys.argv)):
        if(os.sys.argv[i] == "-p"):
            if i == len(os.sys.argv) -1:
                print("-p can't be the last argv")
            else :
                print("Change port to ", os.sys.argv[i+1])
                PORT = int(os.sys.argv[i+1])
    return PORT

def read_Accounts():
    Account_Dict = {}
    with open("./Account.csv", 'r', newline='') as csvfile:
        # rows is a 2-dim list, [ [acnt0, pswd0],[acnt1, pswd1], ... ]
        rows = csv.reader(csvfile)     
        for row in rows:
            # Save accounts info into a local dictionary
            Account_Dict.update({row[0]: row[1]})
            # print(row)

    return Account_Dict

if __name__ == "__main__":
    #-------Initialize all variable-------
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 1234
    
    PORT = Change_Port(PORT)

    clients = []
    for i in range(10000):
        clients.append(Client())

    # create server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    serv_addr = HOST
    
    # create select set
    readset = [server]
    writeset = []
    exceptionset = []
    server.setblocking(False)

    Account_Dict = read_Accounts()
    
    #-------------------------------------

    print(f'the server is listening at {HOST}:{PORT}')
    print('waiting for connection...')

    while True:
        readable,writable,exceptionable = select.select(readset,writeset,exceptionset,0)
        for s in readable:
            if s is server: # server get a request to create a fd for client
                accept_wrapper(s) 
            else:           # server serve a client reqeust
                service_connection(s.fileno())

    
