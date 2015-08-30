from ant import WorkerAnt


class Environment:

    def __init__(self):
        self.base = (0, 0)
        self.food_sources = []
        self.ants = []
        self.tiles = []
        self.time = 0
        self.selection_age_treshold = 5     # Age ant has to be to be judged

    def generate_grid(self, w, h):
        self.tiles = [[0 for x in range(h)] for x in range(w)]
        iw, ih = 0, 0
        while ih < h:
            while iw < w:
                self.create_tile(iw, ih)
                iw += 1
            iw = 0
            ih += 1

    def create_tile(self, x, y):
        tile = Tile(x, y)
        self.tiles[x][y] = tile

    def create_ant(self, mother=None, father=None):
        ant = WorkerAnt(mother, father, self)
        self.ants.append(ant)

    def remove_ant(self, ant):
        try:
            self.ants.remove(ant)
        except ValueError:
            return False

        return True

    def natural_selection(self):
        ants = self.get_eligible_ants(self.ants)
        try:
            mother, father = self.get_best_parents(ants)
        except TypeError:
            return False

        self.create_ant(mother, father)
        # print ants[0].alpha, ants[1].alpha, a.alpha

    def get_eligible_ants(self, ants):
        # Create a list of ants old enough to be judged
        eligible_ants = []
        for a in ants:
            if a.age >= self.selection_age_treshold:
                eligible_ants.append(a)

        return eligible_ants

    def get_best_parents(self, ants):
        if len(ants) >= 2:
            ants = sorted(
                ants,
                key=lambda x: x.food_count,
                reverse=True
            )
            return ants[0], ants[1]
        else:
            return None

    def check_if_occupied(self, tile):
        for a in self.ants:
            if a.coordinates == tile.coordinate:
                return True
        else:
            return False

    def update_state(self):
        self.time += 1
        if not self.time % 1000:
            self.natural_selection()

    def restart(self):
        self.__init__()


class Tile:

    def __init__(self, x, y, tiletype="default"):
        self.home_pheromone = 0
        self.food_pheromone = 0
        self.coordinate = (x, y)
        self.tiletype = tiletype

    def set_type(self, newtype):
        self.tiletype = newtype
