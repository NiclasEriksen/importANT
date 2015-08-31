"""
This is a simulated ant colony, in which we generate an environment for agents
to roam in, gather food, grow and expand.
"""

# Modules needed to run the simulation
import pyglet
import logging

# Global variables
VSYNC = True
FPS = 60

# Pyglet initialization, gathering information about the system
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()
# Limit the frames per second to 60 and initialize fps display
pyglet.clock.set_fps_limit(FPS)
fps_display = pyglet.clock.ClockDisplay()

# Logging
logging.basicConfig(
    filename='debug.log',
    filemode='w',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

# Importing simulation module, needs to be after logging setup
import simulation


class Window(pyglet.window.Window):

    def __init__(self):
        # Template for multisampling
        gl_template = pyglet.gl.Config(
            sample_buffers=1,
            samples=2,
            alpha_size=8
        )
        try:  # to enable multisampling
            gl_config = screen.get_best_config(gl_template)
            logger.debug("Multisampling enabled.")
        except pyglet.window.NoSuchConfigException:
            gl_template = pyglet.gl.Config(alpha_size=8)
            gl_config = screen.get_best_config(gl_template)
            logger.debug("No multisampling.")
        # Create OpenGL context #
        gl_context = gl_config.create_context(None)
        super(Window, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=True,
            vsync=VSYNC
        )

        self.simulation = None

    def on_key_press(self, symbol, modifiers):
        k = pyglet.window.key
        if self.simulation:
            if symbol == k.ENTER:
                self.simulation.start()
            if symbol == k.NUM_ADD:
                self.simulation.increment()
            if symbol == k.A:
                self.simulation.environment.create_ant()
        if symbol == k.ESCAPE:
            pyglet.app.exit()

    def render(self, dt):
        self.clear()
        if self.simulation:
            self.simulation.render()


# Running application
if __name__ == "__main__":
    logger.info("Spawning main window.")
    w = Window()
    logger.debug("Scheduling render function on main window")
    pyglet.clock.schedule_interval(w.render, 1.0 / FPS)
    logger.info("Initializing simulation.")
    s = simulation.Simulation(w)
    w.simulation = s
    logger.info("Running app...")
    pyglet.app.run()
