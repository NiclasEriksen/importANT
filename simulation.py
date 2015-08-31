from main import logger  # Needed for logging
# Importing the logic needed to simulate ants and their environment
import environment as env
import ant


class Simulation:

    def __init__(self, window=None):
        logger.debug("Simulation class __init__")
        if window:
            self.window = window
        else:
            self.window = window
            logger.warning("No window specified, running headless.")

        self.time = 0

        # self.start()

    def start(self, w=200, h=150):
        logger.info("Starting simulation.")
        logger.info("Initializing environment.")
        self.environment = env.Environment()
        logger.debug("Generating environment grid.")
        self.environment.generate_grid(w, h)
        # for i in range(10):
        #     self.environment.create_ant()
        self.render()

    def increment(self):
        logger.debug("Incrementing simulation, frame {0}".format(self.time))
        self.environment.update_state()
        self.time += 1

    def render(self):
        pass
        # for a in self.environment.ants:

