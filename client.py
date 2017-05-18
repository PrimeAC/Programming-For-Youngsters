# -*- coding: utf-8 -*-

import socket
import sys
import select


##########################################################################################################
# INICIALIZACAO

PORTO_SERVIDOR = 5005
IP_SERVIDOR = '127.0.0.1'
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
	if comprimentoMensagem != 3:
		mensagemErro = "Argumentos invalidos. Convide novamente o jogador."
		error(mensagemErro)
		return False
	
	tamanhoTabuleiro = int(comandos[2])
	if tamanhoTabuleiro < 3:
		mensagemErro = "Tabuleiro demasiado pequeno."
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

def jogadaValidaSTDIN(comprimentoMensagem, comandos, tamanhoTabuleiro):
	# Erro caso o comprimento da mensagem seja diferente de 2
	if comprimentoMensagem != 3:
		mensagemErro = "Argumentos invalidos. Insira novamente o quadrado em que quer jogar." 
		error(mensagemErro)
		return False
	linhaTabuleiro = comandos[1]
	if posicaoTabuleiro(linhaTabuleiro, tamanhoTabuleiro) == False:
		return False
	colunaTabuleiro = comandos[2]
	if posicaoTabuleiro(colunaTabuleiro, tamanhoTabuleiro) == False:
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

def posicaoTabuleiro(posicao, tamanhoTabuleiro):
	# Erro caso o segundo argumento introduzido não seja um número
	try:
		posicao = int(posicao)
	except ValueError:
		print("Tem que introduzir um número inteiro, dentro do limite do tabuleiro.")
		return False
	# Erro caso o número do quadrado introduzido não esteja dentro dos limites do tabuleiro
	if posicao <= 0 or posicao > tamanhoTabuleiro:
		mensagemErro = "Jogou fora dos limites do tabuleiro."
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

def conviteJogadorSOCKET(jogadorConvida, jogadorConvidado, tamanho):
	global myTurn, aJogar, rival, tamanhoTabuleiro						# Variáveis globais a serem alteradas
	print("Recebeu um convite de " + jogadorConvida + " para jogar num tabuleiro " + tamanho + "x" + tamanho + ". Para aceitar o jogo digite [S], para recusar [N].")
	# Resposta introduzida pelo jogador convidado
	respostaConvite = sys.stdin.readline().replace("\n", "")
	# Se a reposta for válida, "S" ou "N", uma mensagem vai ser enviada ao servidor
	if respostaConvite == "S":
		rival = jogadorConvida 											# Jogador rival é quem fez o convite
		tamanhoTabuleiro = int(tamanho)
		tabuleiro = criaTabuleiro(tamanhoTabuleiro)
		desenharTabuleiro(tabuleiro, tamanhoTabuleiro)            		# Desenhar o tabuleiro inicial
		mensagem = "RespostaConvite " + jogadorConvidado + " " + jogadorConvida + " aceitou " + tamanho 
		aJogar = True 													# Flag que indica que o jogo está a decorrer
	# Se a resposta do jogador convidado for "N"
	elif respostaConvite == "N":
		mensagem = "RespostaConvite " + jogadorConvidado + " " + jogadorConvida + " recusou " + tamanho
	else:
		mensagemErro = "Introduziu incorrectamente a resposta."
		error(mensagemErro)
		conviteJogadorSOCKET(jogadorConvida, jogadorConvidado, tamanho)
		return
	cliente.sendto(mensagem.encode(), (IP_SERVIDOR, PORTO_SERVIDOR))
	return

def respostaConviteSOCKET(jogadorConvidado, respostaConvite, tamanhoTabuleiro):
	global myTurn, aJogar, rival, tabuleiro								# Variáveis globais a serem alteradas
	print("O jogador " + jogadorConvidado + " " + respostaConvite + " o seu convite.")
	# Se a resposta do jogador convidado for "S", ou o convite foi aceite
	if respostaConvite == "aceitou":
		rival = jogadorConvidado 										# Jogador rival é quem fez o convite
		myTurn = True 													# Flag que indica a vez de jogar
		aJogar = True 													# Flag que indica que o jogo está a decorrer
		tamanhoTabuleiro = int(tamanhoTabuleiro)
		tabuleiro = criaTabuleiro(tamanhoTabuleiro)
		desenharTabuleiro(tabuleiro, tamanhoTabuleiro)                	# Desenhar o tabuleiro inicial
	return

