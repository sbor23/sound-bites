# -*- coding: utf-8 -*-
import os, csv, time, sys
from os.path import join, getsize
from random import randint, sample, choice, shuffle, seed

from psychopy import core, event, gui, sound
from psychopy.visual import Window, TextStim, ImageStim, Rect, GratingStim, BaseVisualStim
from psychopy.constants import FINISHED, STARTED, NOT_STARTED

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
        self.instruction  = ImageStim(win=window, image=image, interpolate=True) #, size=(800, 800))
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


class SearchStim(BaseVisualStim):
    """
    Implement basic functionality to display a stim (images) and accept arrow keys (left, right) as response.
    Logs response and response time.
    """

    def __init__(self, window, name, image):
        super(SearchStim, self).__init__(win=window)
        self.name = name
        self.image = image
        self.stim = ImageStim(win=window, image=image, interpolate=True)

        self.clock = core.Clock()
        self.firstDraw = True
        self.noResponse = True
        self.respKeys = ['left', 'right']
        self.response = None  # will be 'left' or 'right'
        self.rt = None

        self.reset()

    def reset(self):
        self.noResponse = True
        self.firstDraw = True
        self.clock.reset()
        self.response = None    # will be 'left' or 'right'
        self.rt = None

    def draw(self):
        if self.firstDraw:
            self.firstDraw = False
            self.clock.reset()
            self.status = STARTED

        # check for keys
        for key in event.getKeys():
            print(key)
            if key in self.respKeys:
                self.response = key
                self.status = FINISHED

        self.stim.draw()

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)


### Screen config
XRES = 900
YRES = 900

BOX_SIZE = (150, 150)
BOX_SPACING = 50
FONT_SIZE = 30
LIGHTGREY = [0.5, 0.5, 0.5]

RES_PATH = 'resources/'
OUTPUT_PATH = 'output/'
SOUNDS_PATH = 'resources/sounds/exp1/'
INSTR_PATH = 'resources/instructions/'
VISUALS_PATH = 'resources/search_arrays/exp1/'

expInfo = {'VPN': '', 'Geschlecht': ''}
window = None
mouse = None

searchStims = dict()


def create_sound_stimuli():
    config.sound_stimuli = {s: sound.Sound(value=SOUNDS_PATH + s) for s in
              ['clucking_hen.wav',
               'fire_alarm.wav',
               'growling_dog.wav',
               'microwave_oven.wav']}


def create_visual_stimuli():
    # keys:
    # - salience: 'L1' = low, 'H2' = high
    # - position: 'cen' = central, 'per' = peripheral
    # - orientation: 'l' = left, 'r' = right
    for sal in ['L1', 'L2']:
        config.visual_stimuli[sal] = dict()
        for pos in ['cen', 'per']:
            config.visual_stimuli[sal][pos] = dict()
            for ori in ['l', 'r']:
                # read folder, fill dict with list of images
                config.visual_stimuli[sal][pos][ori] = list()

    for _, _, files in os.walk(VISUALS_PATH):
        # filename has format L1_cen1_l.jpg
        for f in files:
            sal, pos, ori_misc = f.split('_')
            pos = pos[:3]   # leave out number
            ori, _ = ori_misc.split('.')    # remove file extension
            ori = ori[0].lower()  # only look at orientation: L3 -> l, R4 -> r

            config.visual_stimuli[sal][pos][ori].append(
                SearchStim(window=window, image=VISUALS_PATH + f, name=f[:-4]))


def save():
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


### Construct experiment
if __name__ == '__main__':
    # get respondent info
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
    window = Window((XRES, YRES), allowGUI=False, color=LIGHTGREY, fullscr=False,
                    monitor='testMonitor', winType='pyglet', units='pix')
    mouse = event.Mouse(win=window)


    # first create all stimuli once
    create_sound_stimuli()
    create_visual_stimuli()

    # then randomly assign them to blocks




    config.exp_clock = core.Clock()



    while testStim.status != FINISHED:
        testStim.draw()
        window.flip()

    print "Response was: " + testStim.response



