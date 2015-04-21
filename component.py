class Component(object):

    def __init__(self):
        pass

    def cleanup(self):
        pass

    def check(self):
        pass

    def update_menu(self, menu):
        pass

class EventHandler(object):
    def __init__(self):
        self.handlers = []

    def add(self, func):
        self.handlers.append(func)

    def remove(self, func):
        self.handlers.remove(func)

    def fire(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)
