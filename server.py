import socket
import select
import types
import os
import base64
import csv


def accept_wrapper(s):
    #only deal with accept client
    conn, addr = s.accept()
    print('accept connection from', addr)
    conn.setblocking(False)
    addr_list[conn.fileno()] = addr
    State_list[conn.fileno()] = "Login Interface"
    readset.append(conn)
    conn.send("Connected to the server".encode())


def sign_up_service(fileno, data):
    #get the account and password from client sending
    if(sub_State_list[fileno] == "Enter Account"):
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
                # 對於每個key(英文單字),及words[key](中文)做寫入，其中兩者會被寫入到同一行
                for key in Account_Dict:
                    writer.writerow( [key, Account_Dict[key]] )
            State_list[fileno] = "Login Interface"
            sub_State_list[fileno] = ""
        else:
            send_data = "Wrong\nPlease enter the Account you want:"
            sub_State_list[fileno] = "Enter Account"
            tmp_pwd[fileno] = ""
            tmp_acc[fileno] = ""
    else :
        print("sign up error")
    s.send(send_data.encode())

    
    
    #create a string that contains currently context of passwd file
    #data_back_passwd = ''
    #for j in passwd_list:
    #    data_back_passwd += str(j) + ":"
    #if account in passwd_list:
    #    send_data = 'NAK'
    #    s.send(send_data.encode())
    #else:
    #    send_data = 'ACK'
    #    s.send(send_data.encode())
    #    password = base64.b64encode(password.encode())
    #    password = password.decode()
    #    #if sign up success, append the account and encrypted password to passwd file
    #    data_back_passwd += account + ":" + password + ":"
    #    print('register success')
    ##write all context back to passwd file
    #f.seek(0)
    #f.write(data_back_passwd)
    #f.close()

def sign_in_service(fileno, data):

    #get the account and password from client sending
    #if data == '(Exit)':
        
        # Back to login interface
        # Communicate_Exit(fileno)
    print("Sign in : ",sub_State_list[fileno] , "data = ", data)
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
            State_list[fileno] = "Choose person"
            sub_State_list[fileno] = "Unuse"
        else :
            send_data = "Wrong password, please enter again."
    else :
        print("sign in error")
    send_data += "\nYou can enter '(Exit)' to exit whenever you want."

    s.send(send_data.encode())
    
def Login_service(fileno, data):
    if(data == "Sign in"):
        send_data = "Please enter your account:"
        State_list[fileno] = "Sign in"
        sub_State_list[fileno] = "Enter Account"
    elif(data == "Sign up"):
        send_data = "Please enter the account you want:"
        State_list[fileno] = "Sign up"
        sub_State_list[fileno] = "Enter Account"
    else :
        send_data = "Login unknown command, please try again\n"
        send_data += "Enter 'Sign in' to sign in, 'Sign up' to sign up."
    s.send(send_data.encode())

def do_service(fileno, recv_data):
    recv_data = recv_data.decode()
    if(State_list[fileno] == "Login Interface"):
        Login_service(fileno, recv_data)
    elif(State_list[fileno] == "Sign in"):
        sign_in_service(fileno, recv_data)        
    elif(State_list[fileno] == "Sign up"):
        sign_up_service(fileno, recv_data)
    else :
        print("do service error(state error)")
    # data = recv_data.split(":")
    # if data[0] == 'Sign in':
    #     sign_in_service(data) 
    # elif data[0] == 'Sign up':
    #     sign_up_service(data)
    # not done yet
    #


def service_connection(s):
    # if client send a request. If the data of the request is none, close this client's fd
    data = s.recv(1024)
    if data:
        do_service(s.fileno(), data)
    else:
        print('closing connection to', addr_list[s.fileno()])
        addr_list[s.fileno()] = ''
        State_list[s.fileno()] = "Unuse"
        sub_State_list[s.fileno()] = "Unuse"
        readset.remove(s)
        s.close()

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

    # Potential State_list = [ "Unuse", "Login Interface", "Sign in", "Sign up", "Choose person", "Communicating"]
    # Potential sub_State_list = [ "Unuse", "Disconnected", "Enter Account", "Enter Password", "Enter Password again", "Receive Offline message", "Start talking"]
    # a fileno -> a state and a substate
    addr_list = []
    State_list = []
    sub_State_list = []
    # these 2 lists are for the server to store msg
    # due to there will be 2 different pkg for the 2 msg
    tmp_acc = []
    tmp_pwd = []
    for i in range(1500):
        addr_list.append('')
        tmp_acc.append('')
        tmp_pwd.append('')
        State_list.append("Unuse")
        sub_State_list.append("Unuse")
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

    
