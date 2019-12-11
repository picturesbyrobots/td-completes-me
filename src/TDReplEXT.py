import td
import os
import json
import re

import lib_finder

class TDRepl :
	def __init__(self, ownerComp) :
		self.ownerComp = ownerComp
		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Peers' , value =[] , dependable = 'deep', readOnly =False)
		self.target_op = None

	def GetFilePath(self, file_path_string) :
		return os.path.abspath(file_path_string)

	def GetData(self,file_path) :
		"""Get some search data from about a file. Gets the path
		of a file and make some assumptions about it
		
		`Args :
			file_path (string) : a path_like object
		

		`Returns:
			{
				`search_term` : the term by which to search,
				`search_method` : search by name or source par
			}
				
		"""
		


		fp_obj = os.path.abspath(file_path)
		head,tail = os.path.split(fp_obj)
		result = None
		if 'touchtmp' in head :
			match= re.search(r'dat_(.*?)__', tail)
			op_name = match.group(1)
			if op_name :
				result = {
					"search_term" : op_name,
					"search_method" : "name"
				}
		else :
			result = {
				"search_term" : tail,
				"search_method" : "src"
			}
		return result


		return None

		
		
	def Lex(self, cmd):
		new_line = ""
		for line in cmd.splitlines(True) :
			inject = line

			if inject.startswith(('op(', 'parent()')) :
				inject = '{}.{}'.format(self.target_op.path, line)

			match_pattern = r'(?<=\().+?(?=\))'
			result = re.search(match_pattern, inject)
			if result :
				print(result.group())

			inject = inject.replace('me.' ,
			"""op("{}").""".format(self.target_op.path))

			new_line += inject

		return new_line

	def Route(self, msg_data) :
		self.RouteTable = {
			"EVAL" : self.Eval,
			"REFRESH" :self.Refresh,
			"RPL_FILE" : self.RunFile,
			"TEXT_PORT" : self.OpenTextport,
			"CLEAR_TEXTPORT" : self.ClearTextport
		}

		if msg_data["cmd"] in self.RouteTable.keys() :
		 	return self.RouteTable[msg_data["cmd"]](msg_data)

		
	def ClearTextport(self, msg_data = None) :
		td.clear()
		pass
		
	def OpenTextport(self, msg_data = None) :
		current_pane = td.ui.panes.current
		new_pane = current_pane.splitRight()
		p = new_pane.changeType(PaneType.TEXTPORT)
		p.ratio = 0.296

	def Eval(self, msg_data) :
		if self.target_op :
			cmd = self.Lex(msg_data["payload"])
			res = eval(cmd)
			self.Send(res)

	def Refresh(self, msg_data) :
		if self.target_op :
			self.target_op.par.loadonstartpulse.pulse()
		return "{} refreshed".format(self.target_op.path)

	def RunFile(self, msg_data) :
		if self.target_op :
			result = self.target_op.run(delayFrames = 1)


	def Send(self, res) :

		peer_store = self.ownerComp.op('peer_store')
		peer_list = peer_store.fetch('peer_list', {})

		return_message = {
			"type" : "RESP",
			"message" : res
		}

		for port in peer_list :
			peer_list[port].send(json.dumps(return_message).strip(), terminator = '')

	def Parse(self, peer = None, message = None) :
		#handle peer storage first

		try :
			peer_store = self.ownerComp.op('peer_store')
			peer_list = peer_store.fetch('peer_list', {})
			if peer.port not in peer_list :
				peer_list[peer.port] = peer
				peer_store.store('peer_list', peer_list)

			msg_data = json.loads(message)
			try :
				file_name = msg_data["file_name"]
			except KeyError as e :
				self.Send('no file specfied')

			op_data = self.GetData(msg_data["file_name"])

			self.target_op = lib_finder.find_op(op_data["search_term"], 
						method = op_data["search_method"])

			res = self.Route(msg_data)

			self.Send(res)
		

		
		except Exception as e:
			raise


		


