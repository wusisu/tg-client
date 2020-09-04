
class messages_handler:
    targets = [
        'messages',
    ]

    def __init__(self, app):
        self.app = app

    def handle(self, event):
        msgs = event['messages']
        for msg in msgs:
            # print(msg['content'])
            c = msg['content']
            
            if c['@type'] == 'messageAnimation':
                self.down_file(c['animation']['animation'])
            elif c['@type'] == 'messagePhoto':
                self.down_file(c['photo']['photo'])
            elif c['@type'] == 'messageVideo':
                self.down_file(c['video']['video'])

    def down_file(self, file):
        print('start downFile', file)
        self.app.td_send({'@type': 'downloadFile',
                    'file_id': file['id'],
                    'priority': 16,
                    # 'offset': 0,
                    # 'limit': 100,
                    'synchronous': True,
                    '@extra': ['downloadFile',file['id']]})