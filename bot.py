import socket
import json
import asyncio
import discordpy
from time import sleep
import os
import sys

global config
global client
global clientTask
client = discordpy.Client()

def setup():
	global config
	defaultConfig = 'BotCode=\nTargetChannel=wekan\nport=80\nShowSourceServer=False'
	try:
		configFile = open('bot config.cfg', 'r')
	except FileNotFoundError:
		print('Creating config file, please input the relevant parameters')
		configFile = open('bot config.cfg', 'w')
		configFile.write(defaultConfig)
		configFile.close()
		sleep(3)
		return False
	config = {}
	for item in configFile.readlines():
		item = item.split('=')
		if item[1].endswith('\n'):
			item[1] = item[1][:-1]
		if item[1] == '':
			del item[1]
		if len(item)<2:
			print("Missing config parameter")
			sleep(2)
			return False
		config[item[0]] = item[1]
	configFile.close()
	return True
	
async def recieveHook():
	await client.wait_until_ready()
	global config
	channels = list(client.get_all_channels())
	for item in channels:
		if item.name==config["TargetChannel"]:
			channel = item
	config["TargetChannel"] = channel
	s = socket.socket()
	s.bind(('',int(config["port"])))
	print('Socket initialized, port '+config["port"]+'          ')
	while not client.is_closed:
		try:
			s.listen()
			s.settimeout(5)
			c, addr = s.accept()
			incoming = c.recv(4096).decode()
			incoming = incoming.split('\r\n')
			if len(incoming)>1:
				try:
					message = json.loads(incoming[-1])
					outgoing = message["text"]
					if config["ShowSourceServer"]!='True':
						outgoing = outgoing.split('\n')
						outgoing = outgoing[0]
					print(outgoing)
					await client.send_message(config["TargetChannel"],outgoing)
				except json.JSONDecodeError:
					pass
			c.close()
		except socket.timeout:
			await client.send_typing(config["TargetChannel"])
			pass
		except:
			raise

@client.event
async def on_ready():
	print('Bot online')

def main():
	global clientTask
	print('')
	print('Wekan->Discord')
	print('--------------')
	print('Running Setup', end='\r', flush=True)
	success = setup()
	if success:
		print('Setup was successful')
		print('Establishing connection to discord', end='\r', flush=True)
		client.loop.create_task(recieveHook())
		client.run(config['BotCode'])
		os.execl(sys.executable, sys.executable, * sys.argv)

if __name__ == "__main__":
		main()