import config


class handler:
    target = 'updateAuthorizationState'

    def __init__(self, app):
        self.app = app

    def handle(self, event):
        auth_state = event['authorization_state']

        # if client is closed, we need to destroy it and create new client
        if auth_state['@type'] == 'authorizationStateClosed':
            return

        # set TDLib parameters
        # you MUST obtain your own api_id and api_hash at https://my.telegram.org
        # and use them in the setTdlibParameters call
        if auth_state['@type'] == 'authorizationStateWaitTdlibParameters':
            self.app.td_send({'@type': 'setTdlibParameters', 'parameters': {
                'database_directory': 'tdlib',
                #    'use_test_dc': True,
                'use_message_database': True,
                'use_secret_chats': True,
                'api_id': config.api_id,
                'api_hash': config.api_hash,
                'system_language_code': 'en',
                'device_model': 'Desktop',
                'application_version': '1.0',
                'enable_storage_optimizer': True}})

        # set an encryption key for database to let know TDLib how to open the
        # database
        if auth_state['@type'] == 'authorizationStateWaitEncryptionKey':
            self.app.td_send(
                {'@type': 'checkDatabaseEncryptionKey', 'encryption_key': ''})

        # enter phone number to log in
        if auth_state['@type'] == 'authorizationStateWaitPhoneNumber':
            phone_number = input('Please enter your phone number: ')
            self.app.td_send(
                {'@type': 'setAuthenticationPhoneNumber', 'phone_number': phone_number})

        # wait for authorization code
        if auth_state['@type'] == 'authorizationStateWaitCode':
            code = input('Please enter the authentication code you received: ')
            self.app.td_send(
                {'@type': 'checkAuthenticationCode', 'code': code})

        # wait for first and last name for new users
        if auth_state['@type'] == 'authorizationStateWaitRegistration':
            first_name = input('Please enter your first name: ')
            last_name = input('Please enter your last name: ')
            self.app.td_send(
                {'@type': 'registerUser', 'first_name': first_name, 'last_name': last_name})

        # wait for password if present
        if auth_state['@type'] == 'authorizationStateWaitPassword':
            password = input('Please enter your password: ')
            self.app.td_send(
                {'@type': 'checkAuthenticationPassword', 'password': password})
