# -*- coding: utf-8 -*-

import socket
import sys
import select


##########################################################################################################
# INICIALIZACAO

PORTO_SERVIDOR = 5005
IP_SERVIDOR = '127.0.0.1'
TAMANHO_TABULEIRO = 4
PECA_X = "X"
PECA_O = "O"

cliente = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
inputs = [cliente, sys.stdin]


##########################################################################################################
# FUNCOES DE CADA OPERACAO

def acknowledge(endereco):
	mensagemResposta = "OK " + endereco + "\n"
	cliente.sendto(mensagemResposta.encode(), (IP_SERVIDOR, PORTO_SERVIDOR))
	return

def error(mensagemErro):
	print("Mensagem de erro: " + mensagemErro)
	return

def mensagemInformativa(mensagem):
	i = 1
	mensagemInformativa = ""
	# Vai retornar uma mensagem àquela recebida como argumento mas sem a primeira palavra
	while i < len(mensagem):
		mensagemInformativa = mensagemInformativa + mensagem[i] + " "
		i += 1
	return mensagemInformativa


# FUNÇÕES PARA O STANDARD INPUT

def registarClienteSTDIN(comprimentoMensagem):
	# Erro caso o comprimento da mensagem seja diferente de 2
	if comprimentoMensagem != 2:
		mensagemErro = "Argumentos invalidos. Registe-se outra vez."
		error(mensagemErro)
		return False	
	return True

def convidarJogadorSTDIN(comprimentoMensagem, comandos):
	# Erro caso o comprimento da mensagem seja diferente de 2
	if comprimentoMensagem != 2:
		mensagemErro = "Argumentos invalidos. Convide novamente o jogador."
		error(mensagemErro)
		return False
	elif registado == False:
		mensagemErro = "Tem que se registar primeiro para convidar um jogador."
		error(mensagemErro)
		return False
	elif aJogar == True:
		mensagemErro = "Acabe o jogo primeiro." 
		error(mensagemErro)
		return False		
	return True

def listarJogadoresSTDIN(comprimentoMensagem):
	# Erro caso o comprimento da mensagem seja diferente de 1
	if comprimentoMensagem != 1:
		mensagemErro = "Argumentos invalidos." 
		error(mensagemErro)
		return False
	elif aJogar == True:
		mensagemErro = "Acabe o jogo primeiro." 
		error(mensagemErro)
		return False
	return True

def jogadaValidaSTDIN(comprimentoMensagem, comandos):
	# Erro caso o comprimento da mensagem seja diferente de 2
	if comprimentoMensagem != 2:
		mensagemErro = "Argumentos invalidos. Insira novamente o quadrado em que quer jogar." 
		error(mensagemErro)
		return False
	posicaoTabuleiro = comandos[1]
	# Erro caso o segundo argumento introduzido não seja um número
	try:
		posicaoTabuleiro = int(posicaoTabuleiro)
	except ValueError:
		print("Tem que introduzir um número inteiro, dentro do limite do tabuleiro.")
		return False
	# Erro caso o número do quadrado introduzido não esteja dentro dos limites do tabuleiro
	if posicaoTabuleiro <= 0 or posicaoTabuleiro > TAMANHO_TABULEIRO:
		mensagemErro = "O quadrado em que jogou esta fora dos limites do tabuleiro."
		error(mensagemErro)
		return False
	# Erro caso não esteja a jogar
	elif aJogar == False:
		mensagemErro = "Nao pode jogar, tem que convidar um jogador primeiro."
		error(mensagemErro)
		return False	
	# Erro caso o não seja a vez do jogador efectuar a jogada
	elif myTurn == False:
		mensagemErro = "Espere pela sua vez para jogar"
		error(mensagemErro)
		return False
	return True


# FUNÇÕES PARA O SOCKET

def listarJogadoresSOCKET(mensagem):
	i = 1
	listarJogadores = ""
	print("Lista Jogadores:")
	while i < len(mensagem):
		# Se "i" for número par, mostra o nome do jogador
		if i % 2 != 0:
			listarJogadores = listarJogadores + "Nome: " + mensagem[i] + " | "
		# Caso contrário, mostra o estado para o mesmo jogador
		else:
			listarJogadores = listarJogadores + "Estado: " + mensagem[i] + "\n"
		i = i + 1
	print(listarJogadores)
	return

