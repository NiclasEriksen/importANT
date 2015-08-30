import unittest

import ant
import environment

tcase = unittest.TestCase


class TestCreateEnvironment(tcase):

    def test_create_env(self):
        env = environment.Environment()
        self.assertIsInstance(env, environment.Environment)

    def test_env_grid(self):
        env = environment.Environment()
        env.generate_grid(10, 10)
        self.assertEqual(len(env.tiles[0]), 10)
        self.assertEqual(len(env.tiles), 10)
        for ty in range(10):
            for tx in range(10):
                self.assertIsInstance(env.tiles[tx][ty], environment.Tile)

    def test_create_tile(self):
        env = environment.Environment()
        env.generate_grid(1, 1)
        # env.create_tile(0, 0)
        self.assertEqual(len(env.tiles), 1)

    def test_env_attributes(self):
        env = environment.Environment()
        self.assertTrue(hasattr(env, "base"))
        self.assertTrue(hasattr(env, "food_sources"))
        self.assertTrue(hasattr(env, "ants"))
        self.assertTrue(hasattr(env, "time"))
        self.assertTrue(hasattr(env, "tiles"))
        self.assertTrue(hasattr(env, "selection_age_treshold"))

    def test_create_initial_ant(self):
        env = environment.Environment()
        env.create_ant()
        self.assertIsNotNone(env.ants[0])

    def test_create_crossover_ant(self):
        env = environment.Environment()
        env.create_ant()
        env.create_ant()
        env.create_ant(env.ants[0], env.ants[1])
        self.assertIsInstance(env.ants[2], ant.WorkerAnt)

    def test_remove_ant(self):
        env = environment.Environment()
        env.create_ant()
        env.remove_ant(env.ants[0])
        self.assertFalse(env.remove_ant(ant.WorkerAnt()))
        self.assertEqual(len(env.ants), 0)

    def test_update_state(self):
        env = environment.Environment()
        oldtime = env.time
        env.update_state()
        self.assertEqual(env.time, oldtime + 1)

    def test_get_tile_by_coord(self):
        env = environment.Environment()
        env.generate_grid(5, 5)

        tile = env.tiles[1][1]
        self.assertIsInstance(tile, environment.Tile)
        self.assertEqual(tile.coordinate, (1, 1))
        with self.assertRaises(IndexError):
            env.tiles[5][5]

    def test_restart_environment(self):
        env = environment.Environment()
        env.create_ant()
        env.generate_grid(1, 1)
        env.update_state()
        env.restart()

        self.assertEqual(len(env.ants), 0)
        self.assertEqual(env.time, 0)
        self.assertEqual(len(env.tiles), 0)


