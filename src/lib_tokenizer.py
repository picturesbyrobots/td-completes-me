"""Copyright 2019 David Tennent

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import traceback 
import re
import collections

Token = collections.namedtuple('Token', ['type','value','line','column'])

def tokenize(code) :
        token_spec = [
                ("OP_METHOD", r'op\(.+?(\))'),
                ("PARENT", r'parent\(.(\)|$|)'),
                ("ME", r'me\.'),
                ("GLOBAL_OP_SEARCH", r"op\.$"),
                ("DOT", r'\.(?![^(]*\))'),
                ("DATA_ACCESS", r"\[.+\]?'|(?=(\.))"),
                ("GLOBAL_OP", r'op\..+?(?=(\..+)|\.)'),
                ("EXT_SEARCH", r'(?![\t])+self\..+?(?=(\..+)|\.)'),
                ("PAR", r'(?!(\.))par.?(?=(\.))')

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


	


