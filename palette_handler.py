
import random
import math

from win32com import client

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class PaletteHandler(object):

    BRUSH_RADIUS = 10.0
    BRUSH_DECAY = 0.88

    pressed_mouse_buttons = []

    stage = None
    target_view = None

    # reset every mouse release
    painting_items = []
    paint_intense = 0.0
    last_pos = (0, 0)

    def __init__(self, target_view):
        self.palette_view = target_view

        self.stage = QtWidgets.QGraphicsScene()
        self.palette_view.setScene(self.stage)
        self.palette_view.mousePressEvent = self.mouse_press
        self.palette_view.mouseMoveEvent = self.mouse_move
        self.palette_view.mouseReleaseEvent = self.mouse_release
        self.palette_view.tabletEvent = self.tablet_event

    def paint_color(self, pos, color=None):
        """
        TODO: blurry brush
        """

        radius = self.BRUSH_RADIUS

        color = self.get_ps_foreground_color()
        color.setAlpha(self.paint_intense * 255)
        brush = QtGui.QBrush(color)

        lx = self.last_pos.x()
        ly = self.last_pos.y()
        cx = pos.x()
        cy = pos.y()
        dx = cx - lx
        dy = cy - ly
        count = 2 + int((abs(dx) + abs(dy)) * 0.1)

        for i in range(count):
            prog = float(i) / count

            tx = lx + dx * prog
            ty = ly + dy * prog

            rect = QtCore.QRectF(
                tx - radius,
                ty - radius,
                radius * 2.0,
                radius * 2.0
            )
            self.painting_items.append(
                self.stage.addEllipse(
                    rect,
                    pen=QtGui.QPen(brush, 0.0),
                    brush=brush
                )
            )

    def static_stage(self):
        self.stage.setSceneRect(
            0.0, 0.0,
            self.palette_view.width(),
            self.palette_view.height()
        )

    def get_ps_foreground_color(self) -> QtGui.QColor:
        try:
            psapp = client.Dispatch("Photoshop.Application").Application
            r = psapp.foregroundColor.rgb.red
            g = psapp.foregroundColor.rgb.green
            b = psapp.foregroundColor.rgb.blue
            return QtGui.QColor(r, g, b)
        except:
            return QtGui.QColor(0, 0, 0)

    def set_ps_foreground_color(self, color):
        try:
            new_color = client.Dispatch("Photoshop.SolidColor")
            new_color.rgb.red = color.red()
            new_color.rgb.green = color.green()
            new_color.rgb.blue = color.blue()
            psapp = client.Dispatch("Photoshop.Application").Application
            psapp.foregroundColor = new_color
        except Exception as e:
            print(e)

    def get_stage_color(self, pos, radius=1) -> QtGui.QColor:
        stage_image = self.palette_view.grab()

        r_sum = 128
        g_sum = 128
        b_sum = 128
        MONTE_CARLO_COUNT = 25
        for _ in range(MONTE_CARLO_COUNT):
            angle = random.random() * math.pi * 2.0
            dist = random.random() * radius

            offset_applied_pos = QtCore.QPoint(
                pos.x() + math.cos(angle) * dist,
                pos.y() + math.cos(angle) * dist
            )

            stage_img = stage_image.toImage()
            if not stage_img.valid(offset_applied_pos):
                continue

            pixel_color = stage_img.pixelColor(offset_applied_pos)
            r_sum += pixel_color.red()
            g_sum += pixel_color.green()
            b_sum += pixel_color.blue()

        r = r_sum / MONTE_CARLO_COUNT
        g = g_sum / MONTE_CARLO_COUNT
        b = b_sum / MONTE_CARLO_COUNT

        r = min(max(r, 0), 255)
        g = min(max(g, 0), 255)
        b = min(max(b, 0), 255)

        return QtGui.QColor(r, g, b)

    def mouse_press(self, e=None):
        self.pressed_mouse_buttons.append(e.button())
        self.painting_items = []

        if QtCore.Qt.LeftButton in self.pressed_mouse_buttons:
            pos = e.pos()
            self.last_pos = pos
            self.paint_color(pos)
            self.static_stage()

        if QtCore.Qt.RightButton in self.pressed_mouse_buttons:
            self.set_ps_foreground_color(self.get_stage_color(e.pos()))

    def mouse_release(self, e=None):
        if QtCore.Qt.RightButton in self.pressed_mouse_buttons:
            self.set_ps_foreground_color(self.get_stage_color(e.pos()))

        if e.button() in self.pressed_mouse_buttons:
            self.pressed_mouse_buttons.remove(e.button())

        # flatten view as bitmap
        image = self.palette_view.grab()
        for item in self.painting_items:
            self.stage.removeItem(item)
        flattened_img = self.stage.addPixmap(image)
        flattened_img.setPos(-1, -1)

    def mouse_move(self, e=None):
        pos = e.pos()
        if QtCore.Qt.LeftButton in self.pressed_mouse_buttons:
            self.paint_color(pos)
            self.static_stage()
            self.last_pos = pos

        if QtCore.Qt.RightButton in self.pressed_mouse_buttons:
            self.set_ps_foreground_color(self.get_stage_color(e.pos()))

    def tablet_event(self, e=None):
        self.paint_intense = e.pressure()
