#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''Creates a buttonff of given width and height
as a special case of a :class:`~psychopy.visual.ShapeStim`'''

# Part of the PsychoPy library
# Copyright (C) 2014 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

import numpy as np

import psychopy  # so we can get the __path__
from psychopy import logging
from psychopy.tools.attributetools import attributeSetter, logAttrib
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.helpers import setColor
from psychopy.visual.rect import Rect
from psychopy.visual.text import TextStim

from layout import GridLayout


class ButtonStyle:

    def __init__(self, fillColor='Gray', borderColor='Black',
                 textColor='Black'):
        self.fillColor = fillColor
        self.borderColor = borderColor
        self.textColor = textColor

    @attributeSetter
    def fillColor(self, color):
        """
        Sets the color of the button fill. See :meth:`psychopy.visual.GratingStim.color`
        for further details of how to use colors.
        """
        setColor(self, color, rgbAttrib='fillRGB', colorAttrib='fillColor')

    @attributeSetter
    def borderColor(self, color):
        """
        Sets the color of the button border. See :meth:`psychopy.visual.GratingStim.color`
        for further details of how to use colors.
        """
        setColor(self, color, rgbAttrib='borderRGB', colorAttrib='borderColor')

    @attributeSetter
    def textColor(self, color):
        """
        Sets the color of the button text. See :meth:`psychopy.visual.GratingStim.color`
        for further details of how to use colors.
        """
        setColor(self, color, rgbAttrib='textRGB', colorAttrib='textColor')


class Button(BaseVisualStim):

    """Creates a button of given width and height, by combining a
    TextStim and a Rect

    (New in version 1.80.99 FIXME)
    """

    def __init__(self, win,
                 text='Hello World',
                 pos=(0.0, 0.0),
                 width=None,
                 height=None,
                 padx=2,
                 pady=2,
                 units="",
                 checked=False,
                 name=None,
                 autoLog=None,
                 autoDraw=False,
                 ):
        """
        Button accepts all input parameters, that
        `~psychopy.visual.BaseVisualStim` accept, except for vertices
        and closeShape.

        :Parameters:

            width : int or float
                Width of the Rectangle (in its respective units, if specified)

            height : int or float
                Height of the Rectangle (in its respective units, if specified)

        """
        # what local vars are defined (these are the init params) for use by
        # __repr__
        self._initParams = dir()
        self._initParams.remove('self')

        super(Button, self).__init__(
            win, units=units, name=name, autoLog=False)

        self.__dict__['pos'] = pos
        self.__dict__['text'] = text

        self.textStim = TextStim(win, text=text, pos=self.pos, wrapWidth=width,
                                 color='Black', units=units, autoLog=autoLog)

        # TODO: expose content_width via TextStim
        autoWidth = (self.textStim._pygletTextObj._layout.content_width +
                     2 * padx)
        autoHeight = self.textStim.height + 2 * pady

        if width is not None and width > autoWidth:
            self.__dict__['width'] = width
        else:
            self.__dict__['width'] = autoWidth

        if height is not None and height > autoHeight:
            self.__dict__['height'] = height
        else:
            self.__dict__['height'] = autoHeight

        self.rectStim = Rect(
            win, pos=self.pos, width=self.width, height=self.height, units=units, autoLog=autoLog)

        self.normalStyle = ButtonStyle()
        self.checkedStyle = ButtonStyle(
            fillColor='#FF8040', borderColor='Black', textColor='Black')

        self.checked = checked  # this will set style

        self.autoDraw = autoDraw

        self.__dict__['autoLog'] = (autoLog or
                                    autoLog is None and self.win.autoLog)
        if self.autoLog:
            logging.exp("Created %s = %s" % (self.name, str(self)))

    def _setStyle(self, style):
        self.rectStim.lineColor = style.borderColor
        self.rectStim.fillColor = style.fillColor
        self.textStim.color = style.textColor

    @attributeSetter
    def text(self, value):
        """Changes the text of the Button"""
        self.__dict__['text'] = value
        # TODO: change this to attributeSetters with 1.80.99
        self.textStim.setText(value)

    @attributeSetter
    def pos(self, value):
        """Changes the position of the Button"""
        self.__dict__['pos'] = value
        self.rectStim.pos = value
        self.textStim.pos = value

    @attributeSetter
    def width(self, value):
        """Changes the width of the Button"""
        self.__dict__['width'] = value
        # TODO: change this to attributeSetters with 1.80.99
        self.rectStim.setWidth(value)
        # this won't work, need to construct new or wait for 1.80.99
        self.textStim.wrapWidth = value

    @attributeSetter
    def height(self, value):
        """Changes the height of the Button"""
        self.__dict__['height'] = value
        # TODO: change this to attributeSetters with 1.80.99
        self.rectStim.setHeight(value)

        # don't set height of text as it will change font size
        # self.textStim.setHeight(value)

    # @attributeSetter
    def checked(self, value):
        self.__dict__['checked'] = value
        if self.checked:
            self._setStyle(self.checkedStyle)
        else:
            self._setStyle(self.normalStyle)

    def setColor(self, color, colorSpace=None, operation=''):
        """For Button use :meth:`~Button.fillColor` or
        :meth:`~Button.borderColor` or :meth:`~Button.textColor`
        """
        raise AttributeError('Button does not support setColor method.'
                             'Please use fillColor, borderColor, or textColor')

    def contains(self, x, y=None, units=None):
        return self.rectStim.contains(x, y, units)

    def draw(self, win=None):
        """
        Draw the stimulus in its relevant window. You must call
        this method after every MyWin.flip() if you want the
        stimulus to appear on that frame and then update the screen
        again.

        If win is specified then override the normal window of this stimulus.
        """
        if win is None:
            win = self.win

        self.rectStim.draw(win)
        self.textStim.draw(win)



if __name__ == "__main__":
    from psychopy import core, event, iohub, visual

    io = iohub.launchHubServer()

    myWin = visual.Window([400, 400], units='pix')

    button = Button(myWin, "Test Button", pos=[0, 100])
    buttonGrid = ButtonGrid(myWin, [str(x) for x in range(12)], rows=0, cols=4)

    trialClock = core.Clock()
    while trialClock.getTime() < 20:

        for evt in io.devices.mouse.getEvents():
            pos = (evt.x_position, evt.y_position)
            if evt.type == iohub.constants.EventConstants.MOUSE_BUTTON_PRESS:
                buttonGrid.click(pos)

        for keys in event.getKeys(timeStamped=True):
            if keys[0]in ['escape', 'q']:
                myWin.close()
                io.quit()
                core.quit()

        button.draw()
        buttonGrid.draw()
        myWin.flip()
