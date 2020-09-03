import sys

class forget_handler:
    targets = [
        'proxy',
        'updateDiceEmojis',
        'updateSupergroupFullInfo',
        'updateAnimationSearchParameters',
        'updateHavePendingNotifications',
        'updateChatFilters',
        'updateScopeNotificationSettings',
        'updateUnreadChatCount',
        'updateOption',
        'updateSelectedBackground',
    ]

    def __init__(self, app):
        self.app = app

    def handle(self, event):
        pass

class print_handler:
    targets = [
        'ok',
        'updateUserStatus',
        'updateConnectionState',
        'updateUser',
        'updateUserFullInfo',
        'updateNewChat',
        'chats',
        'updateChatActionBar',
        'updateChatLastMessage',
        'updateChatPosition',
        'updateSupergroup',
    ]
    def __init__(self, app):
        self.app = app

    def handle(self, event):
        print(event)
        sys.stdout.flush()
