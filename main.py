#
# Copyright Aliaksei Levin (levlam@telegram.org), Arseny Smirnov (arseny30@gmail.com),
# Pellegrino Prevete (pellegrinoprevete@gmail.com)  2014-2020
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
from ctypes.util import find_library
from ctypes import CDLL, c_void_p, c_char_p, c_double, CFUNCTYPE
import json
import sys
import registry
import config
import threading
import worker

# load shared library
tdjson_path = find_library('tdjson') or 'tdjson.dll'
if tdjson_path is None:
    print('can\'t find tdjson library')
    quit()
tdjson = CDLL(tdjson_path)

# load TDLib functions from shared library
td_json_client_create = tdjson.td_json_client_create
td_json_client_create.restype = c_void_p
td_json_client_create.argtypes = []

td_json_client_receive = tdjson.td_json_client_receive
td_json_client_receive.restype = c_char_p
td_json_client_receive.argtypes = [c_void_p, c_double]

td_json_client_send = tdjson.td_json_client_send
td_json_client_send.restype = None
td_json_client_send.argtypes = [c_void_p, c_char_p]

td_json_client_execute = tdjson.td_json_client_execute
td_json_client_execute.restype = c_char_p
td_json_client_execute.argtypes = [c_void_p, c_char_p]

td_json_client_destroy = tdjson.td_json_client_destroy
td_json_client_destroy.restype = None
td_json_client_destroy.argtypes = [c_void_p]

fatal_error_callback_type = CFUNCTYPE(None, c_char_p)

td_set_log_fatal_error_callback = tdjson.td_set_log_fatal_error_callback
td_set_log_fatal_error_callback.restype = None
td_set_log_fatal_error_callback.argtypes = [fatal_error_callback_type]

# initialize TDLib log with desired parameters


def on_fatal_error_callback(error_message):
    print('TDLib fatal error: ', error_message)


def td_execute(query):
    query = json.dumps(query).encode('utf-8')
    result = td_json_client_execute(None, query)
    if result:
        result = json.loads(result.decode('utf-8'))
    return result


c_on_fatal_error_callback = fatal_error_callback_type(on_fatal_error_callback)
td_set_log_fatal_error_callback(c_on_fatal_error_callback)

# setting TDLib log verbosity level to 1 (errors)
print(td_execute({'@type': 'setLogVerbosityLevel',
                  'new_verbosity_level': 1, '@extra': 1.01234}))

# # another test for TDLib execute method
# print(td_execute({'@type': 'getTextEntities', 'text': '@telegram /test_command https://telegram.org telegram.me', '@extra': ['5', 7.0]}))

# # testing TDLib send method
# td_send({'@type': 'getAuthorizationState', '@extra': 1.01234})

class app:
    def __init__(self):
        # create client
        self.client = td_json_client_create()
        self.authenticated = False
        # simple wrappers for client usage

    def td_send(self, query):
            query = json.dumps(query).encode('utf-8')
            td_json_client_send(self.client, query)

    def td_receive(self):
        result = td_json_client_receive(self.client, 1.0)
        if result:
            result = json.loads(result.decode('utf-8'))
        return result

    def proxy(self):
        if config.proxy and config.proxy['enable']:
            self.td_send({'@type': 'addProxy',
                    'server': config.proxy['server'],
                    'port': config.proxy['port'],
                    'enable': True,
                    'type': {'@type': 'proxyTypeSocks5'},
                    '@extra': 'addProxy'})

def runLoop(the_handlers):
    try:
        # main events cycle
        while the_handlers._is_alive:
            event = the_handlers.app.td_receive()
            if event:
                the_handlers.handleEvent(event)
                # # handle an incoming update or an answer to a previously sent request
                # print(event)
                # sys.stdout.flush()
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            pass
        else:
            raise e
    finally:
        print('closing td client')
        # destroy client when it is closed and isn't needed anymore
        td_json_client_destroy(the_handlers.app.client)

myapp = app()
myapp.proxy()
handlers = registry.register_all(myapp)

t = threading.Thread(target=runLoop, args=[handlers])
t.start()

w = worker.Worker(myapp, handlers)
w.run()

try:
    t.join()
except BaseException as e:
    print(type(e))
finally:
    handlers.terminate()
t.join()