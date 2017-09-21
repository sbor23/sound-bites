from __future__ import division

import math

from psychopy.tools.attributetools import attributeSetter
from psychopy import logging


class Spacer:

    def __init__(self, size):
        self.width = size
        self.height = size
        self.pos = (0, 0)


class Layout:
    pass


class BoxLayout(Layout):
    HORIZONTAL = 1
    VERTICAL = 2

    def __init__(self, orientation=HORIZONTAL, pos=(0, 0), width=None, height=None):
        self.items = []
        self.prop = []

        self.__dict__['orientation'] = orientation
        self.__dict__['pos'] = pos
        self._width = width
        self._height = height

    def add(self, item, proportion=0):
        self.items.append(item)
        self.prop.append(proportion)

    def addSpacer(self, size, proportion=0):
        self.items.append(Spacer(size))
        self.prop.append(proportion)

    @attributeSetter
    def pos(self, x, y=None):
        self.__dict__['pos'] = (x, y) if y is None else x

    @attributeSetter
    def width(self, w):
        self._width = w

    @attributeSetter
    def height(self, h):
        self._height = h

    @attributeSetter
    def orientation(self, ori):
        self.__dict__['orientation'] = ori

    def layout(self):
        # TODO: this should be more like CalcMin from wxWidgets
        for item in self.items:
            if isinstance(item, Layout):
                item.layout()

        majorSizes = []
        totalMajor = 0
        if self.orientation == BoxLayout.HORIZONTAL:
            majorSizes = [i.width for i in self.items]
            totalMajor = sum(majorSizes)
            if self._width is not None and self._width > totalMajor:
                totalMajor = self._width
                logging.warning('Minimum width exceeds desired width: %d > %d' % (
                    totalMajor, self._width))
            self.width = totalMajor

            maxMinor = max([i.height for i in self.items])
            if self.height is None:
                self.height = maxMinor
            elif maxMinor > self.height:
                logging.warning('Height of child items exceed height of layout: %d > %d' % (
                    maxMinor, self.height))
            self.height = maxMinor
        elif self.orientation == BoxLayout.VERTICAL:
            majorSizes = [i.height for i in self.items]

            totalMajor = sum(majorSizes)
            if self._height is not None and self._height > totalMajor:
                totalMajor = self._height
                logging.warning('Minimum height exceeds desired height: %d > %d' % (
                    totalMajor, self._height))
            self.height = totalMajor

            maxMinor = max([i.width for i in self.items])
            if self.width is None:
                self.width = maxMinor
            elif maxMinor > self.width:
                logging.warning(
                    'Width of child items exceed width of layout: %d > %d' % (maxMinor, self.width))
            self.width = maxMinor
        else:
            raise NotImplementedError(
                'Only HORIZONTAL and VERTICAL orientations supported')

        # give minimum space to all
        sizes = majorSizes

        # distribute remaining space
        remaining = totalMajor - sum(sizes)
        totalProp = sum(self.prop)
        if totalProp > 0:
            for i in range(len(sizes)):
                sizes[i] += (self.prop[i] / totalProp) * remaining

        if self.orientation == BoxLayout.HORIZONTAL:
            left = self.pos[0] - sum(sizes) / 2
            for i, item in enumerate(self.items):
                left += sizes[i] / 2
                item.pos = (left, self.pos[1])
                left += sizes[i] / 2
        elif self.orientation == BoxLayout.VERTICAL:
            top = self.pos[1] + sum(sizes) / 2
            for i, item in enumerate(self.items):
                top -= sizes[i] / 2
                item.pos = (self.pos[0], top)
                top -= sizes[i] / 2
        else:
            raise NotImplementedError(
                'Only HORIZONTAL and VERTICAL orientations supported')

        # layout children
        for item in self.items:
            if isinstance(item, Layout):
                item.layout()


class GridLayout(Layout):

    def __init__(self, pos=(0, 0), rows=1, cols=0, vgap=0, hgap=0):
        self.__dict__['pos'] = pos
        self.__dict__['rows'] = rows
        self.__dict__['cols'] = cols
        self.__dict__['vgap'] = vgap
        self.__dict__['hgap'] = hgap
        self.items = []

    def add(self, item):
        self.items.append(item)

    def layout(self):
        # TODO: this should be more like CalcMin from wxWidgets
        for item in self.items:
            if isinstance(item, Layout):
                item.layout()

        rows = self.rows
        cols = self.cols
        assert rows or cols
        if rows == 0:
            rows = int(math.ceil(len(self.items) / cols))
        elif cols == 0:
            cols = int(math.ceil(len(self.items) / rows))
        assert rows * cols >= len(self.items)

        maxHeights = []
        for r in range(rows):
            items = self.items[r * cols:r * cols + cols]
            maxHeight = max([i.height for i in items])
            maxHeights.append(maxHeight)

            # TODO: only change height if desired
            for i in items:
                i.height = maxHeight

        maxWidths = []
        for c in range(cols):
            items = self.items[c::cols]
            maxWidth = max([i.width for i in items])
            maxWidths.append(maxWidth)

            # TODO: only change width if desired
            for i in items:
                i.width = maxWidth

        totalWidth = sum(maxWidths) + self.hgap * (cols - 1)
        totalHeight = sum(maxHeights) + self.vgap * (cols - 1)
        y = self.pos[1] + totalHeight / 2
        for row in range(rows):
            y -= maxHeights[row] / 2
            # FIXME: if x is 0, button isn't shown, so add eps for now
            x = self.pos[0] - totalWidth / 2 + 0.1
            for col in range(cols):
                x += maxWidths[col] / 2
                item = self.items[row * cols + col]
                item.setPos([x, y])
                x += maxWidths[col] / 2 + self.hgap
            y -= maxHeights[row] / 2 + self.vgap

        self.width = totalWidth
        self.height = totalHeight

        # layout children
        for item in self.items:
            if isinstance(item, Layout):
                item.layout()

if __name__ == "__main__":
    from psychopy import core, event, iohub, visual
    from button import Button, ButtonGrid

    win = visual.Window([800, 600], units='pix')

    vbox = BoxLayout(orientation=BoxLayout.VERTICAL)

    imlayout = BoxLayout(orientation=BoxLayout.HORIZONTAL)
    btn = Button(win, 'Image 1 here', width=320, height=240, autoDraw=True)
    imlayout.add(btn)
    imlayout.addSpacer(50)
    btn = Button(win, 'Image 2 here', width=320, height=240, autoDraw=True)
    imlayout.add(btn)

    vbox.add(imlayout)
    vbox.addSpacer(50)

    buttonGrid = ButtonGrid(win, [str(x) for x in range(12)], rows=0, cols=4)
    vbox.add(buttonGrid)

    # this will layout children
    vbox.layout()

    trialClock = core.Clock()
    while trialClock.getTime() < 20:
        for keys in event.getKeys(timeStamped=True):
            if keys[0]in ['escape', 'q']:
                win.close()
                core.quit()

        win.flip()
