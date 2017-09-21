# -*- coding: utf-8 -*-
from psychopy.visual import TextBox, Rect, TextStim
from collections import OrderedDict

from button import Button
from utils import Screen
import config

BOX_SIZE = (150, 150)
BOX_SPACING = 50

FONT_SIZE = 30

### Colors
WHITE = [1,1,1]
BLACK = [-1,-1,-1]
GREY = [0,0,0]
LIGHTGREY = [0.5,0.5,0.5]

box_overlay = OrderedDict()
box_overlay['a1Value'] = 'Ergebnis A1'
box_overlay['a1Likely'] = 'Wahrschein- lichkeit A1'
box_overlay['a2Value'] = 'Ergebnis A2'
box_overlay['a2Likely'] = 'Wahrschein- lichkeit A2'
box_overlay['b1Value'] = 'Ergebnis B1'
box_overlay['b1Likely'] = 'Wahrschein- lichkeit B1'
box_overlay['b2Value'] = 'Ergebnis B2'
box_overlay['b2Likely'] = 'Wahrschein- lichkeit B2'


class HoverBox:
    def __init__(self, win, mouse, stim_id, display_method, pos, text, text_overlay, size, fontsize, fontsize_overlay):
        self.mouse = mouse
        self.stim_id = stim_id
        self.clicked = False  # mouse clicked/hovered?
        self.entered = False  # mouse over box?
        self.display_method = display_method  # hover or click
        self.text_overlay = text_overlay
        self.text = text

        self.text_box = TextStim(
            win=win,
            pos=pos,
            text=text,
            # size=size,
            # font_name="Fira Mono",
            # font_size=fontsize,
            color=BLACK,
            units='pix',
            # grid_stroke_width=0,
            # grid_horz_justification='center',
            # grid_vert_justification='center',
        )
        self.text_box.size = size[1]

        self.overlay_text = TextStim(
            win=win,
            pos=pos,
            text=text_overlay,
            # size=size,
            # font_size=fontsize_overlay,
            color=WHITE,
            opacity=1,
            units='pix',
            # grid_stroke_width=0,
            # grid_horz_justification='center',
            # grid_vert_justification='center',
        )
        self.overlay_text.wrapWidth = size[1]

        self.overlay_box = Rect(
            win=win,
            pos=pos,
            size=(2*size[0] + 2, 2*size[1] + 2),
            fillColor=GREY,
            opacity=1,
            units='pix',
            interpolate=False,
            lineWidth=0,
        )
        self.overlay_box.setUseShaders()

    def draw(self):
        # check mouse
        self.check_mouse()
        if self.display_method == 'click' and self.clicked or \
                        self.display_method == 'hover' and self.entered:
            self.text_box.draw()
        else:
            self.text_box.draw()
            self.overlay_box.draw()
            self.overlay_text.draw()

    def check_mouse(self):
        '''
        :returns text if box is freshly selected
        sets self.clicked accordingly
        '''

        # first entrance -> log BoxEnter
        if not self.entered and self.overlay_box.contains(self.mouse):
                self.entered = True
                config.log_append("BoxEnter", self.text_overlay)

        # first leave -> BoxLeave
        elif self.entered and not self.overlay_box.contains(self.mouse):
            self.entered = False
            self.clicked = False
            config.log_append("BoxLeave", self.text_overlay)

        if self.display_method == 'click':
            if not self.clicked and self.mouse.isPressedIn(self.overlay_box):
                self.clicked = True
                config.log_append("BoxClick", self.text_overlay)

    def set_text(self, text):
        self.text_box.setText(text)


