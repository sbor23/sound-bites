# -*- coding: utf-8 -*-
# global log_fields, resp_data, exp_clock, trial_clock, stim_id

log_fields = ['exp_clock', 'trial_clock', 'block', 'block_nr', 'trial_nr', 'stim_id', 'event', 'value', 'responseTime']
resp_data = []

exp_clock = None
trial_clock = None
block = None
block_nr = 0
trial_nr = 0
stim_id = 0

visual_stimuli = {}
sound_stimuli = {}
ratingscales = []


def increase_trial(id):
    global trial_nr, stim_id
    trial_nr = trial_nr + 1
    stim_id = id
    trial_clock.reset()


def increase_block(block_name):
    global block_nr, block, trial_nr
    block = block_name
    block_nr = block_nr + 1
    trial_nr = 0


def log_append(event, value, responseTime):
    combined = dict(
        zip(log_fields,
            [exp_clock.getTime(), trial_clock.getTime(), block, block_nr, trial_nr, stim_id, event,
             value, responseTime]))
    resp_data.append(combined)
    print combined

# def log_append(id, event, text_overlay, text):
#     '''
#
#     :param id:
#     :param event:
#     :param text_overlay:
#     :param text:
#     :return:
#     '''
#     combined = dict(zip(log_fields, [exp_clock.getTime(), trial_clock.getTime(), trial_number, id, event, text_overlay, text]))
#     resp_data.append(combined)
#     print combined