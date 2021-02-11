import tkinter as tk
import socket
import random
import threading
from time import sleep


window = tk.Tk()
window.title("Jokenpo - Servidor")
HOST_ADDR = "192.168.0.5"
HOST_PORT = 8080
N = 0


topFrame = tk.Frame(window)
lbl_nplayers = tk.Label(topFrame, text = "Nr Players:")
lbl_nplayers.pack(side=tk.LEFT)
Nl = tk.Entry(topFrame,width=3)
Nl.pack(side=tk.LEFT)
Nl.insert(0,1)
btnStart = tk.Button(topFrame, text="Iniciar", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Off", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Frame do meio
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Endereco: ")
lblHost.pack(side=tk.LEFT)
END = tk.Entry(middleFrame,width=11)
END.pack(side=tk.LEFT)
END.insert(0,HOST_ADDR)
lblPort = tk.Label(middleFrame, text = "Porta: ")
lblPort.pack(side=tk.LEFT)
PORT = tk.Entry(middleFrame,width=5)
PORT.pack(side=tk.LEFT)
PORT.insert(0,HOST_PORT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# Frame do cliente
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="********Jogadores Online********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None


#print HOST_ADDR + "p" + str(HOST_PORT)
client_name = " "
clients = []
clients_names = []
player_data = []
#N = 3 #Numero de clientes para jogar



def start_server():
    global server, HOST_ADDR, HOST_PORT, N 
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)
    HOST_ADDR = END.get()
    HOST_PORT = int (PORT.get())
    N = int (Nl.get())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print socket.AF_INET #Socket para com IPV4
    #print socket.SOCK_STREAM
    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Endereco: "
    lblPort["text"] = "Porta: "


def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def accept_clients(the_server, y):
    while True:
        if len(clients) < N:
            client, addr = the_server.accept()
            clients.append(client)

            
            threading._start_new_thread(send_receive_client_message, (client, addr))


def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, player_data, player0, player1

    client_msg = " "

    client_name = client_connection.recv(4096)
    if len(clients) < N:
        client_connection.send(bytes("$bemvindo1$", 'utf-8'))
    else:
        client_connection.send(bytes("$bemvindo2$", 'utf-8'))

    clients_names.append(client_name)
    update_client_names_display(clients_names)  # Atualizar os nomes dos clientes

    if len(clients) == N:
        sleep(1)

        #Enviar nome oponente
        count = 0
        while count < len(clients):

            clients[count].send(bytes("nome_adversario$Servidor", 'utf-8')) #Mensagem Nome envia
            count += 1

    while True:
        data = client_connection.recv(4096) 
        if not data: break


        player_escolha = data[11:len(data)]

        msg = {
            "escolha": player_escolha,
            "socket": client_connection
        }

        x = random.randint(1,3);
        if x == 1:
            s_escolha = "pedra"
        elif x == 2:
            s_escolha = "papel"
        elif x == 3:
            s_escolha = "tesoura"

        if len(player_data) < N:
            player_data.append(msg)

        if len(player_data) == N:

            count = 0
            while count < N: #Mensagem para todos players da escolha aleatoria
                player_data[count].get("socket").send(bytes(("$escolha_server" + s_escolha), 'utf-8')) 

                count += 1

            player_data = []


    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()

    update_client_names_display(clients_names)  # Atualizar display dos nomes



def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx



def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, str(c.decode('utf-8'))+("\n"))
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()