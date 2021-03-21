from PyQt5 import QtWidgets, QtCore

class MyCombox(QtWidgets.QComboBox):
    enter_event_signal = QtCore.pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.enter_event_signal.emit()
