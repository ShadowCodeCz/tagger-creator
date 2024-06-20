import logging
import yapsy.IPlugin


class TestKeyPressHandler(yapsy.IPlugin.IPlugin):

    def handle(self, params):
        print("Key event handel")
        print(params.directory)

    def plugin_id(self):
        return "test.key.handler"
