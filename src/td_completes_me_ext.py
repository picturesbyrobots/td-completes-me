import lib_tokenizer
import lib_finder
import re
import td


class TDCompletesMe :
	def __init__(self, ownerComp) :
		self.ownerComp = ownerComp
		self.OpContext = op('/')
		self._tokens = []
		self._current_token = 0
		self._completions = None

	#TODO this should be some sort of enum
		self._states = [
			'GET_METHODS',
			'GET_PARS',
			'GET_OPS'
		]

		self._state = 'GET_OPS'


	def ProcessorLookup(self, token_type) :
		lookup = {
			"OP_METHOD" : self.ProcessOperatorToken,
			"GLOBAL_OP" : self.ProcessGlobalToken,
			"DOT" : self.ProcessDotToken,
			"GLOBAL_OP_SEARCH" : self.ProcessGlobalOpSearch,
			"PARENT" : self.ProcessParentToken
		}

		if token_type in lookup.keys() :
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

	

	def ProcessOperatorToken(self, token_val) :
		
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
		#otherwise get a list of all the operators in the current context
		else :
			child_names = [child.name for child in self.OpContext.findChildren(maxDepth = 1)]
			if len(child_names) :
				return child_names
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
		return [operator for operator in op if not operator.startswith('TD') and not operator.startswith('OP')]
	def ProcessDotToken(self, token) :
		if self._current_token == len(self._tokens) - 1 :
			# we have to do different things based on the last token type
			last_token = self._tokens[self._current_token -1]
			
			
			# we want all the op functions for the current context without the dunder methods

			# this could be done with a much more elegant list comp or inspect modules. something like this list comp would do the trick
			# method_list = [funct for func in dir(self.OpContext) if callable(getattr(self.OpConect, funct)) and not funct starts with '__"]
			#
			# unfortuneatly some depreceated methods in the TD module :  "warnings()" and "errors()"
			# will raise errors and break the things. So we need to build the list long hand

			op_lookup_methods = ['GLOBAL_OP', 'ME', 'PARENT', 'OP_METHOD']
			if last_token.type in op_lookup_methods :
				
				# firts get all the regular op methods
				method_list = [] 
				for funct in dir(self.OpContext) :
					try :
						# the mod functions attempt to compile the operator and result in many network errors. skip them.
						if 'mod' not in funct :
							if callable(getattr(self.OpContext, funct)) and not funct.startswith("__") :
								method_list.append(funct)
						
						


					except NameError as e:
						print(project.stack())
						print(project.pythonStack())
						print("got a name error : {}".format(funct))
					except Exception as e :
							pass 

				# then get any custom modules or functions in the extensions
				custom_members = []
				active_extensions = [extension for extension in self.OpContext.extensions if type(extension) is not None]
				for extension in active_extensions :
					for m in dir(extension) :
						if not m.startswith("__") :
							custom_members.append(m)

				if len(custom_members) :
					method_list = custom_members + method_list



				return method_list

			# the last token type was a Global operator get a list of all global operators and return in

			
		return None



	def ProcessToken(self, token) :
		if self._current_token != len(self._tokens) :
			process_method = self.ProcessorLookup(token.type)
			
			if process_method :
				self._completions = process_method(token.value)


	def Complete(self, msg_data) :
		search_data = lib_finder.get_search_data(msg_data["current_document"]["_uri"])
		op_context = None
		if search_data :
			op_context = lib_finder.find_op(search_data["search_term"],
							method = search_data["search_method"])
		
		current_code = msg_data["lines"][0]
		res = self.GetCompletions(code = current_code, context_op=op_context)
		formatted_results = []
		if res :
			for result in res :
				
				formatted_results.append({
					"label" : result,
					"kind" : "name"
				})


			

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
		self._completions = None

		for token in self._tokens :
			self.ProcessToken(token)
		# increase the current token
			self._current_token =self._current_token + 1
		
		return self._completions







