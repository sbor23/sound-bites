# -*- coding: utf-8 -*-
from psychopy.visual import TextBox, Rect, TextStim
from psychopy import core, event

from button import Button
from choice_screen import HoverBox
from utils import Screen
import config

BOX_SIZE = (150, 150)
BOX_SPACING = 50
FONT_SIZE = 30
WHITE = [1,1,1]
BLACK = [-1,-1,-1]
GREY = [0,0,0]

box_info = {
    'oA': {
        'pos': (-200, 0),
        'overlay_text': 'A'},
    'oB': {
        'pos': (200, 0),
        'overlay_text': 'B'}
}


class InputBox(Screen):
    """
    This is a text box for multiple choice and text response questions. Text boxes
    activate when they are clicked and collect keystrokes. They may be restricted to
    accept integers only.
    """

    def __init__(self, window, mouse, pos, width, height, pre_text='', restricted=False):
        self.window = window
        self.mouse = mouse
        self.pos = pos
        self.w = width
        self.h = height
        self.rect = Rect(self.window, pos=self.pos, width=self.w, height=self.h, lineColor='black', fillColor=WHITE)
        self.inner_text = TextStim(self.window, pos=self.pos, text='', color='black', font='Helvetica',
                                   height=20, alignHoriz='left', wrapWidth=self.w)
        self.responseText = ''
        self.response = TextStim(self.window, pos=(self.rect.pos[0] - self.rect.width / 2 + 5, self.rect.pos[1] + self.rect.height / 2 - 10), text=self.responseText, color="black", wrapWidth=self.w,
                                        alignHoriz='left', alignVert='top')
        if restricted:
            self.keyList = [str(i) for i in range(0, 10)]
        else:
            self.keyList = None

    def draw(self):
        # self.mouse.clickReset()
        punctuation = {'period': '.', 'space': ' ', 'apostrophe': "'", 'question': '?', 'exclamation': '!',
                       'comma': ',', 'colon': ':', 'semicolon': ';', 'parenleft': '(', 'parenright': ')',
                       'minus': '-'}

        # dump the keylist
        # event.getKeys()

        letterlist = event.getKeys(self.keyList)
        for l in letterlist:
            if l == 'backspace' and len(self.responseText) > 0:
                self.responseText = self.responseText[:-1]
            elif len(self.responseText) >= 6:   # don't overflow
                break
            elif l in punctuation.keys():
                self.responseText += punctuation[l]
            elif l != 'backspace' and not len(l) > 1:
                self.responseText += l.capitalize()
        # continually redraw text onscreen while condition persists
        self.response.setText(self.responseText)
        self.rect.draw()
        self.inner_text.draw()
        self.response.draw()

        event.clearEvents()

    def clear(self):
        self.rect.setAutoDraw(False)
        self.pre_text.setAutoDraw(False)
        self.inner_text.setAutoDraw(False)
        self.response.setAutoDraw(False)

    def getResponse(self):
        return self.responseText

    # def setPos(self, pos):
    #     self.rect.pos = (pos[0], pos[1] - self.rect.width / 5)
    #     self.pre_text.pos = (self.rect.pos[0] - self.rect.width / 2 + 5, self.rect.pos[1] + self.rect.height / 2 - 30)
    #     self.response.pos = (self.rect.pos[0] - self.rect.width / 2 + 5, self.rect.pos[1] + self.rect.height / 2 - 10)


class OperationScreen:
    def __init__(self, win, mouse, operation, stim_id, method='click'):
        self.win = win
        self.mouse = mouse
        self.operation = operation
        self.stim_id = stim_id
        self.operation_type = operation['op']
        self.method = method

        # self.n_gambles = len(gambles)

        # create terms and operation text objects
        self.boxes = {}
        for i in ['oA', 'oB']:
            self.boxes[i] = HoverBox(
                win=self.win,
                stim_id=self.stim_id,
                mouse=self.mouse,
                display_method=self.method,
                pos=box_info[i]['pos'],
                text=self.operation[i],
                text_overlay=box_info[i]['overlay_text'],
                size=BOX_SIZE,
                fontsize=FONT_SIZE,
                fontsize_overlay=16)

        # create choice buttons
        #self.choice_buttons = self.generate_choice_buttons()

        # create text input box
        self.inputBox = InputBox(
            window=self.win,
            mouse=self.mouse,
            pos=(350, 0),
            width=100,
            height=50,
            restricted=False
        )
        # create submit button
        self.submit = Rect(self.win, width=75, height=50, pos=(0, -self.win.size[1] / 2 + 50),
                                  fillColor='blue')
        self.subText = TextStim(self.win, text='Weiter', height=15, pos=(0, -self.win.size[1] / 2 + 50),
                                       color='white')

    def display(self):
        self.mouse.clickReset()
        config.log_append("DisplayOperation", "")

        # setup before first gamble
        submit = False
        first_keystroke = False

        # keep displaying current gamble
        while not submit:
            # check for first keystroke
            if not first_keystroke and self.inputBox.getResponse():
                config.log_append("First_Keystroke", "")
                first_keystroke = True

            # check if 'Weiter' is clicked
            if self.mouse.isPressedIn(self.submit) and self.inputBox.getResponse():
                config.log_append("TextResponse", self.inputBox.getResponse())
                config.log_append("Next", "")
                # break
                submit = True

            # # check for mouse events for boxes (enter, select, leave)
            # for b in self.boxes.values():
            #     b.check_mouse(self.global_clock)

            # draw elements
            [self.boxes[t].draw() for t in self.boxes]
            # self.op_box.draw()
            # self.op.draw()
            self.submit.draw()
            self.subText.draw()
            self.inputBox.draw()
            self.win.flip()

    def get_operation_type(self):
        return self.operation_type
