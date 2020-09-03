import auth
import normal
import sys


class registry:
    def __init__(self, app):
        self.app = app
        self._registry = {}
        self.noHandlers = set()
        self._is_alive = True

    def handleEvent(self, event):
        if event['@type'] not in self._registry:
            print('no handler for event type:', event['@type'])
            self.noHandlers.add(event['@type'])
            # handle an incoming update or an answer to a previously sent
            # request
            print(event)
            sys.stdout.flush()
            return
        self._call_handlers(event)

    def add_handler_class(self, handler):
        handler_instance = handler(self.app)
        if hasattr(handler, 'target') and handler.target:
            self._add_handler(handler.target, handler_instance)
        if hasattr(handler, 'targets') and handler.targets and isinstance(handler.targets, list):
            for t in handler.targets:
                self._add_handler(t, handler_instance)

    def _add_handler(self, name, handler_instance):
        if name not in self._registry:
            self._registry[name] = []
        self._registry[name].append(handler_instance)

    def _call_handlers(self, event):
        handlers = self._registry[event['@type']]
        for handler in handlers:
            handler.handle(event)

    def __del__(self):
        self._on_del()

    def _on_del(self):
        print('no handlers: ', self.noHandlers)
    
    def terminate(self):
        self._is_alive = False


def register_all(app):
    r = registry(app)
    r.add_handler_class(auth.handler)
    r.add_handler_class(normal.forget_handler)
    r.add_handler_class(normal.print_handler)
    return r
