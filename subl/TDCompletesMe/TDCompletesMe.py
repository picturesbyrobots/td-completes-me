import sublime_plugin
import json
import socket
import traceback








class TDCompletesMe(sublime_plugin.EventListener):

    def __init__(self) :
        self.current_completions = []
        self.socket = None
        self.HOST = '127.0.0.1'
        self.PORT = 1338
        self.connected = False







    def _get_completions(self, _data, view) :
            if(not self.connected) :
                try :
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.settimeout(5)
                    self.socket.connect((self.HOST,self.PORT))
                    self.connected = True

                except Exception as e:
                    print('TD Completes Me got an error while attempting to connect')
                    print(e)
                    return

            try :
                self.socket.sendall("""{}\r\n""".format(json.dumps(_data)).encode('utf-8'))
                recieved = self.socket.recv(1024)
                # get the content length from td-completes-me tcp header
                headers = recieved.decode('utf-8').split('\n\r')
                content_length = int(headers[2].split(': ')[1])

                # read completion items or time out. 
                _data_buf = b''
                MAX_READ_ATTEMPTS = 300
                current_read_attempt = 0
                while(len(_data_buf) < content_length and current_read_attempt < MAX_READ_ATTEMPTS) :
                    try :
                        part = self.socket.recv(1024)
                        current_read_attempt += 1
                        _data_buf += part

                    except Exception as e:
                        print(e)
                        self.socket.close()
                        self.connected = False
                        return

                # docstrings are also available here but I can't figure out a way to show them in sublime
                new_completions = [[item['label'], item['detail']] for item in json.loads(_data_buf.decode('utf-8'))]
                if(len(new_completions)) :
                    self.socket.close()
                    self.connected = False

                # Format for stl. TODO : limit hint after \t to certain number of character to make it look better in tiny STL window
                    return [["""{}\t{}""".format(item[0],item[1]),"""{}""".format(item[0])] for item in new_completions]

                else :
                    return []

            except Exception as ex :
                traceback.print_exception(type(ex), ex, ex.__traceback__)
                self.socket.close()
                self.connected = False

                return[]


    def on_query_completions(self, view, prefix, locations):
        loc = locations[0]

        # limit you completions scope
        if not view.score_selector(loc, "source"):
            return


        # bail if we don't have a path
        if not view.file_name() :
            return

        # get the text of the line we're interested in
        text = view.substr(view.line(loc))

        #get a char
        char = loc - view.line(loc).begin()

        if char < 3 :
            return

        # td-completes-me expects a series of lines and a line index.
        # we'll just pass the one and an index of zero

        data = {
            "current_document" : {
                "_uri" :view.file_name()
                }
                ,
                "lines" : [text],
                "line_idx" : 0,
                "char" : char
        } 
        return self._get_completions(data, view)
        




	