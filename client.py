# import requirements
import socket
import threading
import random
import sys
import tqdm
import os
import json
import time



HOST = '127.0.0.1'
PORT = 32664

hostname=socket.gethostname()     
ip = socket.gethostbyname(hostname) 


pport = random.randint(1000, 2000)

MAXCON = 10
conn = []	# list of all currently active friends
#inside have username, client /host, port, connected_flag/ in this order

HEADER = 2048

#creating sokcet obj
BUFFER_SIZE = 4096
SEPARATOR = "<>"
FILE_SIZE = 5242880 # send 4096 bytes each time step




def exist(user):
	for con in conn:
		if con[0] == user:
			return True
	return False


def listen_for_mess_server(client):
	#print("this is a thread of listen for mess server")
	while True:

		#mess = client.recv(2048).decode('utf-8')
		content = client.recv(BUFFER_SIZE).decode()

		
		#print(f"client {client}")
		
		#print("content: ", content)
		
		if content != "":
			#username = mess.split(":\n")[0]
			#content = mess.split(":")[1]


			if content == "0":
				print("username has already been used")

				login(client)

				continue

			elif content == "-32664":
				print("wrong Username or Password")

				login(client)

				continue


			elif content.split(" ")[0] == "1":
				print("login confirmed")
				name = content.split(" ")[1]
				return name


			elif content == "-999":
				print("this person is not in your friendlist")
				exit(1)
			

			elif content == "-1":
				print("user is not currently active")
				exit(1)

			elif content.split(":")[0] == "<friendlist>":
				file_info = content.split(":")[1]
				get_file(client, file_info)

				with open("user_f.json", "r") as f:
					data = json.load(f)

					print("friend list:")

					for fr in data["friends"]:
						print(fr)

					f.close()


			#print(f"[{username}] {content}")
			#content != "-999" or content != "-1" or content != "0" or content != "1":
			else:
				username = content.split(" ")[0]
				host = content.split(" ")[1]
				port = int(content.split(" ")[2])
				#print(username, host, port)
				if not exist(username):
					c = conn_to(host, port)
					conn.append((username, c))
			

			

				#return

			#print("active user:")

			#for user in conn:
			#	print(f"{user[0]}")
			#print("#")

		else:
			#print("user is not currently active")
			pass



def send_mess_to_server(client, mess):
	#while True:

		#mess = input("to: ")
		if mess != '':
			client.sendall(mess.encode())

		else:
			#print("Empty mess!")
			#exit(0)
			pass



def listen_for_mess(client, username):
	
	while True:
		msg = ""
		try:
			msg = client.recv(BUFFER_SIZE).decode()
		except:
			for fr in conn:
				if fr[1] == client:
					print(f"friend {fr[0]} has disconnected")
					conn.remove(fr)
				return


		#print(f"preprocessed msg: {msg}")

		if msg != '':
			if msg.split(":")[0] != "sys" and msg.split(":")[0] != "sys_send":
			
			#msg = username + ":\n" + mess +"\n\n"
			#send_mess_to_all(msg)
				print(f"{username}: {msg}")

				continue


			if msg.split(":")[0] == "sys_send":
				print("incoming file...")
				file_inf = msg.split(":")[1]
				#print("file_info: ", file_inf)
				get_file(client, file_inf)

				continue

		else:
			pass




def server_handler(client, friend):
	#print("this is server server_handler")
	#get hand shake


	#while True:
		try:
			msg = friend.recv(BUFFER_SIZE).decode()
		
		except:
			for fr in conn:
				if fr[1] == friend:
					print(f"friend {fr[0]} has disconnected")
					conn.remove(fr)
				return
		#print(f"first msg: {msg}")
		if msg != "":
			username = msg.split(":")[1]
			#lport = int(msg.split(" ")[1])
			#print("msg: ", msg)
			if not exist(username):
				#print("username not in active, find in server")
				threading.Thread(target=listen_for_mess_server,
		args=(client, )).start()
				send_mess_to_server(client, username)
				time.sleep(0.1)



			#rep = "connected"

			#friend.sendall(rep.encode('utf-8'))
###
	#conn_to_p(client, user)
	#threading.Thread(target=listen_for_mess,
	#	args=(friend, username, )).start()
		if exist(username):
			listen_for_mess(friend, username)



	

def sendfile(friend, filename):
	filesize = os.path.getsize(filename)

	friend.send(f"sys_send:{filename}{SEPARATOR}{filesize}".encode())


	#print("filename: ", filename)
	#print("filedsize: ", filesize)

	print("sending...")

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