def conviteJogadorSOCKET(tabuleiro, jogadorConvida, jogadorConvidado):
	global myTurn, aJogar, rival									# Variáveis globais a serem alteradas
	print("Recebeu um convite de " + jogadorConvida + ". Para aceitar o jogo digite [S], para recusar [N].")
	# Resposta introduzida pelo jogador convidado
	respostaConvite = sys.stdin.readline().replace("\n", "")
	# Se a reposta for válida, "S" ou "N", uma mensagem vai ser enviada ao servidor
	if respostaConvite == "S":
		rival = jogadorConvida 										# Jogador rival é quem fez o convite
		desenharTabuleiro(tabuleiro, TAMANHO_TABULEIRO)            				# Desenhar o tabuleiro inicial
		mensagem = "RespostaConvite " + jogadorConvidado + " " + jogadorConvida + " aceitou"
		aJogar = True 													# Flag que indica que o jogo está a decorrer
	# Se a resposta do jogador convidado for "N"
	elif respostaConvite == "N":
		mensagem = "RespostaConvite " + jogadorConvidado + " " + jogadorConvida + " recusou"
	else:
		mensagemErro = "Introduziu incorrectamente a resposta."
		error(mensagemErro)
		conviteJogadorSOCKET(tabuleiro, jogadorConvida, jogadorConvidado)
		return
	cliente.sendto(mensagem.encode(), (IP_SERVIDOR, PORTO_SERVIDOR))
	return

def respostaConviteSOCKET(jogadorConvidado, respostaConvite):
	global myTurn, aJogar, rival									# Variáveis globais a serem alteradas
	print("O jogador " + jogadorConvidado + " " + respostaConvite + " o seu convite.")
	# Se a resposta do jogador convidado for "S", ou o convite foi aceite
	if respostaConvite == "aceitou":
		rival = jogadorConvidado 									# Jogador rival é quem fez o convite
		myTurn = True 													# Flag que indica a vez de jogar
		aJogar = True 													# Flag que indica que o jogo está a decorrer
		tabuleiro = [[0 for x in range(TAMANHO_TABULEIRO)] for y in range(TAMANHO_TABULEIRO)] 
		for i in range(0, TAMANHO_TABULEIRO):
			for j in range(0, TAMANHO_TABULEIRO):
				tabuleiro[i][j] = " "
		desenharTabuleiro(tabuleiro, TAMANHO_TABULEIRO)                			# Desenhar o tabuleiro inicial
	return

def desenharTabuleiro(tabuleiro, tamanho):
	tabuleiroDesenho = "\n "
	# Vai percorrer todos os número de quadrados existentes no tabuleiro
	for numeroQuadrado in range(0, tamanho*tamanho):
		# Verifica se não é o último quadrado da linha
		if (numeroQuadrado + 1) % tamanho != 0:
			# Vai formando uma linha do tabuleiro
			tabuleiroDesenho = tabuleiroDesenho + tabuleiro[numeroQuadrado/tamanho][numeroQuadrado%tamanho] + ' | '
		# É o último quadrado da linha
		else:
			# Acrescenta o último quadrado à linha e imprime-o
			tabuleiroDesenho = tabuleiroDesenho + tabuleiro[numeroQuadrado/tamanho][numeroQuadrado%tamanho]
			print(" " + tabuleiroDesenho)
			# Se não for o último quadrado da última linha imprime um separador de linhas
			if numeroQuadrado != tamanho*tamanho-1:
				tracos = ''
				for i in range(0, tamanho-1):
					tracos = tracos + '---|'
				print(tracos + '---')
				# Prepara uma nova linha
				tabuleiroDesenho = ""
	return

