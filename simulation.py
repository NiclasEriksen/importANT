from main import logger  # Needed for logging
# Importing the logic needed to simulate ants and their environment
from environment import Environment
from ant import WorkerAnt


class Simulation:

    def __init__(self, window=None):
        logger.debug("Simulation class __init__")
        if window:
            self.window = window
        else:
            logger.warning("No window specified, running headless.")

        logger.info("Starting simulation.")
        self.start()


    def start(self, w=200, h=150):
        logger.info("Initializing environment.")
        self.environment = Environment()
        logger.debug("Generating environment grid.")
        self.environment.generate_grid(w, h)