import pygame as pg
from view import View
from chess import Chess
from controller import Controller


class App:
    """
        App - main application class
    """

    def __init__(self):
        self._running = True
        self._display_surf = None
        self._controller = Controller()

    def on_init(self):
        pg.init()
        self._display_surf = pg.display.set_mode(
            self._controller.view.size, pg.HWSURFACE | pg.DOUBLEBUF
        )
        self._controller.on_init()  # must be called after display.set_mode()
        self._running = True

    def on_event(self, event):
        if event.type == pg.QUIT:
            self._running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            # set a piece to be dragged using dragging field in View
            self._controller.select()
        elif event.type == pg.MOUSEMOTION:
            # update any currently dragged mImages
            self._controller.drag()
        elif event.type == pg.MOUSEBUTTONUP:
            # reset dragging field in View
            self._controller.drop()

    def on_loop(self):
        pass

    def on_render(self):
        self._display_surf.blit(self._controller.getSurface(), (0, 0))
        pg.display.update()

    def on_cleanup(self):
        pg.quit()

    def on_execute(self):
        self.on_init()
        while self._running:
            for event in pg.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
