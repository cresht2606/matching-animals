from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
import pygame
import sys

class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super(PygameWidget, self).__init__(parent)
        self.setFixedSize(960, 640)

        pygame.init()
        self.screen = pygame.display.set_mode((960, 640))
        self.clock = pygame.time.Clock()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)

    def tick(self):
        self.handle_events()
        self.screen.fill((255, 255, 255))
        # TODO: Draw tiles, UI elements here
        pygame.display.flip()
        self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


