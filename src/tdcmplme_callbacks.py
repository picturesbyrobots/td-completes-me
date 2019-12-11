import json
import traceback
# me - this DAT
# 
# dat - the DAT that received the data
# rowIndex - the row number the data was placed into
# message - an ascii representation of the data
#			Unprintable characters and unicode characters will
#			not be preserved. Use the 'bytes' parameter to get
#			the raw bytes that were sent.
# bytes - a byte array of the data received
# peer - a Peer object describing the originating data
#   peer.close() 	#close the connection
#	peer.owner	#the operator to whom the peer belongs
#	peer.address	#network address associated with the peer
#	peer.port		#network port associated with the peer

def onConnect(dat, peer):
	return

def onReceive(dat, rowIndex, message, bytes, peer):
	if message.startswith('{'):
		results = []
		try :
			msg_data = json.loads(message)

			completions = me.parent().Complete(msg_data)

			if len(completions) :
				results = completions

			header = getHeader(hType = 'default', msg_bytes = json.dumps(results).encode('utf-8'))
			peer.sendBytes(header)
			peer.sendBytes(json.dumps(results).encode('utf-8'))
		except Exception as e :
			print(traceback.format_exc())

		op("closePeer").run(peer, delayFrames = 1)
		#peer.send('OK', terminator = '\r\n')
		return

def onClose(dat, peer):
	return

def getHeader(hType=None, recHeader=None, msg_bytes= None):
	if hType == 'default':
		header = "HTTP/1.1 200 OK\n\r Content-Type: text/json; charset=UTF-8\n\rContent-Length: {}\n\r\n\r".format(len(msg_bytes)).encode('utf-8')
	return header
	