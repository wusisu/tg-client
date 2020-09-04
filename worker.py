import time
import utils

class Discovery:
    targets = [
        'chat',
        'messages',
        'file',
        'updateFile',
    ]
    def __init__(self, app):
        self.chat_id = -1001368271720
        self.current_message_id = 0
        self.step = 50
        self.pending_files = {}
        self.pending_limit = 2
        self.app = app
        self.identity = self.chat_id
        self.read_message_count = 0
        self.last_text_message = ''
        self.requesting = False
    def read_more(self):
        self.status()
        if self.requesting:
            return
        if self.current_message_id <= 0:
            print('current_message_id <= 0', self.current_message_id)
            return
        if len(self.pending_files.keys()) >= self.pending_limit:
            return
        # print('request messages', self.current_message_id)
        self.requesting = True
        self.app.td_send({'@type': 'getChatHistory',
            'chat_id': self.chat_id,
            'from_message_id': self.current_message_id,
            'offset': 0,
            'limit': self.step,
            '@extra': [self.identity, self.current_message_id]})
    def handle(self, event):
        et = event['@type']
        extra = event['@extra'] if '@extra' in event else 'None'
        c = 0
        if et == 'messages':
            c = event['total_count']
        # print('called Discovery handle', et, extra, c)
        if et == 'chat' and event['@extra'] == self.identity:
            self.current_message_id = event['last_message']['id']
            self.read_more()
        elif et == 'messages' and isinstance(event['@extra'], list) and event['@extra'][0] == self.identity and event['@extra'][1] == self.current_message_id:
            self.handle_messages(event)
            self.read_more()
        elif et == 'file' and isinstance(event['@extra'], list) and event['@extra'][0] == self.identity:
            self.handle_file(event)
            self.read_more()
        elif et == 'updateFile':
            self.handle_file(event['file'])
            self.read_more()
    def handle_file(self, event):
        # copy file
        # print(event)
        if event['id'] in self.pending_files:
            if event['local']['is_downloading_completed']:
                self.pending_files.pop(event['id'])
        pass
        
    def handle_messages(self, event):
        self.requesting = False
        if event['total_count'] == 0:
            self.current_message_id = -1
            print('has read all messages')
            return
        self.read_message_count += event['total_count']
        for msg in event['messages']:
            c = msg['content']
            if c['@type'] == 'messageText':
                # print(c['text']['text'])
                self.last_text_message = c['text']['text']
            elif c['@type'] == 'messageAnimation':
                self.down_file(c['animation']['animation'])
            elif c['@type'] == 'messagePhoto':
                self.down_file(max(c['photo']['sizes'], key=lambda ph: ph['photo']['size'])['photo'])
            elif c['@type'] == 'messageVideo':
                self.down_file(c['video']['video'])
        # print(self.current_message_id, ','.join(str(m['id']) for m in event['messages']))
        self.current_message_id = event['messages'][-1]['id']
        
    def down_file(self, f):
        self.pending_files[f['id']] = f
        self.app.td_send({'@type': 'downloadFile',
                    'file_id': f['id'],
                    'priority': 16,
                    # 'offset': 0,
                    # 'limit': 100,
                    'synchronous': True,
                    '@extra': [self.identity, 'downloadFile',f['id']]})
    def status(self):
        print(','.join([str(i) for i in self.pending_files.keys()]), 'downloading... ', self.read_message_count, ' messages read. current message is', self.last_text_message)
    def start(self):
        self.app.td_send({'@type': 'getChat',
                    'chat_id': self.chat_id,
                    '@extra': self.identity})

class Worker:
    def __init__(self, app, registry):
        self.app = app
        self.registry = registry
    
    def run(self):
        def is_authenticated(app):
            return app.authenticated
        if not utils.wait_until(is_authenticated, 600, 0.25, self.app):
            print('wait 600s before authenticated')
            exit(1)
        d = self.registry.add_handler_class(Discovery)
        d.start()
        
        # self.app.td_send({'@type': 'getChats',
        #             # 'chat_list': {'@type': 'chatListMain'},
        #             # 'offset_order': 0,
        #             # 'offset_chat_id': 0,
        #             'limit': 5,
        #             '@extra': 'getChats'})

        # self.app.td_send({'@type': 'getChat',
        #             'chat_id': -1001368271720,
        #             '@extra': 'getChat switch group'})

        # self.app.td_send({'@type': 'getChatMessageByDate',
        #             'chat_id': -1001368271720,
        #             'date': 1599187071,
        #             '@extra': 'getChatMessageByDate switch group'})

        # self.app.td_send({'@type': 'getChatHistory',
        #             'chat_id': -1001368271720,
        #             'from_message_id': 14911799296,
        #             'offset': 0,
        #             'limit': 100,
        #             '@extra': 'getChatHistory switch group'})

        # self.app.td_send({'@type': 'getChatHistory',
        #             'chat_id': 1247866323,
        #             'from_message_id': 4696571904,
        #             'offset': 0,
        #             'limit': 100,
        #             '@extra': 'getChatHistory collectionbot'})

