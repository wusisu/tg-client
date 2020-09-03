import auth
import sys


class registry:
    def __init__(self, app):
        self.app = app
        self._registry = {}
        self.noHandlers = set()

    def handleEvent(self, event):
        if event['@type'] not in self._registry:
            print('no handler for event type:', event['@type'])
            self.noHandlers.add(event['@type'])
            # handle an incoming update or an answer to a previously sent
            # request
            print(event)
            sys.stdout.flush()
            return
        self._registry[event['@type']].handle(event)

    def _register(self, hander):
        self._registry[hander.target] = hander(self.app)

    def __del__(self):
        print('no handlers: ', self.noHandlers)


def register_all(app):
    r = registry(app)
    r._register(auth.handler)
    return r
