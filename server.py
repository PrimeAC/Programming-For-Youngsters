# -*- coding: utf-8 -*-

import socket


##########################################################################################################
# INICIALIZAÇÃO

PORTO_SERVIDOR = 5005

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(('', 5005))

enderecos = {}  # dicionário: nome -> endereço  | Exemplo: endereços["utilizador"] = ('127.0.0.1', 17234)
clientes = {}   # dicionário: endereço -> nome  | Exemplo: clientes[('127.0.0.1', 17234)] = "João"
estado = {}     # dicionário: nome -> estado    | Exemplo: estado["utilizador"] = ("ocupado" ou "livre")


##########################################################################################################
# FUNÇÕES DE CADA OPERAÇÃO

def acknowledge(endereco):
    if endereco == "servidor":
        print("Servidor OK")
    else:
        mensagemResposta = "OK" + "\n"
        enderecoJogador = enderecos[comandos[1]]
        servidor.sendto(mensagemResposta.encode(), enderecoJogador)
    return

def error(mensagemErro, enderecoJogador):
    mensagemResposta = "Mensagem de erro: " + mensagemErro
    print(mensagemResposta)
    mensagemResposta = "MensagemInformativa " + mensagemResposta
    servidor.sendto(mensagemResposta.encode(), enderecoJogador)
    return

def registarCliente(nome, endereco):
    # Verificar se o nome já está a ser usado
    if nome in enderecos:
        mensagemErro = "Nome de utilizador " + nome + " ja esta a ser usado."
        error(mensagemErro, endereco)
    # Verificar se o endereço já está a ser usado
    elif endereco in clientes:
        mensagemErro = "Endereco " + str(endereco) + " ja esta a ser usado."
        error(mensagemErro, endereco)
    # Adicionar um novo jogador
    else:
        enderecos[nome] = endereco
        clientes[endereco] = nome
        estado[nome] = "Livre"
        mensagemResposta = "Registado com o nome {}".format(nome)
        print(mensagemResposta)
        mensagemResposta = "MensagemInformativa " + mensagemResposta
        servidor.sendto(mensagemResposta.encode(), endereco)
        acknowledge(endereco)
    return

def removerCliente(endereco):
    # Verificar se o endereço (utilizador) existe
    if endereco in clientes:
        nome = clientes[endereco]
        del enderecos[nome]
        del clientes[endereco]
        del estado[nome]
    servidor.sendto(comandos[0].encode(), endereco)
    return

def listarJogadores(endereco):
    # Verificar se o endereço (utilizador) existe
    if endereco in clientes:
        mensagemResposta = "Listar "
        for nome in estado:
            mensagemResposta = mensagemResposta + nome + " " + estado[nome] + " "
        servidor.sendto(mensagemResposta.encode(), endereco)
    else:
        mensagemErro = "Nao tem acesso!"
        error(mensagemErro, endereco)
    return

def convidarJogador(endereco, jogadorConvidado):
    jogadorConvida = clientes[endereco]
    # Verificar se o destinatário está na lista de endereços
    if jogadorConvidado in enderecos:
        # Verificar se o destinatário não é o próprio que convida
        if jogadorConvidado != jogadorConvida:
            # Verificar se o estado do jogador que fez o convite é diferente de "ocupado"
            if estado[jogadorConvida] != "Ocupado":
                # Verificar se o estado do jogador convidado é "livre"
                if estado[jogadorConvidado] == "Livre":
                    estado[jogadorConvida] = "Ocupado"
                    enderecoConvidado = enderecos[jogadorConvidado]
                    mensagemConvite = "Convidar " + jogadorConvida + " " + jogadorConvidado
                    servidor.sendto(mensagemConvite.encode(), enderecoConvidado)
                    mensagem = "MensagemInformativa Convite enviado para " + jogadorConvidado
                    servidor.sendto(mensagem.encode(), endereco)
                    return
                else:
                    mensagemErro = "Utilizador convidado esta ocupado."
            else:
                mensagemErro = "Esta ocupado, nao pode convidar ninguem."
        else:
            mensagemErro = "Nao se pode convidar a si proprio."
    else:
        mensagemErro = "Utilizador convidado nao existe"
    error(mensagemErro, endereco)
    return

def respostaConvite(jogadorConvidado, jogadorConvida, resposta):
    enderecoConvida = enderecos[jogadorConvida]
    if resposta == "aceitou":
        estado[jogadorConvidado] = "Ocupado"
    else:
        estado[jogadorConvida] = "Livre"
    mensagemResposta = "RespostaConvite " + jogadorConvidado + " " + resposta
    servidor.sendto(mensagemResposta.encode(), enderecoConvida)
    return








#def end_clients():
 #   for addr in clients:
 #       respond_msg = "EXIT"
 #       servidor.sendto(respond_msg.encode(), addr)

#def respond_error(addr):
#    respond_msg = "INVALID MESSAGE\n"
 #   servidor.sendto(respond_msg.encode(),addr)

#def play(src, dest, pos ):
 #   msg = "MOV "+ src + " " + dest + " "+ pos
 #   servidor.sendto(msg.encode(),addrs[dest])

#def endGame(src,dest, pos, msg):
 #   status[src] = "available"
 #   status[dest] = "available"
#    msg = "END "+src+ " " + dest +" "+ pos+" "+msg
 #   servidor.sendto(msg.encode(),addrs[dest])










# CORPO PRINCIPAL

print("Iniciar o servidor no porto {}...".format(PORTO_SERVIDOR))

while True:
    # Lê o que o servidor enviou
    (mensagem, endereco) = servidor.recvfrom(1024)
    mensagem = mensagem.decode()
    comandos = mensagem.split()

    if comandos[0] != "OK":
        print("Comando inserido: " + comandos[0])

    if comandos[0] == "Registar":
        nomeJogador = comandos[1]
        registarCliente(nomeJogador, endereco)
    elif comandos[0] == "Sair" :
        removerCliente(endereco)
    elif comandos[0] == "Listar":
        listarJogadores(endereco)
    elif comandos[0] == "Convidar":
        nomeJogador = comandos[1]
        convidarJogador(endereco, nomeJogador)
    elif comandos[0] == "RespostaConvite":
        jogadorConvidado = comandos[1]
        jogadorConvida = comandos[2]
        resposta = comandos[3]
        respostaConvite(jogadorConvidado, jogadorConvida, resposta)
    #elif comandos[0] == "Movimentar":



 #   elif(comandos[0]=="MOV"):
 #       play(comandos[1],comandos[2],comandos[3])
 #   elif(comandos[0]=="END"):
 #       endGame(comandos[1],comandos[2],comandos[3],comandos[4])
 #   elif(comandos[0]=="KILLSERVER"):
 #       end_clients()
  #      break
  #  else:
  #      respond_error(endereco)

servidor.close()
