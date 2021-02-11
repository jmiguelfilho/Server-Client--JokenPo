
import tkinter as tk
from tkinter import PhotoImage
from tkinter import messagebox
import socket
from time import sleep
import threading

# Janela Principal
window_main = tk.Tk()
window_main.title("JokenPo - Cliente")
nome_cliente = ""
nome_adversario = ""
turno = 0
game_timer = 4
escolha_cliente = ""
escolha_server = ""
PARTIDAS = 5
cliente_score = 0
server_score = 0

# Rede Cliente
client = None
HOST_ADDR = "192.168.0.5"
HOST_PORT = 8080


top_welcome_frame= tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text = "Nome:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Conectar", command=lambda : connect())
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line = tk.Label(top_message_frame, text="***********************************************************").pack()
lbl_welcome = tk.Label(top_message_frame, text="")
lbl_welcome.pack()
lbl_line_server = tk.Label(top_message_frame, text="***********************************************************")
lbl_line_server.pack_forget()
top_message_frame.pack(side=tk.TOP)


top_frame = tk.Frame(window_main)
top_left_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_nome_cliente = tk.Label(top_left_frame, text="Nome: " + nome_cliente, font = "Helvetica 13 bold")
lbl_nome_adversario = tk.Label(top_left_frame, text="Servidor: " + nome_adversario)
lbl_nome_cliente.grid(row=0, column=0, padx=5, pady=8)
lbl_nome_adversario.grid(row=1, column=0, padx=5, pady=8)
top_left_frame.pack(side=tk.LEFT, padx=(10, 10))


top_right_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_turno = tk.Label(top_right_frame, text="O jogo comecara em ...", foreground="blue")
lbl_timer = tk.Label(top_right_frame, text=" ", foreground="blue")
lbl_turno.grid(row=0, column=0, padx=5, pady=5)
lbl_timer.grid(row=1, column=0, padx=5, pady=5)
top_right_frame.pack(side=tk.RIGHT, padx=(10, 10))

top_frame.pack_forget()

middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()
lbl_line = tk.Label(middle_frame, text="**** Jokenpo ****", font = "Helvetica 13 bold", foreground="blue").pack()
lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()

round_frame = tk.Frame(middle_frame)
lbl_round = tk.Label(round_frame, text="Round")
lbl_round.pack()
lbl_escolha_cliente = tk.Label(round_frame, text="Sua Escolha: " + "-", font = "Helvetica 13 bold")
lbl_escolha_cliente.pack()
lbl_escolha_server = tk.Label(round_frame, text="Escolha do Server: " + "-")
lbl_escolha_server.pack()
lbl_result = tk.Label(round_frame, text=" ", foreground="blue", font = "Helvetica 14 bold")
lbl_result.pack()
round_frame.pack(side=tk.TOP)

final_frame = tk.Frame(middle_frame)
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
lbl_final_result = tk.Label(final_frame, text=" ", font = "Helvetica 13 bold", foreground="blue")
lbl_final_result.pack()
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
final_frame.pack(side=tk.TOP)

middle_frame.pack_forget()

botao_frame = tk.Frame(window_main)
photo_pedra = PhotoImage(file=r"pedra.gif")
photo_papel = PhotoImage(file = r"papel.gif")
photo_tesoura = PhotoImage(file = r"tesoura.gif")

bot_pedra = tk.Button(botao_frame, text="Pedra", command=lambda : escolha("pedra"), state=tk.DISABLED, image=photo_pedra)
bot_papel = tk.Button(botao_frame, text="Papel", command=lambda : escolha("papel"), state=tk.DISABLED, image=photo_papel)
bot_tesoura = tk.Button(botao_frame, text="Tesoura", command=lambda : escolha("tesoura"), state=tk.DISABLED, image=photo_tesoura)
bot_pedra.grid(row=0, column=0)
bot_papel.grid(row=0, column=1)
bot_tesoura.grid(row=0, column=2)
botao_frame.pack(side=tk.BOTTOM)


def verificar_vencedor(cliente, servidor):
    vencedor = ""
    pedra = "pedra"
    paper = "papel"
    tesoura = "tesoura"
    player0 = "cliente"
    player1 = "servidor"

    if cliente == servidor:
        vencedor = "empate"
    elif cliente == pedra:
        if servidor == paper:
            vencedor = player1
        else:
            vencedor = player0
    elif cliente == tesoura:
        if servidor == pedra:
            vencedor = player1
        else:
            vencedor = player0
    elif cliente == paper:
        if servidor == tesoura:
            vencedor = player1
        else:
            vencedor = player0
    return vencedor


