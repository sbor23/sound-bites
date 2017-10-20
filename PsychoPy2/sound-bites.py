# -*- coding: utf-8 -*-
import os, csv, time, sys, random, copy
from os.path import join, getsize

from psychopy import core, event, gui, sound
from psychopy.visual import Window, TextStim, ImageStim, Rect, GratingStim, BaseVisualStim, RatingScale
from psychopy.constants import FINISHED, STARTED, NOT_STARTED

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
        self.status = NOT_STARTED
        self.firstDraw = True
        self.respKeys = ['left', 'right']
        self.response = None  # will be 'left' or 'right'
        self.rt = None

        self.too_slow_box = Rect(win=window, width=200, height=120, fillColor=LIGHTGREY)
        self.too_slow_text = TextStim(win=window, text="Zu langsam", color='black')
        self.reset()

    def __str__(self):
        return "SearchStim: " + self.name

    def reset(self):
        self.status = NOT_STARTED
        self.firstDraw = True
        self.clock.reset()
        self.response = None    # will be 'left' or 'right'
        self.rt = None

    def draw(self):
        if self.firstDraw:
            self.firstDraw = False
            self.status = STARTED
            event.clearEvents('keyboard')
            self.clock.reset()

        # enforce timeout of 3.5s
        elif self.clock.getTime() > 3.5 and self.status != TIMEOUT:
            self.status = TIMEOUT

        # stop prematurely
        elif self.clock.getTime() > 5:
            self.status = FINISHED

        # check for keys
        if self.status == STARTED:
            for key in event.getKeys():
                print(key)
                if key in self.respKeys:
                    self.response = key
                    self.rt = self.clock.getTime()
                    self.status = FINISHED
        self.stim.draw()

        if self.status == TIMEOUT:
            self.too_slow_box.draw()
            self.too_slow_text.draw()

    def getResponse(self):
        if not self.status == FINISHED:
            raise "SearchStim not completed yet"
        else:
            return self.response

    def getRT(self):
        if not self.status == FINISHED:
            raise "SearchStim not completed yet"
        else:
            return self.rt

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

SOUNDS = ['cluckinghen.wav',
          'firealarm.wav',
          'growlingdog.wav',
          'microwaveoven.wav']
TIMEOUT = 3  # stimulus state constant
expInfo = {'VPN': '', 'Geschlecht': ''}

# some global objects
window = None
mouse = None
searchStims = dict()
va_sounds = list()

va_stimuli = None
vo_stimuli = None
fixation = None


def create_sound_stimuli():
    config.sound_stimuli = {s: sound.Sound(value=SOUNDS_PATH + s, name=s) for s in SOUNDS}


def create_ratingscales():
    config.ratingscales = [RatingScale(win=window, name='valence_rating', scale=u'Wie fühlen Sie sich gerade?',
                                       labels=('negativ', 'positiv'),
                                       stretch=2, pos=[0.0, -0.4], low=0, high=1, precision=100, showValue=False,
                                       markerExpansion=0, acceptText='Weiter', textColor='white'),
                           RatingScale(win=window, name='arousal_rating', scale=u'Wie fühlen Sie sich gerade?',
                                       labels=('niedrige Aktivierung', 'hohe Aktivierung'),
                                       stretch=2, pos=[0.0, -0.4], low=0, high=1, precision=100, showValue=False,
                                       markerExpansion=0, acceptText='Weiter', textColor='white')]


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
                SearchStim(window=window, name=f, image=VISUALS_PATH + f))


def block_sound_ratings():
    config.increase_block("Ratings")
    config.log_append("StartBlockRatings", "", "")
    for s in va_sounds:
        config.increase_trial(s.name)
        config.log_append("DisplayFixation", "", "")
        sound_played = False

        # fixation
        while config.trial_clock.getTime() < 0.5 + s.duration:
            if config.trial_clock.getTime() >= 0.5 and not sound_played:
                sound_played = True
                s.play()
            fixation.draw()
            window.flip()

        # ratings
        for r in config.ratingscales:
            r.reset()

            # draw scale
            while r.status != FINISHED:
                r.draw()
                window.flip()
            config.log_append(r.name, r.getRating(), r.getRT())


def block_va_search():
    config.increase_block("VA")
    config.log_append("StartBlockVA", "", "")
    for va in va_stimuli:
        va_sound = va.keys()[0]
        va_stim = va.values()[0]
        config.increase_trial("%s-%s" % (va_sound, va_stim.name))
        config.log_append("DisplayFixation", "", "")
        va_stim.reset()
        sound_played = False

        # fixation
        while config.trial_clock.getTime() < 0.5 + config.sound_stimuli[va_sound].duration:
            if config.trial_clock.getTime() >= 0.5 and not sound_played:
                print("trial clock: %f, duration: %f" %
                      (config.trial_clock.getTime(), 0.5 + config.sound_stimuli[va_sound].duration))

                sound_played = True
                config.sound_stimuli[va_sound].play()
            fixation.draw()
            window.flip()

        # search task
        while va_stim.status != FINISHED:
            va_stim.draw()
            window.flip()
        config.log_append("SearchResponse", va_stim.getResponse(), va_stim.getRT())

        # 3s empty screen
        emptyscreen_clock = core.Clock()
        while emptyscreen_clock.getTime() < 3:
            window.flip()