def criaTabuleiro(tamanhoTabuleiro):
	global tabuleiro
	tabuleiro = [[0 for x in range(tamanhoTabuleiro)] for y in range(tamanhoTabuleiro)] 
	for i in range(0, tamanhoTabuleiro):
		for j in range(0, tamanhoTabuleiro):
			tabuleiro[i][j] = " "
	return tabuleiro

def desenharTabuleiro(tabuleiro, tamanho):
	tabuleiroDesenho = "\n "
	tamanhoTabuleiro = int(tamanho)
	# Vai percorrer todos os número de quadrados existentes no tabuleiro
	for linha in range(0, tamanhoTabuleiro):
		for coluna in range(0, tamanhoTabuleiro):
		# Verifica se não é o último quadrado da linha
			if coluna != tamanhoTabuleiro - 1:
				# Vai formando uma linha do tabuleiro
				tabuleiroDesenho = tabuleiroDesenho + tabuleiro[linha][coluna] + ' | '
			# É o último quadrado da linha
			else:
				# Acrescenta o último quadrado à linha e imprime-o
				tabuleiroDesenho = tabuleiroDesenho + tabuleiro[linha][coluna]
				print(" " + tabuleiroDesenho)
				# Se não for o último quadrado da última linha imprime um separador de linhas
				if (linha + 1) * (coluna + 1) - 1 != (tamanhoTabuleiro * tamanhoTabuleiro) - 1:
					tracos = ''
					for i in range(0, tamanhoTabuleiro - 1):
						tracos = tracos + '---|'
					print(tracos + '---')
					# Prepara uma nova linha
					tabuleiroDesenho = ""
	return

def jogar(tabuleiro, peca, linhaTabuleiro, colunaTabuleiro, tamanhoTabuleiro):
	global myTurn														# Variável global a ser alterada
	linhaTabuleiro = linhaTabuleiro - 1
	colunaTabuleiro = colunaTabuleiro - 1
	# Verificar se posição está vazia
	if tabuleiro[linhaTabuleiro][colunaTabuleiro] == " ":
		tabuleiro[linhaTabuleiro][colunaTabuleiro] = peca
		desenharTabuleiro(tabuleiro, tamanhoTabuleiro)
		myTurn = False													# Passa a vez ao adversário
	# A posição está ocupada
	else:
		if myTurn == True:
			mensagemErro = "O local onde jogou ja contem uma peca. Jogue noutro sitio"
			error(mensagemErro)
			return False
	return










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
registado = False														# Variável que indica se está registado ou não
myTurn = False 															# Flag que indica a vez de jogar
aJogar = False															# Variável que indica se se está a jogar ou não
rival = ""																# Jogador adversário
tamanhoTabuleiro = 0													# Tamanho do tabuleiro

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
				success = jogadaValidaSTDIN(comprimentoMensagem, comandos, tamanhoTabuleiro)
				if success == False:
					break
				else:
					linhaTabuleiro = int(comandos[1])
					colunaTabuleiro = int(comandos[2])
					success = jogar(tabuleiro, PECA_X, linhaTabuleiro, colunaTabuleiro, tamanhoTabuleiro)
					if success == False:
						break
					mensagem = mensagem + rival
			elif comandos[0] == "Sair":
				mensagem = "Sair " + rival

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
				tamanhoTabuleiro = comandos[3]
				conviteJogadorSOCKET(jogadorConvida, jogadorConvidado, tamanhoTabuleiro)
				break
			elif comandos[0] == "RespostaConvite":
				jogadorConvidado = comandos[1]
				respostaConvite = comandos[2]
				tamanhoTabuleiro = comandos[3]
				respostaConviteSOCKET(jogadorConvidado, respostaConvite, tamanhoTabuleiro)
				acknowledge(jogadorConvidado)
				break
			elif comandos[0] == "Jogar":
				linhaTabuleiro = int(comandos[1])
				colunaTabuleiro = int(comandos[2])
				jogar(tabuleiro, PECA_O, linhaTabuleiro, colunaTabuleiro, tamanhoTabuleiro)
				myTurn = True
				break
			elif comandos[0] == "SairRival":
				myTurn = False
				aJogar = False
				rival = ""
				print("Parabens, ganhou este jogo devido a desistencia do seu adversario!")
				break
			elif comandos[0] == "Sair":
				sys.exit()


############################################## STDIN ################################################


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
