import random

class WorkerAnt:

    """The main worker ant constructor, also acts as migrant constructor."""

    def __init__(self, father=None, mother=None, env=False):
        # Set random genetic properties
        self.env = env
        if mother and father:
            self.crossover(mother, father)
        else:
            self.alpha = random.uniform(-5, 5)  # Pheromone sensibility
            self.beta = random.uniform(-5, 5)   # ?
            self.gamma = random.uniform(-5, 5)  # ?
        self.base_pheromone = 10
        self.age = random.randrange(0, 10)
        self.visited = set()                # Set of visited tiles
        self.searching = False
        self.have_food = False
        self.food = None
        self.food_count = 0
        self.hunger = 0
        self.hunger_max = 1000
        self.hunger_turn_treshold = self.hunger_max / 2
        self.direction = (1, 0)
        self.coordinates = (0, 0)
        self.random_chance = 20
        self.random_chance = 100 / self.random_chance

    def crossover(self, m, f):
        if random.getrandbits(1):
            a = m.alpha
        else:
            a = f.alpha
        if random.getrandbits(1):
            b = m.beta
        else:
            b = f.beta
        if random.getrandbits(1):
            g = m.gamma
        else:
            g = f.gamma

        self.alpha, self.beta, self.gamma = a, b, g

    def mutate(self):
        choice = random.randint(0, 2)
        if choice == 0:
            self.alpha = random.uniform(-5, 5)  # Pheromone sensibility
        elif choice == 1:
            self.beta = random.uniform(-5, 5)   # ?
        elif choice == 2:
            self.gamma = random.uniform(-5, 5)  # ?

    def search_home(self, random_choice=True):
        if random_choice:
            success = self.make_decision()
            if not success:
                self.move_pheromone_tile("home")
        else:
            self.move_pheromone_tile("home")

    def search_food(self, random_choice=True):
        if random_choice:
            success = self.make_decision()
            if not success:
                self.move_pheromone_tile("food")
        else:
            self.move_pheromone_tile("food")

    def make_decision(self):
        choice = random.randrange(0, self.random_chance)
        if not choice:
            if random.randint(0, 1):
                self.turn_left()
                self.move_forward()
            else:
                self.turn_right()
                self.move_forward()

            return True

        else:
            return False

    def move_pheromone_tile(self, target):
        walkable = self.check_neighbors()
        target_tile = self.get_pheromone_tile(walkable, target=target)
        self.coordinates = target_tile.coordinate

    def get_pheromone_tile(self, tiles, target):
        if target == "food":
            sorted_tiles = sorted(
                tiles,
                key=lambda x: x.food_pheromone,
                reverse=True
            )
        elif target == "home":
            sorted_tiles = sorted(
                tiles,
                key=lambda x: x.home_pheromone,
                reverse=True
            )
        else:
            raise IndexError("No target by that name.")
            return False

        return sorted_tiles[0]

    def check_neighbors(self):
        ant_x, ant_y = self.coordinates[0], self.coordinates[1]
        dir_x, dir_y = self.direction[0], self.direction[1]
        if dir_y == 0:
            if dir_x == 1:
                dir_lx, dir_rx = 1, 1
                dir_ly, dir_ry = -1, 1
            elif dir_x == -1:
                dir_lx, dir_rx = -1, -1
                dir_ly, dir_ry = 1, -1
        elif dir_y == 1:
            if dir_x == 1:
                dir_lx, dir_rx = 1, 0
                dir_ly, dir_ry = 0, 1
            elif dir_x == 0:
                dir_lx, dir_rx = 1, -1
                dir_ly, dir_ry = 1, 1
            elif dir_x == -1:
                dir_lx, dir_rx = 0, -1
                dir_ly, dir_ry = 1, 0
        elif dir_y == -1:
            if dir_x == 1:
                dir_lx, dir_rx = 0, 1
                dir_ly, dir_ry = -1, 0
            elif dir_x == 0:
                dir_lx, dir_rx = -1, 1
                dir_ly, dir_ry = -1, -1
            elif dir_x == -1:
                dir_lx, dir_rx = -1, 0
                dir_ly, dir_ry = 0, -1

        # result = [
        #     t for t in self.env.tiles if
        #     t.coordinate == (ant_x + dir_x, ant_y + dir_y) or
        #     t.coordinate == (ant_x + dir_lx, ant_y + dir_ly) or
        #     t.coordinate == (ant_x + dir_rx, ant_y + dir_ry)
        # ]
        result = []
        try:
            result.append(self.env.tiles[ant_x + dir_x][ant_y + dir_y])
        except IndexError:
            pass
        try:
            result.append(self.env.tiles[ant_x + dir_lx][ant_y + dir_ly])
        except IndexError:
            pass
        try:
            result.append(self.env.tiles[ant_x + dir_rx][ant_y + dir_ry])
        except IndexError:
            pass
        for t in result:
            if not t.tiletype == "default":
                result.remove(t)
        return result

    def move_forward(self):
        new_pos = (
            self.coordinates[0] + self.direction[0],
            self.coordinates[1] + self.direction[1]
        )
        self.coordinates = new_pos

    def get_dir_left(self, direction):
        dir_x, dir_y = direction
        if dir_x == 1 and dir_y == 1:
            return (1, 0)
        elif dir_x == 1 and not dir_y:
            return (1, -1)
        elif dir_x == 1 and dir_y == -1:
            return (0, -1)
        elif not dir_x and dir_y == -1:
            return (-1, -1)
        elif dir_x == -1 and dir_y == -1:
            return (-1, 0)
        elif dir_x == -1 and not dir_y:
            return (-1, 1)
        elif dir_x == -1 and dir_y == 1:
            return (0, 1)
        elif dir_x == 0 and dir_y == 1:
            return (1, 1)
        else:
            return direction

    def get_dir_right(self, direction):
        dir_x, dir_y = direction
        if dir_x == 1 and dir_y == 1:
            return (0, 1)
        elif dir_x == 1 and not dir_y:
            return (1, 1)
        elif dir_x == 1 and dir_y == -1:
            return (1, 0)
        elif not dir_x and dir_y == -1:
            return (1, -1)
        elif dir_x == -1 and dir_y == -1:
            return (0, -1)
        elif dir_x == -1 and not dir_y:
            return (-1, -1)
        elif dir_x == -1 and dir_y == 1:
            return (-1, 0)
        elif dir_x == 0 and dir_y == 1:
            return (-1, 1)
        else:
            return direction

    def turn_left(self):
        self.direction = self.get_dir_left(self.direction)

    def turn_right(self):
        self.direction = self.get_dir_right(self.direction)

    def update_hunger(self):
        if self.hunger < self.hunger_max:
            self.hunger += 1
        else:
            self.kill()

        # Ants that're beginning to starve will abandon search and head home.
        if self.hunger >= self.hunger_turn_treshold:
            self.searching = False

    def kill(self):
        if self.env:
            self.env.remove_ant(self)

    def pick_up_food(self):
        self.have_food = True
        self.food = 1

    def deposit_food(self):
        self.have_food = False
        self.food = 0

    def lay_pheromone(self):
        for t in self.visited:
            if self.searching:
                t.food_pheromone += self.base_pheromone
            else:
                t.home_pheromone += self.base_pheromone
        self.visited = set()

    def update_pos(self):
        pass

    def update_state(self):
        self.update_hunger()
        self.age += 1