class ChoiceScreen(Screen):
    def __init__(self, win, mouse, gamble, stim_id, method="click", orientation="horizontal"):
        self.win = win
        self.mouse = mouse
        self.orientation = orientation
        self.method = method

        self.gamble = gamble
        self.stim_id = stim_id

        # create boxes
        self.boxes = self.generate_hoverboxes()
        # create choice buttons
        self.choice_buttons = self.generate_choice_buttons()
        # create submit button
        self.submit = Rect(self.win, width=75, height=50, pos=(0, -self.win.size[1] / 2 + 50),
                                  fillColor='blue')
        self.subText = TextStim(self.win, text='Weiter', height=15, pos=(0, -self.win.size[1] / 2 + 50),
                                       color='white')

    def display(self):
        self.mouse.clickReset()
        config.log_append("DisplayGamble", "")

        # for btn in self.choice_buttons:
        #     btn.checked = False
        #     btn._setStyle(btn.normalStyle)
        submit = False
        selection = False

        # keep displaying current gamble
        while not submit:
            # check for gamble selection
            for i in range(len(self.choice_buttons)):
                if self.mouse.isPressedIn(self.choice_buttons[i]) and not self.choice_buttons[i].checked:
                    # on first selection -> set as checked
                    selection = self.choice_buttons[i]
                    self.choice_buttons[i].checked = True
                    self.choice_buttons[i]._setStyle(self.choice_buttons[i].checkedStyle)

                    # if other button was checked already -> uncheck it
                    if self.choice_buttons[(i+1)%2].checked:
                        self.choice_buttons[(i + 1) % 2].checked = False
                        self.choice_buttons[(i + 1) % 2]._setStyle(self.choice_buttons[(i + 1) % 2].normalStyle)

                    config.log_append("Choice", self.choice_buttons[i].text)

            # check if 'Weiter' is clicked
            if self.mouse.isPressedIn(self.submit) and selection:
                config.log_append("Next", "")
                break

            # draw elements
            [b.draw() for b in self.boxes.values()]
            [b.draw() for b in self.choice_buttons]
            self.submit.draw()
            self.subText.draw()
            self.win.flip()

    def generate_positions(self, size=BOX_SIZE, spacing=BOX_SPACING, orientation="horizontal"):
        x_step = spacing + size[0]
        y_step = spacing + size[1]
        x_start = -(1.5 * spacing + 1.5 * size[0])
        y_start = -(0.5 * spacing + 0.5 * size[1])

        # start with A
        pos = [((x_start + i * x_step), y_start) for i in range(4)]
        # add B
        pos.extend([((x_start + i * y_step), -y_start) for i in range(4)])

        # flip coordinates for vertical orientation, move up 50px
        if orientation == "vertical":
            pos = [(tup[1], -tup[0] + 50) for tup in pos]

        # combine with button name
        ret = dict(zip(box_overlay.keys(), pos))
        return ret

    def set_gamble(self, gamble):
        for box_key in self.boxes:
            if 'Likely' in box_key:
                text = str(gamble[box_key]) + "%"
            else:
                text = str(gamble[box_key])
            self.boxes[box_key].set_text(text)

    # def advance(buttonA, buttonB):
    #     for btn in (buttonA, buttonB):
    #         if mouse.isPressedIn(btn):
    #             print (str(trialClock.getTime()) + ", Advance, " + btn.text)
    #             return True
    #     return False

    def generate_hoverboxes(self):
        ret = dict()
        positions = self.generate_positions(orientation=self.orientation)

        for b in box_overlay.keys():
            # TODO appropriate starting gamble
            if 'Likely' in b:
                text = str(self.gamble[b]) + "%"
            else:
                text = str(self.gamble[b])

            ret[b] = HoverBox(win=self.win,
                              stim_id=self.stim_id,
                              mouse=self.mouse,
                              display_method=self.method,
                              pos=positions[b],
                              text=text,
                              text_overlay=box_overlay[b],
                              size=BOX_SIZE,
                              fontsize=FONT_SIZE,
                              fontsize_overlay=16)
        return ret

    def generate_choice_buttons(self):
        pos = self.generate_positions(orientation=self.orientation)
        # add offset to last A & B buttons
        if self.orientation == "horizontal":
            buttonA_pos = (pos['a2Likely'][0] + BOX_SIZE[0], pos['a2Likely'][1])
            buttonB_pos = (pos['b2Likely'][0] + BOX_SIZE[0], pos['b2Likely'][1])
        if self.orientation == "vertical":
            buttonA_pos = (pos['a2Likely'][0], pos['a2Likely'][1] - BOX_SIZE[1])# - BOX_SPACING/2)
            buttonB_pos = (pos['b2Likely'][0], pos['b2Likely'][1] - BOX_SIZE[1])# - BOX_SPACING/2)

        return [Button(self.win, u"Wähle A", pos=buttonA_pos),
                Button(self.win, u"Wähle B", pos=buttonB_pos)]