def enable_disable_buttons(todo):
    if todo == "disable":
        bot_pedra.config(state=tk.DISABLED)
        bot_papel.config(state=tk.DISABLED)
        bot_tesoura.config(state=tk.DISABLED)
    else:
        bot_pedra.config(state=tk.NORMAL)
        bot_papel.config(state=tk.NORMAL)
        bot_tesoura.config(state=tk.NORMAL)


def connect():
    global nome_cliente
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="ERROR!", message="Digite seu nome")
    else:
        nome_cliente = ent_name.get()
        lbl_nome_cliente["text"] = "Seu nome: " + nome_cliente
        connect_to_server(nome_cliente)


def count_down(my_timer, nothing):
    global turno
    if turno <= PARTIDAS:
        turno = turno + 1

    lbl_turno["text"] = "Turno " + str(turno) + " comeca em"

    while my_timer > 0:
        my_timer = my_timer - 1
        print("Tempo: " + str(my_timer))
        lbl_timer["text"] = my_timer
        sleep(1)

    enable_disable_buttons("enable")
    lbl_round["text"] = "Turno - " + str(turno)
    lbl_final_result["text"] = ""


def escolha(arg):
    global escolha_cliente, client, turno
    escolha_cliente = arg
    lbl_escolha_cliente["text"] = "Sua Escolha: " + escolha_cliente

    if client:
        client.send("Partida"+str(turno)+escolha_cliente)
        enable_disable_buttons("disable")


def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR, nome_cliente
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name) # Enviar nome do cliente ao servidor


        btn_connect.config(state=tk.DISABLED)
        ent_name.config(state=tk.DISABLED)
        lbl_name.config(state=tk.DISABLED)
        enable_disable_buttons("disable")

        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Nao foi possivel conectar ao host: " + HOST_ADDR + " na porta: " + str(HOST_PORT) + " Servidor Indisponivel...")


def receive_message_from_server(sck, m):
    global nome_cliente, nome_adversario, turno
    global escolha_cliente, escolha_server, cliente_score, server_score

    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        if from_server.startswith("$bemvindo"): #Mensagem de BV
            if from_server == "$bemvindo1$":
                lbl_welcome["text"] = "Bem vindo " + nome_cliente + "! Aguardando todos jogadores..."
            elif from_server == "$bemvindo2$":
                lbl_welcome["text"] = "Bem vindo " + nome_cliente + "! O Jogo vai comecaar..."
            lbl_line_server.pack()

        elif from_server.startswith("nome_adversario$"): #Mensagem Nome adversario
            nome_adversario = from_server.replace("nome_adversario$", "")
            lbl_nome_adversario["text"] = "Adversario: " + nome_adversario
            top_frame.pack()
            middle_frame.pack()

            # Usuarios conectados para poder conectar
            threading._start_new_thread(count_down, (game_timer, ""))
            lbl_welcome.config(state=tk.DISABLED)
            lbl_line_server.config(state=tk.DISABLED)

        elif from_server.startswith("$escolha_server"): #Mensagem Escolha
            # Receber a resposta do oponente
            escolha_server = from_server.replace("$escolha_server", "")

            
            vencedor = verificar_vencedor(escolha_cliente, escolha_server)
            round_result = " "
            if vencedor == "cliente":
                cliente_score = cliente_score + 1
                round_result = "Vitoria"
            elif vencedor == "servidor":
                server_score = server_score + 1
                round_result = "Perdeu"
            else:
                round_result = "Empate"

            # Update da tela
            lbl_escolha_server["text"] = "Escolha do Server: " + escolha_server
            lbl_result["text"] = "Resultado: " + round_result

            
            if turno == PARTIDAS:
                # calc resutlado final
                final_result = ""
                color = ""

                if cliente_score > server_score:
                    final_result = "(Voce venceu!!!)"
                    color = "green"
                elif cliente_score < server_score:
                    final_result = "(Voce Venceu!!!)"
                    color = "red"
                else:
                    final_result = "(Empate!!!)"
                    color = "black"

                lbl_final_result["text"] = "RESULTADO: " + str(cliente_score) + " - " + str(server_score) + " " + final_result
                lbl_final_result.config(foreground=color)
                cliente_score = 0
                server_score = 0
                enable_disable_buttons("disable")
                turno = 0

            # Comecar o temporizador
            threading._start_new_thread(count_down, (game_timer, ""))


    sck.close()


window_main.mainloop()