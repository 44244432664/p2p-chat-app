#import required modules
import socket
import threading
import sys
import time
import tqdm
import os
import json


HOST = '127.0.0.1'
#can use any port between 0-65535
PORT = 32664
#maximum num of client can connect to server
LISTENER_LIM = 10
active = []	# list of all currently active user
#inside have username, host, port in this order

HEADER = 2048

BUFFER_SIZE = 4096
SEPARATOR = "<>"

#listen for coming mess from cli
def listen_for_mess(client, username):
	
	while True:

		try:
			requsr = client.recv(BUFFER_SIZE).decode()



			if requsr != '':
				
				#msg = username + ":\n" + mess +"\n\n"
				#send_mess_to_all(msg)
				print("got msg: ", requsr)


				if requsr.split(":")[0] == "sys_friend":

					username = requsr.split(":")[1]


					with open("data.json", "r") as f:
						data = json.load(f)

						for user in data:
							if user["username"] == username:

								print("username: ", user["username"])

								print("send_file")

								with open("user_f.json", "w") as s:
									json.dump(user, s)
									print("write")
									s.close()

								file = "user_f.json"
								sendfile(client, file)
								break

						f.close()
					print("closed file")

				else:

					with open("data.json", "r") as f:
						data = json.load(f)

						is_fr = False

						for user in data:
							if user["username"] == username:
								
								for fr in user["friends"]:
									if requsr == fr:
										is_fr = True
										break

								break
						if not is_fr:
							msg = "-999"
							client.sendall(msg.encode())

						else:
							send_user(client, requsr)

			else:
				pass
				#empty mess
		except:
			for cli in active:
				if cli[1] == client:
					print(f"client {fr[0]} has disconnected")
					conn.remove(fr)
				return

'''
#send mess to a cli
def send_to(client, mess):
	client.sendall(mess.encode('utf-8'))


# func to sent mess to all client
#currently connected to server
def send_mess_to_all(mess):
	for user in active:
		send_to(user[1], mess) #user[1] = client
'''

def sendfile(friend, filename):
	filesize = os.path.getsize(filename)

	friend.send(f"<friendlist>:{filename}{SEPARATOR}{filesize}".encode())


	#print("filename: ", filename)
	#print("filedsize: ", filesize)

	print(f"sending {filename}...")

	with open(filename, "rb") as f:
		while True:
			# read the bytes from the file
			bytes_read = f.read(BUFFER_SIZE)
			if not bytes_read:
				# file transmitting is done
				print("sent")
				f.close()
				break

			# we use sendall to assure transimission in 
			# busy networks
			friend.sendall(bytes_read)


def send_user(client, usrname):
	online = False
	for user in active:
		if user[0] == usrname:
			mess = f"{user[0]} {user[1]} {user[2]}"
			online = True
			break
	if not online:
		mess = "-1"

	print("mess to usr:", mess)
	try:
		client.sendall(mess.encode())
	except:
		for fr in conn:
			if fr[1] == client:
				print(f"friend {fr[0]} has disconnected")
				conn.remove(fr)
				return

# func to handle client
def client_handler(client, addr):
	
	#server listen for cli mess
	#contain username

	while True:
		try:

			info_msg = client.recv(BUFFER_SIZE).decode()

		
			username = info_msg.split(" ")[0]
			password = info_msg.split(" ")[1]
			port = info_msg.split(" ")[2]
			if username != '':
				###

				if not check_login(username, password):
					mess = "-32664"
					client.sendall(mess.encode())
					continue

				else:

					appd = True
					for user in active:
						print("\n", user)
						print("user: ", user[0])
						print("host: ", user[1], "port: ", user[2])

						if user[0] == username:
							appd = False
							#user[1] = addr[0]
							#user[2] = port
							break
					if appd:
						active.append((username, addr[0], port))
						mess = "1 " + username
						client.sendall(mess.encode())
					###
					else:
						mess = "0"
						client.sendall(mess.encode())

						continue

					break
			else:
				#print("empty username")
				pass
		except:
			for fr in active:
				if fr[1] == client:
					print(f"friend {fr[0]} has disconnected")
					conn.remove(fr)
				return

	#threading.Thread(target=listen_for_mess,
	#	args=(client, username, )).start()

	listen_for_mess(client, username)
	

def check_login(username, password):
	with open("user.json", "r") as user:
		data = json.load(user)


		exist = False
		for u in data:
			if u["username"] == username and u["password"] == password:
				print("login success!!!")
				exist = True
				break


		if not exist:
			print("login failed :<")

		return exist


#main
def main():
	active.clear()
	#creating socket class obj:
	server = socket.socket(socket.AF_INET,
		socket.SOCK_STREAM)
	#not work -> change to DGRAM
	#AF_INET: stating of using IPv4 addresses
	#SOCK_STREAM: using TCP packets for comm.
	#for UDP, use SOCK_DGRAM


	#bind server to a hosting port
		#creating try-catch block
	try:
		#provide server with address in the form host IP
		# & port
		server.bind((HOST, PORT))
		print(f"connected to host {HOST}, {PORT}")
	except:
		print(f"Unable to bind to host {HOST} and port {PORT}")
	#set server limit
	server.listen(LISTENER_LIM)


	#while loop to listen to client connections
	while True:

		client, address = server.accept()
		# accept func waits for new connection, return
		# a new socket represent connection $ client address
		# client: socket of client
		# address: address of client
		print(f"new user at host {address[0]}\
port {address[1]} joined the chat")


		threading.Thread(target=client_handler,
			args=(client, address, )).start()




if __name__ == '__main__':
	main()