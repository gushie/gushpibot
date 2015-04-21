from component import Component

class Command(object):
    """
    This class stores a single command
    """
    def __init__(self, shortcut, name, start_func, finish_func):
        self.shortcut = shortcut
        self.name = name
        self.start_func = start_func
        self.finish_func = finish_func

class Program(Component):
    """
    This class stores the instructions to run the program
    """
    def __init__(self, display):
        self.instructions = []
        self.commands = {}
        self.active = False
        self.display = display

    def set(self, program):
        for inst in program:
            self.add_instruction(inst)

    def cleanup(self):
        self.stop()

    def clear(self):
        self.instructions = []

    def add_command(self, shortcut, name, start_func, finish_func=None):
        self.commands[shortcut] = Command(shortcut, name, start_func, finish_func)

    def add_instruction(self, instruction):
        if instruction in self.commands.keys():
            self.instructions.append(instruction)

    def delete_instruction(self, step=-1):
        del self.instructions[step]

    def update_menu(self, menu):
        folder = menu.add_folder("Program")
        menu.add_function("View Program", self.view, folder)
        for command in self.commands:
            menu.add_function("Add " + self.commands[command].name,
                    lambda c=command: self.add_instruction(self.commands[c].shortcut), folder)
        menu.add_function("Delete Step", self.delete_instruction, folder)
        menu.add_function("Run Program", self.run, folder)
        menu.add_function("Stop Program", self.stop, folder)
        menu.add_function("Clear Program", self.clear, folder)

    def stop(self):
        self.active = False

    def run(self):
        self.active = True
        for instruction in self.instructions:
            if not self.active:
                return
            self.commands[instruction].start_func()
            time.sleep(1)
            if self.commands[instruction].finish_func:
                self.commands[instruction].finish_func()

    def view(self):
        self.display.display_at(1, 0, str(self).ljust(16))

    def __str__(self):
        curr_count = 0
        string = ""
        for instruction in self.instructions:
            if string and instruction == string[-1]:
                curr_count += 1
            else:
                if curr_count > 1:
                    string += str(curr_count)
                string += instruction
                curr_count = 1
        if curr_count > 1:
            string += str(curr_count)
        return string