def jogar(tabuleiro, peca, posicaoTabuleiro):
	global myTurn														# Variável global a ser alterada
	# Verificar se posição está vazia
	if tabuleiro[posicaoTabuleiro - 1] == " ":
		tabuleiro[posicaoTabuleiro - 1] = peca
		desenharTabuleiro(tabuleiro, TAMANHO_TABULEIRO)
		myTurn = False													# Passa a vez ao adversário
	# A posição está ocupada
	else:
		if myTurn == True:
			mensagemErro = "O local onde jogou ja contem uma peca. Jogue noutro sitio"
			error(mensagemErro)
			return False
	return










#def makeMove(board, letter, move):

		#  if 1 <= move_number <= 9:
		#      if board[int(move)] == " ":
		#           board[int(move)] = letter
			#          return True
			#     else:
			#         print('Postion {} is already occupied,'
				#                            'please try another one'.format(move_number))
			#         return False
			# else:
		#          print('"{}" is an invalid input number. The provided number should'
				#        ' be from 1 to 9'.format(move_number))
			#         return False

#def isWinner(bo, le):
					# Given a board and a player's letter, this function returns True if that player has won.
					# We use bo instead of board and le instead of letter so we don’t have to type as much.
		#   return ((bo[7] == le and bo[8] == le and bo[9] == le) or # across the top
		#   (bo[4] == le and bo[5] == le and bo[6] == le) or # across the middle
		#   (bo[1] == le and bo[2] == le and bo[3] == le) or # across the bottom
		#   (bo[7] == le and bo[4] == le and bo[1] == le) or # down the left side
		#   (bo[8] == le and bo[5] == le and bo[2] == le) or # down the middle
		#   (bo[9] == le and bo[6] == le and bo[3] == le) or # down the right side
		#   (bo[7] == le and bo[5] == le and bo[3] == le) or # diagonal
		#   (bo[9] == le and bo[5] == le and bo[1] == le)) # diagonal

#def getBoardCopy(board):
					# Make a duplicate of the board list and return it the duplicate.
	#    dupeBoard = []

	#    for i in board:
	#         dupeBoard.append(i)

	#    return dupeBoard

#def isSpaceFree(board, move):
					# Return true if the passed move is free on the passed board.
		#   return board[move] == ' '

#def isBoardFull(board):
					# Return True if every space on the board has been taken. Otherwise return False.
				# for i in range(1, 10):
				#     if isSpaceFree(board, i):
				#            return False
				# return True










# CORPO PRINCIPAL
registado = False												# Variável que indica se está registado ou não
myTurn = False 												# Flag que indica a vez de jogar
aJogar = False													# Variável que indica se se está a jogar ou não
rival = ""														# Jogador adversário
tabuleiro = [[0 for x in range(TAMANHO_TABULEIRO)] for y in range(TAMANHO_TABULEIRO)] 
for i in range(0, TAMANHO_TABULEIRO):
	for j in range(0, TAMANHO_TABULEIRO):
		tabuleiro[i][j] = " "

while True:
	
	if aJogar == True:
		if myTurn == True:
			print("\nSua vez de jogar.")
		else:
			print("\nVez do seu adversario jogar.")
	
	ins, outs, exs = select.select(inputs,[],[])
				
	for mode in ins:

		# Lê da consola o que a pessoa introduziu no teclado
		if mode == sys.stdin:
			mensagem = sys.stdin.readline()
			comandos = mensagem.split()
			comprimentoMensagem = len(comandos)

			if mensagem == "\n":
				mensagemErro = "Tem que introduzir qualquer coisa no teclado."
				error(mensagemErro)
				break
			elif comandos[0] == "Registar":
				success = registarClienteSTDIN(comprimentoMensagem)
				if success == False:
					break
				else:
					registado = True
			elif comandos[0] == "Listar":
				success = listarJogadoresSTDIN(comprimentoMensagem)
				if success == False:
					break
			elif comandos[0] == "Convidar":
				success = convidarJogadorSTDIN(comprimentoMensagem, comandos)
				if success == False:
					break
			elif comandos[0] == "Jogar":
				success = jogadaValidaSTDIN(comprimentoMensagem, comandos)
				if success == False:
					break
				else:
					posicaoTabuleiro = int(comandos[1])
					success = jogar(tabuleiro, PECA_X, posicaoTabuleiro)
					if success == False:
						break
					mensagem = mensagem + rival

			cliente.sendto(mensagem.encode(), (IP_SERVIDOR, PORTO_SERVIDOR))

		# Lê da socket, mensagem que vem do servidor
		elif mode == cliente:
			(mensagem, endereco) = cliente.recvfrom(1024)
			mensagem = mensagem.decode()
			comandos = mensagem.split()

			if comandos[0] == "MensagemInformativa":
				print(mensagemInformativa(comandos))
				break
			elif comandos[0] == "Listar":
				listarJogadoresSOCKET(comandos)
				acknowledge("servidor")
				break
			elif comandos[0] == "Convidar":
				jogadorConvida = comandos[1]
				jogadorConvidado = comandos[2]
				conviteJogadorSOCKET(tabuleiro, jogadorConvida, jogadorConvidado)
				break
			elif comandos[0] == "RespostaConvite":
				jogadorConvidado = comandos[1]
				respostaConvite = comandos[2]
				respostaConviteSOCKET(jogadorConvidado, respostaConvite)
				acknowledge(jogadorConvidado)
				break
			elif comandos[0] == "Jogar":
				posicaoTabuleiro = comandos[1]
				jogar(tabuleiro, PECA_O, int(posicaoTabuleiro))
				myTurn = True
				break
			elif comandos[0] == "Sair":
				sys.exit()


