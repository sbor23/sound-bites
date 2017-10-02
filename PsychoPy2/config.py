# -*- coding: utf-8 -*-
# global log_fields, resp_data, exp_clock, trial_clock, stim_id

log_fields = ['exp_clock', 'trial_clock',  'trial', 'stim_id', 'event', 'value']
resp_data = []

exp_clock = None
trial_clock = None
trial_nr = 0
stim_id = 0

visual_stimuli = {}
sound_stimuli = {}


def increase_trial(id):
    global trial_nr, stim_id
    trial_nr = trial_nr + 1
    stim_id = id
    trial_clock.reset()

def log_append(event, value):
    combined = dict(
        zip(log_fields,
            [exp_clock.getTime(), trial_clock.getTime(), trial_nr, stim_id, event,
             value]))
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