import time

class Worker:
    def __init__(self, app):
        self.app = app
    def run(self):
        # time.sleep(3)
        # print('getChats')
        self.app.td_send({'@type': 'getChats',
                    # 'chat_list': {'@type': 'chatListMain'},
                    # 'offset_order': 0,
                    # 'offset_chat_id': 0,
                    'limit': 10,
                    '@extra': 'getChats'})