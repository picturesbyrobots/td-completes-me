import traceback 
import re
import collections

Token = collections.namedtuple('Token', ['type','value','line','column'])

def tokenize(code) :
        token_spec = [
                ("OP_METHOD", r'op\(.+?(\))'),
                ("PARENT", r'parent\(.(\)|$|)'),
                ("ME", r'me\.'),
                ("DOT", r'\.(?![^(]*\))'),
                ("DATA_ACCESS", r'\[.+(\]|$)' ),
                ("GLOBAL_OP", r'op\..+?(?=(\..+)|\.)'),
                ("GLOBAL_OP_SEARCH", r'^op\.$'),
                ("EXT_SEARCH", r'(?![\t])+self\..+?(?=(\..+)|\.)')

        ]

        tok_reg = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
        line_num = 1
        line_start = 0
        for mo in re.finditer(tok_reg, code): 
                kind = mo.lastgroup
                value = mo.group()
                col = mo.start() - line_start
                yield Token(kind, value, line_num, col)


def get_all_tokens(code) :

	try :
		tokens = [token for token in tokenize(code)] 
		if len(tokens) :
			return tokens
		else :
			return None

	except Exception as e:
		print('TOKENIZER: Encountered an exception {}'.format(
			traceback.format_exc()
		))


	


