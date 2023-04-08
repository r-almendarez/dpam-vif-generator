######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QProgressBar


class Worker(QObject):
    action = Signal(QProgressBar)
    finished = Signal()

    @Slot()
    def run(self, progress: QProgressBar = None):
        self.action.emit(progress)
        self.finished.emit()
