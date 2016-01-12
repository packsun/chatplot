from datetime import datetime
from pylab import rcParams
import socket, string, json, urllib2, threading, time, numpy
import matplotlib.pyplot as plt
import numpy as np

def observeStream(readbuffer="", MODT=False, time=0):
	chatlog = [[], []]
	prev = startTime
	while True:
		readbuffer = readbuffer + s.recv(1024)
		temp = string.split(readbuffer, "\n")
		readbuffer = temp.pop()
		try:
			jsonOnline = getJSON()
			if not jsonOnline['stream']:
				print 'Stream has concluded.'
				return chatlog
		except:
			print 'Connection timed out.'
			continue
		for line in temp:
			parts = string.split(line, ":")
			if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
				try:
					message = parts[2][:len(parts[2]) - 1]
				except:
					message = ""
			usernamesplit = string.split(parts[1], "!")
			username = usernamesplit[0]
			if MODT:
				print username + ": " + message
				chatlog[0].append(username + ": " + message)
				now = datetime.utcnow()
				if (now - prev).total_seconds() > 300:
					s.send("PONG %s\r\n" % line[1])
					prev = now
				minutes = (now - creationTime).total_seconds()/60
				chatlog[1].append(minutes)
				if time != 0 and (now - startTime).total_seconds()/60 > time:
					print 'Reached time limit of ' + str(time) + ' minutes.'
					return chatlog
			for l in parts:
				if "End of /NAMES list" in l:
					MODT = True

def printHighlights(times, counts):
	totalMins = len(times)
	for i in range(9):
		if totalMins <= i:
			return
		else:
			maxCounts = -1
			maxIndex = -1
			for j in range(totalMins-i):
				curr = counts[j]
				if curr > maxCounts:
					maxCounts = curr
					maxIndex = j
			print str(i+1) + '. ' + parseTime(times[maxIndex]) + ' - ' \
				+ str(int(maxCounts)) + ' messages'
			counts = np.delete(counts, maxIndex)
			times = np.delete(times, maxIndex)


def parseTime(timestamp):
	if timestamp > 60:
		hours, minutes = timestamp // 60, timestamp % 60
	return timeHelper(hours) + ':' + timeHelper(minutes)

def timeHelper(x):
	if x == 0:
		return '00'
	elif x < 10:
		return '0' + str(x)
	else:
		return str(x)

def getJSON():
	return json.load(urllib2.urlopen('https://api.twitch.tv/kraken/streams/' + USER))

def validTime():
	time = raw_input("Max time in minutes: ")
	if time == "":
		return 0
	try:
		time = int(time)
		if time <= 0:
			print "Time limit must be a positive integer or empty string."
			return validTime()
		else:
			return time
	except:
		print "Time limit must be in numerical form."
		return validTime()


HOST = "irc.twitch.tv"
NICK = "chatplot"
PORT = 6667
PASS = "oauth:xtqny81s2j3sqze5rmm7bu9k0rsb7b"
USER = raw_input("Channel name: ").lower()

try:
	jsonData = getJSON()
except urllib2.HTTPError:
	print "twitch.tv/" + USER + " is not a valid channel." 
	quit()

if not jsonData['stream']:
	print USER + "'s stream is currently offline."
	quit()

MAX_TIME = validTime()

s = socket.socket()
s.connect((HOST, PORT))
s.send("PASS " + PASS + "\r\n")
s.send("NICK " + NICK + "\r\n")
s.send("JOIN #" + USER + " \r\n")

creationTime = jsonData['stream']['created_at']
creationTime = datetime.strptime(str(creationTime), "%Y-%m-%dT%H:%M:%SZ")
startTime = datetime.utcnow()
title = jsonData['stream']['channel']['status']

chats = observeStream(time=MAX_TIME)
msgs = chats[0]
timestamps = chats[1]
print 'Total messages: ' + str(len(msgs))

rcParams['figure.figsize'] = 16, 9
counts, times, patches = plt.hist(timestamps, bins=range(int(timestamps[0]), int(timestamps[-1]+2)))
printHighlights(times[:-1], counts)
plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
plt.xlim(int(timestamps[0]), int(timestamps[-1]+1))
plt.xlabel('Timestamp in minutes')
plt.ylabel('Number of chat messages')
plt.title(title + "\ntwitch.tv/" + USER + " on " + creationTime.strftime("%b %d, %Y"))
plt.show()