class TestCreateAnt(tcase):

    def test_ant_attributes(self):
        a = ant.WorkerAnt()
        self.assertTrue(hasattr(a, "base_pheromone"))
        self.assertTrue(hasattr(a, "coordinates"))
        self.assertTrue(hasattr(a, "env"))
        self.assertTrue(hasattr(a, "direction"))
        self.assertTrue(hasattr(a, "alpha"))
        self.assertTrue(hasattr(a, "beta"))
        self.assertTrue(hasattr(a, "gamma"))
        self.assertTrue(hasattr(a, "age"))
        self.assertTrue(hasattr(a, "visited"))
        self.assertTrue(hasattr(a, "searching"))
        self.assertTrue(hasattr(a, "have_food"))
        self.assertTrue(hasattr(a, "food"))
        self.assertTrue(hasattr(a, "food_count"))
        self.assertTrue(hasattr(a, "hunger"))
        self.assertTrue(hasattr(a, "hunger_max"))
        self.assertTrue(hasattr(a, "hunger_turn_treshold"))

    def test_migrant_genetics(self):
        a = ant.WorkerAnt()
        self.assertTrue(a.alpha <= 5.0 and a.alpha >= -5.0)
        self.assertTrue(a.beta <= 5.0 and a.beta >= -5.0)
        self.assertTrue(a.gamma <= 5.0 and a.gamma >= -5.0)

    def test_children_genetics(self):
        m = ant.WorkerAnt()
        f = ant.WorkerAnt()
        genetics = [m.alpha, m.beta, m.gamma, f.alpha, f.beta, f.gamma]

        c = ant.WorkerAnt(m, f)

        self.assertTrue(c.alpha in genetics)
        self.assertTrue(c.beta in genetics)
        self.assertTrue(c.gamma in genetics)

    def test_children_mutation(self):
        m = ant.WorkerAnt()
        f = ant.WorkerAnt()
        c = ant.WorkerAnt(m, f)

        old_genetics = [c.alpha, c.beta, c.gamma]
        c.mutate()
        new_genetics = [c.alpha, c.beta, c.gamma]

        self.assertFalse(old_genetics == new_genetics)

    def test_ant_hunger(self):
        a = ant.WorkerAnt()
        old_hunger = a.hunger
        a.update_hunger()

        self.assertTrue(a.hunger > old_hunger)

    def test_ant_starvation(self):
        env = environment.Environment()
        a = ant.WorkerAnt(env=env)
        env.ants.append(a)

        a.hunger = a.hunger_max
        a.update_hunger()

        self.assertFalse(a in env.ants)

    def test_ant_abandon_search(self):
        a = ant.WorkerAnt()

        a.hunger = a.hunger_max / 2
        a.update_hunger()

        self.assertFalse(a.searching)

    def test_ant_lay_home_pheromone(self):
        env = environment.Environment()
        env.generate_grid(1, 1)
        env.create_ant()
        a = env.ants[0]
        a.visited.add(env.tiles[0][0])
        a.lay_pheromone()
        self.assertTrue(env.tiles[0][0].home_pheromone > 0)

    def test_ant_lay_food_pheromone(self):
        env = environment.Environment()
        env.generate_grid(1, 1)
        env.create_ant()
        a = env.ants[0]
        a.visited.add(env.tiles[0][0])
        a.searching = True
        a.lay_pheromone()
        self.assertTrue(env.tiles[0][0].food_pheromone > 0)

    def test_ant_check_neighbors(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        a = env.ants[0]
        a.coordinates = (1, 1)
        a.direction = (1, 0)
        available = a.check_neighbors()
        self.assertEqual(len(available), 3)
        result = []
        for t in available:
            result.append(t.coordinate)
        self.assertIn((2, 1), result)
        self.assertIn((2, 0), result)
        self.assertIn((2, 2), result)

        a.direction = (-1, 1)
        available = a.check_neighbors()
        result = []
        for t in available:
            result.append(t.coordinate)
        self.assertIn((0, 1), result)
        self.assertIn((0, 2), result)
        self.assertIn((1, 2), result)

    def test_ant_check_neighbors_exceptions(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        a = env.ants[0]
        a.coordinates = (1, 1)
        a.direction = (1, 0)
        env.tiles[2][1].set_type("water")
        available = a.check_neighbors()
        self.assertEqual(len(available), 2)
        env.create_ant()
        env.ants[1].coordinates = (2, 0)
        for t in available:
            if env.check_if_occupied(t):
                available.remove(t)

        self.assertEqual(len(available), 1)

    def test_move_forward(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        a = env.ants[0]
        a.coordinates = (1, 1)
        a.direction = (-1, 1)

        a.move_forward()
        self.assertEqual(a.coordinates, (0, 2))

    def test_turn_left(self):
        a = ant.WorkerAnt()
        a.direction = (1, 0)

        a.turn_left()
        self.assertEqual(a.direction, (1, -1))

    def test_turn_right(self):
        a = ant.WorkerAnt()
        a.direction = (1, 0)

        a.turn_right()
        self.assertEqual(a.direction, (1, 1))

    def test_update_state(self):
        a = ant.WorkerAnt()
        oldage = a.age
        oldhunger = a.hunger

        a.update_state()

        self.assertNotEqual(a.age, oldage)
        self.assertNotEqual(a.hunger, oldhunger)

    def test_get_highest_home_pheromone_option(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        ant = env.ants[0]
        ant.coordinates = (1, 1)
        ant.direction = (1, 0)
        env.tiles[2][0].home_pheromone = 5

        tiles = ant.check_neighbors()
        self.assertEqual(
            ant.get_pheromone_tile(tiles, target="home").coordinate, (2, 0)
        )

    def test_get_highest_food_pheromone_option(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        ant = env.ants[0]
        ant.coordinates = (1, 1)
        ant.direction = (1, 0)
        env.tiles[2][0].food_pheromone = 5

        tiles = ant.check_neighbors()
        self.assertEqual(
            ant.get_pheromone_tile(tiles, target="food").coordinate, (2, 0)
        )

    def test_make_home_path_decision_with_pheromone(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        ant = env.ants[0]
        ant.coordinates = (1, 1)
        ant.direction = (1, 0)
        env.tiles[2][0].home_pheromone = 5
        env.tiles[2][2].home_pheromone = 2

        ant.search_home(random_choice=False)
        self.assertEqual(ant.coordinates, (2, 0))

    def test_make_food_path_decision_with_pheromone(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        ant = env.ants[0]
        ant.coordinates = (1, 1)
        ant.direction = (1, 0)
        env.tiles[2][0].food_pheromone = 5
        env.tiles[2][2].food_pheromone = 2

        ant.search_food(random_choice=False)
        self.assertEqual(ant.coordinates, (2, 0))

    def test_random_home_path_decisison_without_pheromone(self):
        env = environment.Environment()
        env.generate_grid(3, 3)
        env.create_ant()
        ant = env.ants[0]
        ant.coordinates = (1, 1)
        ant.direction, old_dir = (1, 0), (1, 0)

        ant.search_home(random_choice=True)
        self.assertNotEqual(ant.coordinates, old_dir)


class TestNaturalSelection(tcase):

    def test_find_best(self):
        env = environment.Environment()
        a1 = ant.WorkerAnt()
        a2 = ant.WorkerAnt()
        a3 = ant.WorkerAnt()

        a1.food_count = 3
        a2.food_count = 1
        a3.food_count = 2

        ants = [a1, a2, a3]

        self.assertEqual((a1, a3), env.get_best_parents(ants))

    def test_if_find_best_fails_when_parents_not_found(self):
        env = environment.Environment()
        env.create_ant()
        ants = env.get_best_parents(env.ants)
        self.assertIsNone(ants)

    def test_create_offspring(self):
        env = environment.Environment()
        a1 = ant.WorkerAnt()
        a2 = ant.WorkerAnt()
        a3 = ant.WorkerAnt()

        a1.food_count = 3
        a2.food_count = 1
        a3.food_count = 2

        ants = [a1, a2, a3]
        mother, father = env.get_best_parents(ants)
        a4 = ant.WorkerAnt(mother, father)
        self.assertIn(a4.alpha, [a1.alpha, a2.alpha, a3.alpha])
        self.assertIn(a4.beta, [a1.beta, a2.beta, a3.beta])
        self.assertIn(a4.gamma, [a1.gamma, a2.gamma, a3.gamma])

    def test_find_eligible_ants(self):
        env = environment.Environment()
        a1 = ant.WorkerAnt()
        a2 = ant.WorkerAnt()
        a3 = ant.WorkerAnt()

        tres = env.selection_age_treshold

        a1.age = tres
        a2.age = tres + 1
        a3.age = tres - 1

        ants = [a1, a2, a3]
        eligible_ants = env.get_eligible_ants(ants)

        self.assertTrue(a1 in eligible_ants)
        self.assertTrue(a2 in eligible_ants)
        self.assertFalse(a3 in eligible_ants)

    def test_automatic_natural_selection(self):
        env = environment.Environment()
        for i in range(0, 5):
            env.create_ant()
        age = env.selection_age_treshold - 3
        for a in env.ants:
            a.age = age
            age += 1

        old_length = len(env.ants)
        env.time = 999
        env.update_state()

        self.assertTrue(len(env.ants) == old_length + 1)


class TestTiles(tcase):

    def test_create_tile(self):
        t = environment.Tile(0, 0)
        self.assertIsInstance(t, environment.Tile)

    def test_tile_attributes(self):
        t = environment.Tile(0, 0)
        self.assertTrue(hasattr(t, "home_pheromone"))
        self.assertTrue(hasattr(t, "food_pheromone"))
        self.assertTrue(hasattr(t, "coordinate"))
        self.assertTrue(hasattr(t, "tiletype"))

    def test_change_tile_type(self):
        t = environment.Tile(0, 0)
        self.assertEqual(t.tiletype, "default")
        t.set_type("water")
        self.assertEqual(t.tiletype, "water")

    def test_check_if_tile_is_occupied(self):
        env = environment.Environment()
        env.generate_grid(10, 10)
        env.create_ant()
        a = env.ants[0]
        a.coordinates = (1, 1)
        t = env.tiles[1][1]
        self.assertTrue(env.check_if_occupied(t))
        t = env.tiles[0][1]
        self.assertFalse(env.check_if_occupied(t))

if __name__ == '__main__':
    unittest.main()
