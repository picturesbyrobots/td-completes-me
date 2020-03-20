"""A module for finding operators in Touch Designer
	"""



import td
import os.path as path




def get_search_data(file_path) :
	fp_obj = path.abspath(file_path)
	head,tail = path.split(fp_obj)
	result = None

	# if we're in touch designers temp directory find the dat
	if 'touchtmp' in head :
		result = {
			"search_term" : tail,
			"search_method" : "editing_file"
		}
	else :
		result = {
			"search_term" : tail,
			"search_method" : "src"
		}

	return result


def compare_src(op_to_check, target_name, evalParams = True) :
	"""this function accepts an operator of typeDAT and a file name and attempts to identify if the file
	specified by the file parameter in the DAT refers to the same file
	
	Args:
		op_to_check(an operator) : this is an operator. ideally a file dat
		target_name : the name of the file
		TODO evalParams : if set to true this function will fetch values via the eval menthod. Potentially
		causing side effects


	Returns :
		True if the DAT's file parameter references the file name
		False otherwise
	
	"""

	# if file is not a valid parameter return false
	if 'file' not in [par.name for par in op_to_check.pars()] :
		return False

	try :
		# get the parameter via eval. adding support for expressions.
		par_val = op_to_check.par.file.eval()
		
		# if we have an empty string return
		if par_val == '' :
			return False

		#get the path to the file and check if it exists
		path_to_file = path.abspath(par_val)
		if path.isfile(path_to_file) :

			#split the path and (finally) run the compare
			head,tail = path.split(path_to_file)
			if tail == target_name :
				return True

			else :
				return False

	except AttributeError as e:
		return False

	except :
		raise

def compare_file(op_to_check, file_name) :
	"""Thanks to Ben Voight we can now check against the editing file."""

	#not sure which operators have the member functions
	#return if can't find it
	if 'editingFile' not in dir(op_to_check)  :
		return False 

	if op_to_check.editingFile is None :
		return False 

	def split_tail(fp) :
		#remove any mac or pc path weirdness
		path_to_file = path.abspath(fp)
		if path.isfile(path_to_file) :
			_,tail = path.split(path_to_file)
			return tail
	print("comparing : {} to {} :".format(split_tail(op_to_check.editingFile),file_name))

	if split_tail(op_to_check.editingFile) == file_name :
		print('found op')
		return True
	else : 
		return False


def get_current_network() :
	current_network = td.ui.panes.current.owner
	return current_network
	

def find_op(search_term, depth = 2, method = 'name', custom_function = None) :
	"""find an operator based on a search term and a method.
	
	this function will attempt to find and return an operator specified by the search term and 
	method. It will search for any operator in the following order: 

			In the comp provided by by the search_first parameter
			Recursively in the current network open in the editor
			Recusively in all networks open in the editor
			Recursively in starting from the root of the project to a maxDepth of Depth

	Args :
		search_term(string) : The term to search for
		depth(integer) : how recursive should the find children calls go
		method(string) : "name" to search by name "src" to search by source_file "custom" use a custom search function
		custom_function(func) : reference to a function object to use a key function

			This function should take two positional arguments :
			op_to_check(TD opClass) an operator
			target_name(string) a string

			and should return True or False

	Return :
		op_found. Returns a reference to the operator if found, None otherwise


	Raises :
		(TODO)AttributeError : If method is specefied as "cust" and no custom_function is supplied
			
	"""


	if custom_function is not None :
		search_function = custom_function

	else :
		try :
			search_function = {
				"editing_file" : compare_file,
				"src" : compare_src }[method]
		except KeyError as e:
			return None

	# be lazy. it's probably in the open network
	current_network = get_current_network()
	if search_function(current_network.currentChild, search_term) :
		return current_network.currentChild

	# if we can't find it in the current network then odds are its in one of the open network editors
	open_networks = [pane.owner for pane in td.ui.panes if pane.type == PaneType.NETWORKEDITOR]
	for network in open_networks :
		op_in_children = network.findChildren(maxDepth =depth,type = DAT, 
											key = lambda x : search_function(x,search_term))
		if len(op_in_children) :
			return op_in_children[0]
	

	# if we can't find it in the open editors search the project from the top down
	op_in_root = op("/").findChildren(maxDepth = 10, type = DAT, key = lambda x : search_function(x, search_term))

	if len(op_in_root) :
		return op_in_root[0]

	return None





