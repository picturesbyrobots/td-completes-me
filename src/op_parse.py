
import re

def parse(expr_string = None, position = None) :
	print('parsing')
	#get all characters before the position
	previous_chars = expr_string[:position]

	# get the strings between any op() calls
	match_pattern = r'(?<=op\()(.*)(?=\))'
	result = re.search(match_pattern, previous_chars)
	if '/' in result :
		print(result)
	else :
		print('no change directives in op string')

	

	
	
	
	tokens = previous_chars.split('.')