def block_vo_search():
    config.increase_block("VO")
    config.log_append("StartBlockVO", "", "")
    for vo in vo_stimuli:
        config.increase_trial(vo.name)
        config.log_append("DisplayFixation", "", "")
        vo.reset()

        # fixation
        while config.trial_clock.getTime() < 1:
            fixation.draw()
            window.flip()

        # search task
        while vo.status != FINISHED:
            vo.draw()
            window.flip()
        config.log_append("SearchResponse", vo.getResponse(), vo.getRT())

        # 3s empty screen
        emptyscreen_clock = core.Clock()
        while emptyscreen_clock.getTime() < 3:
            window.flip()


def save():
    # add experiment info to log entries
    [config.resp_data[i].update({'respondent': expInfo['VPN'], 'sex': expInfo['Geschlecht']})
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

def count_other_sounds(snd, dic):
    assert(isinstance(dic, dict))

    other_snds = set(SOUNDS) - set([snd])
    count = 0
    for s in other_snds:
        count += len(dic[s])
    return count


def copy_dict_list(input):
    ret = {}
    for k in input.keys():
        ret[k] = input[k][:]
    return ret


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
    fileName = OUTPUT_PATH + expInfo['VPN'] + '_' + time.strftime("%Y%m%d-%H%M%S") + '_sound-bites.csv'

    # create window and mouse objects
    window = Window((XRES, YRES), allowGUI=False, color='black', fullscr=False,
                    monitor='testMonitor', winType='pyglet', units='pix')
    mouse = event.Mouse(win=window)


    # first create all stimuli once
    fixation = GratingStim(win=window, tex=None, mask='gauss', sf=0, size=15,
                           name='fixation', autoLog=False, units='pix', pos=(0.0, 0.0), color="white")
    create_sound_stimuli()
    create_visual_stimuli()
    create_ratingscales()

    ### create random blocks
    # ratings: random sound order
    random.shuffle(SOUNDS)
    va_sounds = [config.sound_stimuli[k] for k in SOUNDS[:]]

    # va: for each sound - pick one of each combination
    # -> 8 combinations
    va_stimuli = []
    sound_stimuli = {}
    for sal in ['L1', 'L2']:
        for pos in ['cen', 'per']:
            for ori in ['l', 'r']:
                for snd in SOUNDS:
                    # get random stimuli of given category
                    if not snd in sound_stimuli.keys():
                        sound_stimuli[snd] = list()
                    sound_stimuli[snd].append({snd: random.choice(config.visual_stimuli[sal][pos][ori])})

    # randomize order, same sounds never in succession
    backup = copy_dict_list(sound_stimuli)
    for snd in SOUNDS:
        random.shuffle(sound_stimuli[snd])
    last_snd = None
    restart_count = 0

    print "Start randomizing, this can take a while..."
    start_time = time.time()
    while len(va_stimuli) < 32:
        snd = random.choice(SOUNDS)

        # store stim if there are any left of this sound
        if not snd == last_snd and len(sound_stimuli[snd]) > 0:
            last_snd = snd
            va_stimuli.append(sound_stimuli[snd].pop(0))
        # restart if only one sound is left and it's the same as last_sound
        elif snd == last_snd and count_other_sounds(snd, sound_stimuli) == 0:
            last_snd = None
            va_stimuli = []
            restart_count += 1
            sound_stimuli = copy_dict_list(backup)

        # one run takes ~1ms on this system, so allow at most 1s = 1000 runs
        if restart_count > 1000:
            sys.exit("Randomization did not succeed")
    print "Finished randomizing, taking %i restarts in %s seconds" % (restart_count, time.time() - start_time)

    # for i in va_stimuli:
    #     print("sound: %s,\tstim: %s" % (i.keys()[0], i.values()[0].name))

    # vo: pick four of each combination
    # -> 8 combinations
    vo_stimuli = []
    for sal in ['L1', 'L2']:
        for pos in ['cen', 'per']:
            for ori in ['l', 'r']:
                for _ in xrange(4):
                    vo_stimuli.append(random.choice(config.visual_stimuli[sal][pos][ori]))
    # randomize visuals order
    random.shuffle(vo_stimuli)

    config.exp_clock = core.Clock()
    config.trial_clock = core.Clock()

    # get sound ratings
    block_sound_ratings()
    #window.setColor('black')
    #fixation.setColor('white')

    # flip a coin with which task to start...
    startVA = random.choice([True, False])
    if startVA:
        block_va_search()
        block_va_search()
        block_vo_search()
    else:
        block_vo_search()
        block_va_search()
        block_va_search()

    # save logged results
    save()
