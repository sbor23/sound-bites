# -*- coding: utf-8 -*-
import os, csv, time, sys
from random import randint, sample, choice, shuffle, seed

from psychopy import core, event, gui, sound
from psychopy.visual import Window, TextStim, ImageStim, Rect, GratingStim

from choice_screen import ChoiceScreen
from operations_screen import OperationScreen
import config
from utils import from_csv


class InstructionScreen:
    """
    This is a class for instructions only. Text stays up
    until a key has been pressed.
    """

    def __init__(self, window, mouse, image):
        self.window = window
        self.mouse = mouse
        self.  = ImageStim(win=window, image=image, interpolate=True) #, size=(800, 800))
        # self.instruction = TextStim(self.window, text=self.text, color='black',
        #                                font='Helvetica', wrapWidth=.9 * self.window.size[0])

        self.next = Rect(self.window, width=75, height=50, pos=(0, -self.window.size[1] / 2 + 50),
                                  fillColor='blue')
        self.nextText = TextStim(self.window, text='Weiter', height=15, pos=(0, -self.window.size[1] / 2 + 50),
                                color='white')

    def display(self):
        self.mouse.clickReset(buttons=(0,1,2))
        instr_timer = core.Clock()
        while True:
            self.instruction.draw()
            self.next.draw()
            self.nextText.draw()
            self.window.flip()
            if self.mouse.isPressedIn(self.next) and instr_timer.getTime() > 2:
                break

# set path
os.chdir(sys.path[0])

### Screen config
XRES = 900
YRES = 900

BOX_SIZE = (150, 150)
BOX_SPACING = 50
FONT_SIZE = 30
LIGHTGREY = [0.5, 0.5, 0.5]

RES_PATH = 'resources/'
OUTPUT_PATH = 'output/'
SOUND_PATH = 'resources/audio/'
INSTR_PATH = 'resources/instructions/'

### Construct experiment
# get respondent info
expInfo = {'VPN': '', 'Geschlecht': ''}
expInfoDlg = gui.Dlg(title="Experiment Log")
expInfoDlg.addField('VPN')
expInfoDlg.addField('Geschlecht', choices=["m", "f"])
expInfoDlg.show()  # show dialog and wait for OK or Cancel

if expInfoDlg.OK:  # then the user pressed OK
    expInfo = dict(zip(["VPN", "Geschlecht"], expInfoDlg.data))
    print(expInfo)
elif expInfoDlg.OK or not expInfo['VPN'] or not expInfo['Geschlecht']:
    core.quit()

# Create output file
fileName = OUTPUT_PATH + expInfo['VPN'] + '_' + time.strftime("%Y%m%d-%H%M%S") + '_mousetracking.csv'

# create window and mouse objects
window = Window((XRES, YRES), allowGUI=False, color=LIGHTGREY, fullscr=True,
                monitor='testMonitor', winType='pyglet', units='pix')
mouse = event.Mouse(win=window)

# load gambles, set condition
# TODO: adjust for data collection
gambles = from_csv(RES_PATH, 'Gambles.csv')
operations = from_csv(RES_PATH, 'Operationen alle.csv')
# gambles = from_csv(RES_PATH, 'samples/gambles_5.csv')
# operations = from_csv(RES_PATH, 'samples/operations_5.csv')
expInfo['condition'] = 'horizontal'

# create fixation stimulus
# fixation = GratingStim(win=window, size=20, pos=[0,0], sf=0, rgb=-1)
fixation = GratingStim(win=window, tex=None, mask='gauss', sf=0, size=15,
                       name='fixation', autoLog=False, units='pix', pos=(0.0, 0.0), color="Black")

# create instruction screen for 2. part
instr_screen = {}
instr_screen['Teil2.1'] = InstructionScreen(window, mouse, image=INSTR_PATH + "Instruktionen Teil 2 Folie 1.png")
instr_screen['Teil2.2'] = InstructionScreen(window, mouse, image=INSTR_PATH + "Instruktionen Teil 2 Folie 2.png")
instr_screen['Schluss'] = InstructionScreen(window, mouse, image=INSTR_PATH + "Schlusssatz.png")

# load instruction sound
instr_sound = {}
for i in ['instr_erwartungswert', 'instr_grosser', 'instr_kleiner', 'instr_mal', 'instr_minus', 'instr_plus']:
    instr_sound[i] = sound.Sound(SOUND_PATH + i + '.wav')
    instr_sound[i].setVolume(0.5)

# free condition sequence
free_condition_sequence = [
    ChoiceScreen(win=window, mouse=mouse, gamble=gambles[id], stim_id=id, orientation=expInfo['condition'],
                 method="click")
    for id in gambles.keys()]
# create experiment_sequence
exp_sequence = (
    [ChoiceScreen(win=window, mouse=mouse, gamble=gambles[id], stim_id=id, orientation=expInfo['condition'],
                  method="click")
     for id in gambles.keys()] +
    [OperationScreen(win=window, mouse=mouse, operation=operations[id], stim_id=id, method='click')
     for id in operations.keys()]
)

# generate random order
shuffle(free_condition_sequence)
shuffle(exp_sequence)

# create clocks
config.exp_clock = core.Clock()
config.trial_clock = core.Clock()

### Experiment loop
# "free condition": display only choice screens
config.log_append("StartFreeCondition", "")

for screen in free_condition_sequence:
    sound_played = False
    config.increase_trial(screen.stim_id)
    config.log_append("DisplayFixation", "")

    # fixation
    while config.trial_clock.getTime() < 5:
        fixation.draw()
        window.flip()

    # choice screen: contains own loop
    screen.display()

# instruction slides for main experiment
config.log_append("InstructionTeil2", "")
instr_screen['Teil2.1'].display()
instr_screen['Teil2.2'].display()

# main experiment: display all them screens
config.log_append("StartMainExperiment", "")

for screen in exp_sequence:
    sound_played = False
    config.increase_trial(screen.stim_id)
    config.log_append("DisplayFixation", "")

    # first fixation , after 1s the instruction sound
    while config.trial_clock.getTime() < 5:
        fixation.draw()
        window.flip()
        if config.trial_clock.getTime() >= 1 and not sound_played:
            if isinstance(screen, ChoiceScreen):
                i = 'instr_erwartungswert'
                instr_sound[i].play()
                core.wait(instr_sound[i].duration)
            elif isinstance(screen, OperationScreen):
                if screen.get_operation_type() == '+':
                    i = 'instr_plus'
                elif screen.get_operation_type() == '-':
                    i = 'instr_minus'
                elif screen.get_operation_type() == '*':
                    i = 'instr_mal'
                elif screen.get_operation_type() == '>':
                    i = 'instr_grosser'
                instr_sound[i].play()
                core.wait(instr_sound[i].duration)
            sound_played = True

    screen.display()

# end instruction
config.log_append("InstructionSchluss", "")
instr_screen['Schluss'].display()


# add experiment info to log entries
[config.resp_data[i].update({'respondent': expInfo['VPN'], 'sex': expInfo['Geschlecht'], 'condition': expInfo['condition']})
 for i in range(len(config.resp_data))]
# encode everything as unicode
config.resp_data = [
    {(k.encode('utf-8') if isinstance(k, unicode) else k): (v.encode('utf-8') if isinstance(v, unicode) else v)
     for (k, v) in row.iteritems()} for row in config.resp_data]

with open(fileName, 'wb') as csvfile:
    fieldnames = (['respondent', 'sex', 'condition'] + config.log_fields)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(config.resp_data)
