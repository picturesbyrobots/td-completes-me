import lib_tokenizer
import lib_finder
import re
import td
import traceback
import types


class TDCompletesMe :
	def __init__(self, ownerComp) :
		self.ownerComp = ownerComp
		self.OpContext = op('/')
		self._tokens = []
		self._current_token = 0
		self._completions = None
		self._msg_data = None

	#TODO this should be some sort of enum
		self._state = 'OPS'



	def ProcessorLookup(self, token_type) :
		lookup = {
			"OP_METHOD" : self.ProcessOperatorToken,
			"GLOBAL_OP" : self.ProcessGlobalToken,
			"DOT" : self.ProcessDotToken,
			"GLOBAL_OP_SEARCH" : self.ProcessGlobalOpSearch,
			"PARENT" : self.ProcessParentToken,
			"EXT_SEARCH" : self.ProcessSelfToken,
			"PAR" : self.ProcessParToken,
			"DATA_ACCESS" : self.ProcessDataToken
		}

		if token_type in lookup.keys() :
			print(token_type)
			return lookup[token_type]
		else:
			return None

	def GetGlobalOp(self, op_name = None) :
		if op_name in [operator for operator in op] :
			return op.__getattribute__(op_name)
		else:
			return None


	def GetOpFromContext(self, op_name = None, context = None) :
		if context is None : 
			context = self.OpContext

		if context.op(op_name) : 
			return context.op(op_name)
		else : 
			return None

	def ProcessParentToken(self, token_val) :
		number_match= re.search(r'\d',  token_val)
		levels_up = 1
		if number_match:
			levels_up = number_match.group(0)
		
		self.OpContext = self.OpContext.parent(levels_up)

	

	def _get_extension_from_data(self) : 
		# helper function to pull out any class modules in an incoming stream
		class_name = None
		for line in self._msg_data["lines"] :
			if "class" in line :
				#we can assume that the class name is directly after the class
				class_name = line.split(' ')[1]
			
		return class_name

	def ProcessDataToken(self, token_val) :
		print('processing {} in op context : {}'.format(token_val, self.OpContext.name))
		completions = []
		#we need to make sure at the cursor is actually in the [] operator
		match = re.search(r"\[.+\]?'|(?=(\.))", self._msg_data["lines"][self._msg_data["line_idx"]])
		if match is not None :
			char_idx = self._msg_data["char"]
			if char_idx > match.start() and char_idx < match.end() :
				# if we're dealing with an OpContext that is of type DAT
				if "DAT" in self.OpContext.OPType :
					# check and make sure we're looking for a string 
					if "['" or '["' in token_val : 
						# check for a comma character to get rows or cols 
						cells = []
						if ',' in token_val :
							# we need to deduce rows and cols. use a split to get all values between ""
							# and compare the results. The one with less digits is probably what we
							# want to complete
							# TODO. Convert this logic to return rows or cols based on calculated 
							# cursor position.

							def scrub(in_str) :
							# helper function to clean cruft from input strings
								ignored = [' ', '[', ']', "'"]
								for char in ignored :
									if char in in_str:
										in_str = in_str.replace(char, '')

								return in_str

							vals = [scrub(val) for val in token_val.split(',')]
							if len(vals[0]) > len(vals[1]) : 
								cells = self.OpContext.cols()
							else :
								cells = self.OpContext.rows()
						else :
							cells = self.OpContext.rows()


						if len(cells) :
							for cell_list in cells :
								head = cell_list[0]
								completions.append(
									{
										"label" : str(head.val),
										"kind" : 6,
										"detail" : head.owner.name,
										"documentation" :"""{} :\n \n row : {} \n col : {}""".format(
											head.owner.path, str(head.row), str(head.col)
										) 
									}
								)
							return completions
				
				# the other option is that we're dealing with a chop operator
				if "CHOP" in self.OpContext.OPType :
					channels = [channel.name for channel in self.OpContext.chans()]
					print('getting channels for {}'.format(self.OpContext.name))
					if len(channels) :
						for channel in channels :
							completions.append(
											{
												"label" : channel,
												"kind" : 6,
												"detail" : self.OpContext.name,
												"documentation" :""
											}
										)	
						return completions
						

	def ProcessParToken(self, token_val) :
		return

	def ProcessSelfToken(self, token_val) :


		# we need the full class name to get which op is being referenced by the extension code
		class_name = self._get_extension_from_data()
		if not class_name :
			return 
		
		# roll up a custom extension search function to use with lib finder
		# if I have to use it more than just in this instance I'll migrate to lib_finder proper
		def search_by_extension(op_to_check, target_name) : 

			# if we're not getting passed a COMP check the parent
			if not op_to_check.isCOMP :
				op_to_check = op_to_check.parent()

			# loop through all extension objects and check the name against the target name
			for extension in op_to_check.extensions :
				if extension is not None :
					if extension.__class__.__name__ == target_name :
						return True

			return False 

		# lib finder allows you to specify a custom search fuction. we'll supply the above function
		# to search creatively by name
		new_op_context = lib_finder.find_op(
			class_name , custom_function= search_by_extension
		)

		if new_op_context :
		# lib finder returns the matching op by searching the children. 
		# so if it's not a COMP we want the parent
			if not new_op_context.isCOMP :
				new_op_context = new_op_context.parent()
			
			# move the context to the returned op
			self.OpContext = new_op_context

			# if we're looking for the keyword ownerComp in the token value
			# use some special logic
			if "ownerComp" in token_val :
				target_extensions = [extension for extension in self.OpContext.extensions 
									if class_name == extension.__class__.__name__]

				if len(target_extensions) :
					target_extension = target_extensions[0]
					target_op = target_extension.__getattribute__("ownerComp")
					self.OpContext = target_op



			
		




	def ProcessOperatorToken(self, token_val) :
		
		# if this is the first token odds are that we need to move up a level get all the children in the context
		if self._current_token == 0 :
			if 'COMP' not in self.OpContext.OPType :
				self.OpContext = self.OpContext.parent()

		# if we're not in the last token try to get a new op context
		if self._current_token != len(self._tokens) - 1 :
		#get all values between "op(""  and ")"
			pattern = r'(?<=op\()(.*)(?=\))'
			matches = re.search(pattern, token_val)
			if matches :
			# strip any quotes from the string
				op_name = matches.group(0).replace("'", '').replace('"', '')

			# attempt to get the new operator context
				new_context = self.GetOpFromContext(op_name=op_name)
				if new_context :
					self.OpContext = new_context
			return None
	

		else :
			completions = []

			# respect DOT syntax. if there are special characters in the token val move the context
			if '/' in token_val :
				count = len(re.findall("\.", token_val))
				self.OpContext = self.OpContext.parent(count - 1)

			for operator in self.OpContext.findChildren(maxDepth = 1) :
				completions.append(
					{
						"label" : operator.name,
						"kind" : 6,
						"detail" : operator.path,
						"documentation" : operator.__doc__
					}
				)

			if len(completions) :
				return completions
			else :
				return None




	def ProcessGlobalToken(self, token_val) :
		try :
			new_context = self.GetGlobalOp(op_name=token_val.split('.')[1])

		except IndexError :
			return None

		if new_context : 
			self.OpContext = new_context

		else :
			return None


	def ProcessGlobalOpSearch(self, token) :
		"""Returns formatted completions for operators in global shortcuts."""

		completions = []
		# the list comp below will return a list of operator names.
		op_names = [operator for operator in op if not operator.startswith('TD') and not operator.startswith('OP')]
		for operator_name in op_names:
			# actual ops are store as attributes. get them so we can pull the paths
			target_op = op.__getattribute__(operator_name)
			if target_op :
				completions.append(
							{
								"label" : target_op.name,
								"kind" : 6,
								"detail" : target_op.path,
								"documentation" : target_op.__doc__
							}	)

		return completions
	def ProcessDotToken(self, token) :
		if self._current_token == len(self._tokens) - 1 :
			# we have to do different things based on the last token type
			last_token = self._tokens[self._current_token -1]

			# if the last token type was PAR return a list of parameters for the current op context
			if last_token.type == "PAR" :
				completions = []
				for param in self.OpContext.pars() :
					completions.append({
						"label" : param.name,
						"kind" : 0,
						"detail" : param.name,
						"documentation" : param.__doc__
					})
				return completions


			op_lookup_methods = ['GLOBAL_OP', 'ME', 'PARENT', 'OP_METHOD']

			if last_token.type in op_lookup_methods :

				# we want all the op functions for the current context without the dunder methods

				# this could be done with a much more elegant list comp or inspect modules. something like this list comp would do the trick
				# method_list = [funct for func in dir(self.OpContext) if callable(getattr(self.OpConect, funct)) and not funct starts with '__"]
				#
				# unfortuneatly some depreceated methods in the TD module :  "warnings()" and "errors()"
				# will raise errors and break the things. So we need to build the list long hand
				completions = [] 
				# __dir__ returns a list of strings for all attributes of the current context
				for funct in dir(self.OpContext) :
					try :
						# certain atttributes and functions will raise an error and clutter the text port. bypass them here
						bypassed_attributes = ['mod', 'module', 'recursiveChildren', 'warning', 'error']
						if funct not in bypassed_attributes :
							# construct a completion item if the attribute is a method and isn't magical
							if callable(getattr(self.OpContext, funct)) and not funct.startswith("__") :
								completions.append({
									"label" : funct,
									"kind" : 0,
									"detail" : funct,
									"documentation" : getattr(self.OpContext, funct).__doc__ 
								})
					except NameError as e:
						print(project.stack())
						print(project.pythonStack())
						print("got a name error : {}".format(funct))
						
					except Exception as e :
						print(traceback.format_exc())
						pass 


				# then get any custom modules or functions in the extensions
				custom_members = []
				if 'COMP' in self.OpContext.OPType :
					active_extensions = [extension for extension in self.OpContext.extensions if type(extension) is not None]
					for extension in active_extensions :
						# get all methods in the extension minus and dunder methods
						for m in dir(extension) :
							if not m.startswith("__") :
								try :
									# class level objects(self.ownerComp e.t.c. ) will show up in this.
									# treat them differently based on type
									obj = extension.__getattribute__(m)
									kind_lookup = {
										types.MethodType: 0,
										td.baseCOMP : 6
										}
									#default to type 6(operator type)
									try :
										kind = kind_lookup[type(obj)]
									except KeyError as e:
										kind = 6
									
									#build the completion
									custom_members.append(
										{
											"label" : m,
											"kind" : kind,
											"detail" : m,
											"documentation" : obj.__doc__ if obj.__doc__ is not None else "member {}".format(obj)
										}
									)	

								except Exception as e:
									print(traceback.format_exc())
								
				if len(custom_members) :
					completions = custom_members + completions

				return completions
			
		return None



	def ProcessToken(self, token) :
		if self._current_token != len(self._tokens) :
			process_method = self.ProcessorLookup(token.type)
			
			if process_method :
				new_completions = process_method(token.value) 
				# some operator methods will return completions even if they're not the last operator.
				# this logic will only overwrite completions
				if new_completions :
					self._completions.extend(new_completions)

					
					


	def Complete(self, msg_data) :
		search_data = lib_finder.get_search_data(msg_data["current_document"]["_uri"])
		op_context = None
		self._msg_data = msg_data
		if search_data :
			op_context = lib_finder.find_op(search_data["search_term"],
							method = search_data["search_method"])
		

		try :
			current_code = msg_data["lines"][msg_data["line_idx"]]
		except KeyError as e:
			return []

		res = self.GetCompletions(code = current_code, context_op=op_context)
		
		formatted_results = []
		if res :
			formatted_results = res

		return formatted_results


	def GetCompletions(self, code, context_op = None) :
		if context_op is not None :
			self.OpContext = context_op
		else :
			self.OpContext = op('/')

		"""get all tokens. Tokens are of type
		  Token (type = SomeType, value = code value)
		  see local/modules/lib_tokenizer for more details
		"""

		self._tokens = []
		tkns = lib_tokenizer.get_all_tokens(code)
		if tkns :
			self._tokens = tkns

		self._current_token = 0
		self._completions = []


		for token in self._tokens :
			self.ProcessToken(token)
		# increase the current token
			self._current_token =self._current_token + 1
		
		return self._completions







