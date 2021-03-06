from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class Slider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value_changed_by_user = False

    # def mouseReleaseEvent(self, event):
    #     super(Slider, self).mouseReleaseEvent(event)
    #     self.value_changed_by_user = False

    def mousePressEvent(self, event):
        super(Slider, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            val = self.pixelPosToRangeValue(event.pos())
            # print('triggering action')
            self.setValue(val)          
            self.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepAdd)
            # self.triggerAction(QAbstractSlider.SliderAction.SliderNoAction)
            # print('value set to',val)

    def keyPressEvent(self, event):
        # print('key pressed')
        if event.key() == Qt.Key_Left:
            self.triggerAction(QAbstractSlider.SliderAction.SliderPageStepSub)
            self.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepAdd) # TBD This is a strange solution, but it works
            # self.value_changed_by_user = True
            # print(self.sliderPosition())
        elif event.key() == Qt.Key_Right:
            self.triggerAction(QAbstractSlider.SliderAction.SliderPageStepAdd)
            self.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepAdd)
            # self.value_changed_by_user = True
            # print(self.sliderPosition())

    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                               sliderMax - sliderMin, opt.upsideDown)