def get_file(friend, file_info):

	filename, filesize = file_info.split(SEPARATOR)
	# remove absolute path if there is
	filename = os.path.basename(filename)
	# convert to integer
	filesize = int(filesize)

	#print("filename: ", filename)
	#print("filesize: ", filesize)

	# start receiving the file from the socket
	# and writing to the file stream
	print("receiving file...")

	with open(filename, "wb") as f:
		while filesize != 0:
			# read 1024 bytes from the socket (receive)
			bytes_read = friend.recv(BUFFER_SIZE)
			
			#if not bytes_read:
				# nothing is received
				# file transmitting is done
			#	f.close()
			#	print("file received")
			#	break
			# write to the file the bytes we just received
			f.write(bytes_read)

			filesize -= int(len(bytes_read))


		f.close()
		print("file received")
			






def conn_to_p(client, user):

	while True:
		#spk = spk.dup()

		usr = ""
		usr = input("to: ")
		#try:

		if usr == "":
			continue
			#return

		else:

			if usr == "sys_friend:>":
				mess = f"sys_friend:{user}"
				threading.Thread(target=listen_for_mess_server, 
					args=(client, )).start()
				send_mess_to_server(client, mess)


			else:

				if not exist(usr):
					#print("conn_to_p: friend not in active, find in server...")
					threading.Thread(target=listen_for_mess_server,
				args=(client, )).start()
					send_mess_to_server(client, usr)
					time.sleep(0.1)

				#print("friendlist:")
				#for f in conn:
				#	print(f"username {f[0]}\n{f[1]}")


				for con in conn:
					if con[0] == usr:
						#host = con[1]
						#port = con[2]
						#print(f"username: {con[0]}, host: {con[1]}, port: {con[2]}, port type: {type(con[2])}")

						#conn_to(spk, host, port)
						#print("handshaking...")
						info = f"sys:{user}" # {pport}
						#print("info: ", info)
						#spk.sendall(info.encode('utf-8'))
						try:
							con[1].sendall(info.encode())
						except:
							for fr in conn:
								if fr[1] == con[1]:
									print(f"friend {fr[0]} has disconnected")
									conn.remove(fr)
							continue
								#return

						#continue


						#print(user)
						#print("before typing msg...")
						msg = input("> ")
						if msg != "":

							if msg == "sys_send:>":
								filename = input("filename: ")
								sendfile(con[1], filename)
								#msg = ""
								break


							else:
								con[1].sendall(msg.encode())
								break

			




def conn_to(host, port):
	client = socket.socket(socket.AF_INET, 
		socket.SOCK_STREAM)
	try:
		client.connect((host, port))
		#print(f"connected to {host}, {port}")
	except:
		
		print(f"unanble to connect to {host}, port {port}")

	return client




def server(client, srv):

	while True:

		friend, address = srv.accept()

		#print(f"friend conn at: {friend} {address[0]} {address[1]}")
		
		#get_handshake(client, friend)

		threading.Thread(target=server_handler,
		args=(client, friend, )).start()




def login(client):
	USERNAME = input("Username: ")
	PASSWORD = input("Password: ")
	info_mess = f"{USERNAME} {PASSWORD} {pport}"
	if USERNAME != '':
		client.sendall(info_mess.encode())
	else:
		print("Username cannot be empty!")
		exit(0)

	return USERNAME





def main():
	
	conn.clear()


	srv = socket.socket(socket.AF_INET,
		socket.SOCK_STREAM)

	#connect to server
	client = conn_to(HOST, PORT)


	# listen for conn
	try:
		srv.bind((HOST, pport))
		#print(f"listening on port {pport}")
	except:
		print(f"Unable to bind to port {pport}")
	srv.listen(MAXCON)
	
	

	USERNAME = login(client)

	#USERNAME = input("Username: ")
	#info_mess = f"{USERNAME} {pport}"
	#if USERNAME != '':
	#	client.sendall(info_mess.encode('utf-8'))
	#else:
	#	print("Username cannot be empty!")
	#	exit(0)


	USERNAME = listen_for_mess_server(client)


###
	threading.Thread(target=server,
		args=(client, srv, )).start()

	#threading.Thread(target=conn_to_p,
	#		args=(client, USERNAME, )).start()


	conn_to_p(client, USERNAME)
###


if __name__ == '__main__':
	main()