############################################## STDIN ################################################

#            if comandos[0] == "MOV":
##                if length != 2:
#                    print("Invalid arguments. Try again with two arguments")
#                    break
#                #msg = msg.split()
#                move = arg[1]
#                if gameIsPlaying:
#                    if turn == 'yourTurn':#
#                    
	#                                           if makeMove(theBoard, player1Letter, move):
	#                                               flag=1
	#                                               msg = arg[0]+" "+name+" "+oponent+" "+arg[1]
													#                          if isWinner(theBoard, player1Letter):
	#                                                   #ALTERAR
	#                                                   drawBoard(theBoard)
#                                                    print('Hooray! You have won the game!')
	#                                                   gameIsPlaying = False
	#                                                   flag = 0
#                                                    msg = "END"+" "+name+" "+oponent+" "+arg[1]+" V"

	#                                               else:

	#                                                   if isBoardFull(theBoard):
	#                                                       drawBoard(theBoard)
		#                                                      print('The game is a tie!')
#                                                      msg = "END" + " " + name + " " + oponent + " " + arg[1] + " D"
		#                                                      flag = 0


		#                                                  else:
		#                                                      turn = 'notYourTurn'

	#                                           else:
	#                                               break
#                    
	#                                       else:
	#                                           print("Not your turn")
	#                                           break


############################################## SOCKET ################################################


#            if comandos[0] == "MOV":
#                acknowledge(cmds[1])
	#               move=cmds[3]
#
	#               if gameIsPlaying:
	#                   if turn == "notYourTurn":
	#                       makeMove(theBoard, player2Letter, move)
	#                       flag = 1
#
	#                       if isWinner(theBoard, player2Letter):
																												#ALTERAR
		#                          drawBoard(theBoard)
		#                          print('Uhhh!!!! What a shame. Better luck next time ;^)')
		#                          gameIsPlaying = False
		#                          flag=0
		#                          break
		#                     else:
			#                         if isBoardFull(theBoard):
			#                             drawBoard(theBoard)
				#                            print('The game is a tie!')
				#                            flag=0
				#                            break
				#                        else:
			#                             turn = 'yourTurn'
			#                             break

					#               else:
					#                   print("Not your turn")
					#                   break





				##        if comandos[0] == "END":
				#            acknowledge(cmds[1])
				#            move=cmds[3]

				#            makeMove(theBoard, player2Letter, move)

				#            if cmds[4] == "V":
					#               drawBoard(theBoard)
				#                print('Uhhh!!!! What a shame. Better luck next time ;^)')
				##                gameIsPlaying = False
				#                flag=0
				#                break

					#           else:
					#               drawBoard(theBoard)
						#              print('The game is a tie!')
					#               flag=0
					#               break







					#       print('Message received from server: "{}"'.format(comandos[0]))
