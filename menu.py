class Menu(object):

    class MenuItem(object):
        def __init__(self, name, func, folder):
            self.name = name
            self.func = func
            self.folder = folder

        def fire(self):
            if self.func:
                self.func()

    class MenuList(object):
        def __init__(self, parent=None):
            self.options = []
            self.parent = parent

        def add(self, name, func=None, folder=None):
            self.options.append(Menu.MenuItem(name, func, folder))

    def __init__(self, display, speech=None):
        self.root = Menu.MenuList(self)
        self.menu = self.root
        self.display = display
        self.speech = speech
        self.option = 0

    def add_folder(self, name, folder=None):
        if folder is None:
            folder = self.root
        new_folder = Menu.MenuList()
        new_folder.add("Back", folder=folder)
        folder.add(name + "/", folder=new_folder)
        return new_folder

    def add_function(self, name, func, folder=None):
        if folder is None:
            folder = self.root
        folder.add(name, func=func)

    def current_item(self):
        return self.menu.options[self.option]

    def prev(self):
        self.option -= 1
        if self.option < 0:
            self.option = len(self.menu.options) - 1
            self.display.reset()
        self.notify()

    def next(self):
        self.option += 1
        if self.option == len(self.menu.options):
            self.option = 0
            self.display.reset()
        self.notify()

    def text(self):
        return self.current_item().name

    def notify(self):
        self.display.display_at(0, 0, self.text().ljust(16))
        if self.speech:
            self.speech.speak(self.text())

    def select(self):
        if self.current_item().folder:
            self.menu = self.current_item().folder
            self.option = 0
            self.notify()
        else:
            self.current_item().fire()

