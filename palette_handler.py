
from win32com import client

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class PaletteHandler(object):

    stage = None
    target_view = None

    def __init__(self, target_view):
        self.palette_view = target_view

        self.stage = QtWidgets.QGraphicsScene()
        self.palette_view.setScene(self.stage)
        self.palette_view.mousePressEvent = self.mouse_press_event
        self.palette_view.tabletEvent = self.tablet_event

    def get_ps_foreground_color(self):
        try:
            psapp = client.Dispatch("Photoshop.Application").Application
            foreground_color = psapp.ForegroundColor
            print(foreground_color)
            return foreground_color
        except:
            return None

    def mouse_press_event(self, e=None):
        position = e.scenePos()
        button = e.button()
        if button == QtCore.Qt.RightButton:
            radius = 25.0
            rect = QtCore.QRectF(
                position.x() - radius,
                position.y() - radius,
                radius * 2.0,
                radius * 2.0
            )

            color = self.get_ps_foreground_color()
            print(color)

            self.stage.addEllipse(
                rect,
                pen=QtGui.QPen(),
                brush=QtGui.QBrush()
            )
        elif button == QtCore.Qt.LeftButton:
            print("LLL")

        print(position)

    def tablet_event(self, e=None):
        print(e)
