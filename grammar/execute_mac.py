# Low-level execution of AST commands on mac using TODO.

import os
import subprocess

from spark import GenericASTTraversal


class ExecuteCommands(GenericASTTraversal):
    def __init__(self, ast, real = True):
        GenericASTTraversal.__init__(self, ast)
        self.output = []
        self.automator = Automator(real)

        self.postorder()
        self.automator.flush()

    def n_char(self, node):
        self.automator.key(node.meta[0])
    def n_raw_char(self, node): # special things like space/tab/escape/...
        self.automator.raw_key(node.meta[0])
    def n_mod_plus_key(self, node): # where is this used tho?
        self.automator.mod_plus_key(node.meta[0], node.meta[1])
    def n_movement(self, node): # up, down, left, right
        self.automator.raw_key(node.meta[0].type)
    def n_sequence(self, node):  # TODO: Implement this as paste
        for c in node.meta[0]:
            self.automator.key(c)
    def n_word_sequence(self, node):
        n = len(node.children)
        for i in range(0, n):
            word = node.children[i].meta
            for c in word:
                self.automator.key(c)
            if(i + 1 < n):
                self.automator.raw_key('space')
    def n_null(self, node):
        pass

    def n_repeat(self, node):
        xdo = self.automator.xdo_list[-1]
        for n in range(1, node.meta[0]):
            self.automator.xdo(xdo)

    def default(self, node):
#        for child in node.children:
#            self.automator.execute(child.command)
        pass


class Automator:
    def __init__(self, real = True):
        self.xdo_list = []
        self.real = real

    def xdo(self, xdo):
        self.xdo_list.append(xdo)

    def flush(self):
        if len(self.xdo_list) == 0: return

        command = '/usr/local/bin/cliclick' + ' '
        command += ' '.join(self.xdo_list)
        self.execute(command)
        self.xdo_list = []

    def execute(self, command):
        if command == '': return

        print "`%s`" % command
        if self.real:
            os.system(command)

    def paste(self, string):
        """Use pbcopy and keypresses to enter long strings, being sure to leave
        the clipboard unchanged."""
        clipboard = subprocess.check_output('pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')

        process = subprocess.Popen(
            'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(string.encode('utf-8'))

        # use pbcopy to put it in clipboard
        # trigger key presses for paste
        process = subprocess.Popen(
            'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(clipboard.encode('utf-8'))

        pass

    def raw_key(self, k):
        m = {
            "up": "arrow-up",
            "down": "arrow-down",
            "left": "arrow-left",
            "right": "arrow-right",
            "Return": "enter",
            "BackSpace": "delete",
            "Escape": "esc",
            #text: colon, semicolon, apostrophe, quotedbl, exclam, numbersign,
            #dollar, percent, caret, ampersand, parenlegt, parenright,
            # underscore, backslash, period, question, comma
            "equal": "num-equals",
            "Tab": "tab",
            "asterisk": "num-multiply",
            "minus": "num-minus",
            "plus": "num-plus",
            "slash": "num-divide",
        }
        if(k == "'"): k = 'apostrophe'
        elif(k == '.'): k = 'period'
        elif(k == '-'): k = 'minus'
        if k in m:
            self.xdo('kp:' + m[k])
        else:
            self.xdo('kp:' + k)

    def key(self, k):
        if(len(k) > 1): k = k.capitalize()
        self.xdo('t:' + k)
    def mod_plus_key(self, m, k):
        if(len(k) > 1): k = k.capitalize()
        self.xdo('key ' + m + '+' + k)

def execute(ast, real):
    ExecuteCommands(ast, real)