# # load gambles, set condition
# # TODO: adjust for data collection
# gambles = from_csv(RES_PATH, 'Gambles.csv')
# operations = from_csv(RES_PATH, 'Operationen alle.csv')
# # gambles = from_csv(RES_PATH, 'samples/gambles_5.csv')
# # operations = from_csv(RES_PATH, 'samples/operations_5.csv')
# expInfo['condition'] = 'horizontal'
#
# # create fixation stimulus
# # fixation = GratingStim(win=window, size=20, pos=[0,0], sf=0, rgb=-1)
# fixation = GratingStim(win=window, tex=None, mask='gauss', sf=0, size=15,
#                        name='fixation', autoLog=False, units='pix', pos=(0.0, 0.0), color="Black")
#
# # create instruction screen for 2. part
# instr_screen = {}
# instr_screen['Teil2.1'] = InstructionScreen(window, mouse, image=INSTR_PATH + "Instruktionen Teil 2 Folie 1.png")
# instr_screen['Teil2.2'] = InstructionScreen(window, mouse, image=INSTR_PATH + "Instruktionen Teil 2 Folie 2.png")
# instr_screen['Schluss'] = InstructionScreen(window, mouse, image=INSTR_PATH + "Schlusssatz.png")
#
# # load instruction sound
# instr_sound = {}
# for i in ['instr_erwartungswert', 'instr_grosser', 'instr_kleiner', 'instr_mal', 'instr_minus', 'instr_plus']:
#     instr_sound[i] = sound.Sound(SOUND_PATH + i + '.wav')
#     instr_sound[i].setVolume(0.5)
#
# # free condition sequence
# free_condition_sequence = [
#     ChoiceScreen(win=window, mouse=mouse, gamble=gambles[id], stim_id=id, orientation=expInfo['condition'],
#                  method="click")
#     for id in gambles.keys()]
# # create experiment_sequence
# exp_sequence = (
#     [ChoiceScreen(win=window, mouse=mouse, gamble=gambles[id], stim_id=id, orientation=expInfo['condition'],
#                   method="click")
#      for id in gambles.keys()] +
#     [OperationScreen(win=window, mouse=mouse, operation=operations[id], stim_id=id, method='click')
#      for id in operations.keys()]
# )
#
# # generate random order
# shuffle(free_condition_sequence)
# shuffle(exp_sequence)
#
# # create clocks
# config.exp_clock = core.Clock()
# config.trial_clock = core.Clock()
#
# ### Experiment loop
# # "free condition": display only choice screens
# config.log_append("StartFreeCondition", "")
#
# for screen in free_condition_sequence:
#     sound_played = False
#     config.increase_trial(screen.stim_id)
#     config.log_append("DisplayFixation", "")
#
#     # fixation
#     while config.trial_clock.getTime() < 5:
#         fixation.draw()
#         window.flip()
#
#     # choice screen: contains own loop
#     screen.display()
#
# # instruction slides for main experiment
# config.log_append("InstructionTeil2", "")
# instr_screen['Teil2.1'].display()
# instr_screen['Teil2.2'].display()
#
# # main experiment: display all them screens
# config.log_append("StartMainExperiment", "")
#
# for screen in exp_sequence:
#     sound_played = False
#     config.increase_trial(screen.stim_id)
#     config.log_append("DisplayFixation", "")
#
#     # first fixation , after 1s the instruction sound
#     while config.trial_clock.getTime() < 5:
#         fixation.draw()
#         window.flip()
#         if config.trial_clock.getTime() >= 1 and not sound_played:
#             if isinstance(screen, ChoiceScreen):
#                 i = 'instr_erwartungswert'
#                 instr_sound[i].play()
#                 core.wait(instr_sound[i].duration)
#             elif isinstance(screen, OperationScreen):
#                 if screen.get_operation_type() == '+':
#                     i = 'instr_plus'
#                 elif screen.get_operation_type() == '-':
#                     i = 'instr_minus'
#                 elif screen.get_operation_type() == '*':
#                     i = 'instr_mal'
#                 elif screen.get_operation_type() == '>':
#                     i = 'instr_grosser'
#                 instr_sound[i].play()
#                 core.wait(instr_sound[i].duration)
#             sound_played = True
#
#     screen.display()
#
# # end instruction
# config.log_append("InstructionSchluss", "")
# instr_screen['Schluss'].display()
#
#

