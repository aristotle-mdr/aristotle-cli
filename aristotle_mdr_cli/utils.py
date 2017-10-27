import requests

class AristotleCommand(object):
    def hello_are_you_there(self, url=""):
        return requests.get(
            self.registry['base'],
        )
