# import sys
# sys.path.insert(0, '/opt/pypy3/site-packages')
import random
import tdl
from noise import snoise2, pnoise3
from functions import (
    shade_color, tint_color, filled_circle, alpha_blend_color, turn,
    tiles_in_front, check_range, create_rect, check_point_rectangle,
    weighted_choice
)
from river import gen_river

# tdl.set_font("courier12x12_aa_tc.png", altLayout=True, greyscale=True)
tdl.set_font("arial12x12.png", altLayout=True, greyscale=True)

MOVEMENT_KEYS = {
    # standard arrow keys
    'UP': [0, -1],
    'DOWN': [0, 1],
    'LEFT': [-1, 0],
    'RIGHT': [1, 0],

    # diagonal keys
    # keep in mind that the keypad won't use these keys even if
    # num-lock is off
    'HOME': [-1, -1],
    'PAGEUP': [1, -1],
    'PAGEDOWN': [1, 1],
    'END': [-1, 1],

    # number-pad keys
    # These keys will always show as KPx regardless if num-lock
    # is on or off.  Keep in mind that some keyboards and laptops
    # may be missing a keypad entirely.
    # 7 8 9
    # 4   6
    # 1 2 3
    'KP1': [-1, 1],
    'KP2': [0, 1],
    'KP3': [1, 1],
    'KP4': [-1, 0],
    'KP6': [1, 0],
    'KP7': [-1, -1],
    'KP8': [0, -1],
    'KP9': [1, -1],
}


class UIButton:

    def __init__(
        self, con, x, y, label="DEBUG", action=None, args=None, kwargs=None
    ):
        self.console = con
        self.x, self.y = x, y
        self.width, self.height = len(label) + 2, 3
        self.label = label
        self.action = action
        self.args, self.kwargs = args, kwargs

    def check_hit(self, p):
        r = create_rect(self.x, self.y, self.width, self.height)
        if check_point_rectangle(p[0], p[1], r):
            self.click()

    def click(self):
        # print("CLACK")
        if self.action:
            if self.args and self.kwargs:
                self.action(*self.args, **self.kwargs)
            elif self.args and not self.kwargs:
                self.action(*self.args)
            elif self.kwargs and not self.args:
                self.action(**self.kwargs)
            else:
                self.action()

    def draw(self):
        self.console.draw_frame(
            self.x, self.y, self.width, self.height, None, bg=(150, 150, 150)
        )
        # self.console.draw_rect(
        #     b.x + 1, b.y + 1, len(b.label), 1, None, bg=(255, 255, 255)
        # )
        self.console.draw_str(
            self.x + 1, self.y + 1, self.label
        )


class UIValueChanger:
    def __init__(self, con, x, y, label, cur_val=None, action=None, incr=1):
        self.console = con
        self.x, self.y = x, y
        self.label = label
        self.cur_val = cur_val
        self.action = action
        self.incr_rate = incr
        self.btn_decr = UIButton(
            con, x + len(self.label) + 1, y, label="-", action=self.decrease
        )
        self.btn_incr = UIButton(
            con, x + len(self.label) + 5, y, label="+", action=self.increase
        )

    def decrease(self):
        if self.action:
            self.action(-self.incr_rate)

    def increase(self):
        if self.action:
            self.action(self.incr_rate)

    def check_hit(self, p):
        self.btn_decr.check_hit(p)
        self.btn_incr.check_hit(p)

    def draw(self):
        self.console.draw_str(self.x, self.y + 1, self.label)
        self.btn_decr.draw()
        self.btn_incr.draw()
        if self.cur_val:
            self.console.draw_str(
                self.x + len(self.label) + 9, self.y + 1,
                "{0:.3f}".format(self.cur_val())
            )


class SettingsWindow:
    def __init__(self, game):
        self.game = game
        self.console = tdl.Console(
            game.width - 2, game.height - 2
        )
        self.ui_elements = [
            UIButton(
                self.console, 2, 4, label="Set 1", action="print", args=["CLACK"]
            ),
            UIButton(
                self.console, 2, 8, label="Set 2", action="print", args=["CLACK"]
            ),
            UIButton(
                self.console, 2, 12, label="Set 3",
                action="print", args=["CLACK"]
            ),
            UIValueChanger(
                self.console, 2, 16, "FPS:", cur_val=game.get_fps,
                action=game.set_fps
            ),
            UIValueChanger(
                self.console, 2, 20, "Evaporation rate:",
                cur_val=game.world.get_pher_evap_rate,
                action=game.world.change_pher_evap_rate, incr=0.001
            ),
            UIValueChanger(
                self.console, 2, 24, "Pher sensitivity:",
                cur_val=game.world.get_pher_sensitivity,
                action=game.world.change_pher_sensitivity, incr=0.1
            ),
            UIValueChanger(
                self.console, 2, 28, "Pher refill amount:",
                cur_val=game.world.get_pher_refill_amnt,
                action=game.world.change_pher_refill_amnt, incr=0.05
            ),
            UIValueChanger(
                self.console, 2, 32, "Pher walk amount:",
                cur_val=game.world.get_pher_walk_amnt,
                action=game.world.change_pher_walk_amnt, incr=0.01
            )
        ]

    def update(self):
        if self.game.active_window == self.console:
            self.draw()

    def click(self, pos):
        pos = (pos[0] - 1, pos[1] - 1)
        for e in self.ui_elements:
            e.check_hit(pos)

    def draw(self):
        self.console.clear()
        self.console.draw_str(2, 2, "SETTINGS|")
        for e in self.ui_elements:
            e.draw()


class InfoWindow:
    def __init__(self, game, width, height, type="pher"):
        self.game = game
        self.console = tdl.Console(width, height)
        self.width, self.height = width, height
        self.type = type
        self.grid = [
            [0 for y in range(self.height)] for x in range(self.width)
        ]
        if self.type == "pher":
            self.console.set_colors(fg=(255, 128, 128))
        elif self.type == "height":
            self.console.set_colors(fg=(64, 48, 32))

    def update(self):
        if self.game.active_window == self.console:
            if self.type == "pher":
                self.grid = self.game.world.pher_grid
                for x in range(self.width):
                    for y in range(self.height):
                        gx, gy = self.game.world.get_gamepos(x + 1, y + 1)
                        try:
                            v = self.game.world.pher_grid[gx][gy]
                            v = int(v * 10)
                            if v >= 10:
                                v = 9
                        except IndexError:
                            v = 0
                        self.grid[x][y] = v
            if self.type == "height":
                self.grid = self.game.world.heightmap
                for x in range(self.width):
                    for y in range(self.height):
                        gx, gy = self.game.world.get_gamepos(x + 1, y + 1)
                        try:
                            v = self.game.world.heightmap[gx][gy]
                            v = int(v)
                            if v >= 10:
                                v = 9
                        except IndexError:
                            v = 0
                        self.grid[x][y] = v

            self.draw()

    def draw(self):
        self.console.clear()
        self.console.blit(self.game.world.window)
        for x in range(self.width):
            for y in range(self.height):
                self.console.draw_char(x, y, str(self.grid[x][y]), bg=None)


class UIWindow:
    def __init__(self):
        self.console = tdl.Console(20, 10)

    def update(self):
        pass

    def draw(self):
        self.console.clear()
        self.console.draw_str(10, 10, "TESTING")


class Game:
    def __init__(self):
        self.width, self.height = 120, 80
        self.console = tdl.init(
            self.width, self.height,
            title="importANT", fullscreen=False, renderer=u'OPENGL'
        )
        self.console.set_colors(
            fg=(255, 225, 200), bg=(50, 30, 10)
        )
        tdl.set_fps(15)
        self.mouse_pos = (0, 0)
        self.paused = False
        self.mouse_state = dict(
            LEFT=False,
            RIGHT=False
        )
        self.world = World(self)
        self.active_window = self.world.window
        self.settings = SettingsWindow(self)
        self.pher_window = InfoWindow(
            self, self.width - 2, self.height - 2
        )
        self.height_window = InfoWindow(
            self, self.width - 2, self.height - 2, type="height"
        )
        self.windows = dict(
            world=self.world.window,
            settings=self.settings.console,
            pher=self.pher_window.console,
            height=self.height_window.console
        )
        self.symbols = dict(
            diag1=chr(227),
            diag2=chr(226),
            horizontal=chr(229),
            vertical=chr(228)
        )
        self.draw_borders()
        self.world.render()

    def set_fps(self, change=0, value=0):
        if value:
            if value >= 1:
                tdl.set_fps(int(value))
        elif change:
            fps = tdl.get_fps() + change
            if fps >= 1:
                tdl.set_fps(fps)
            else:
                tdl.set_fps(1)

    def get_fps(self):
        return tdl.get_fps()

    def set_active_window(self, window):
        try:
            self.active_window = self.windows[window]
        except KeyError:
            self.active_window = self.world.window

    def draw_borders(self):
        for x in range(1, self.width - 1):
            self.console.drawChar(x, 0, chr(205))
            self.console.drawChar(x, self.height - 1, chr(205))
        for y in range(1, self.height - 1):
            self.console.drawChar(0, y, chr(186))
            self.console.drawChar(self.width - 1, y, chr(186))
        self.console.drawChar(0, 0, chr(218))
        self.console.drawChar(0, self.height - 1, chr(192))
        self.console.drawChar(self.width - 1, 0, chr(191))
        self.console.drawChar(self.width - 1, self.height - 1, chr(217))

    def draw_bounds(self):
        self.console.draw_rect(1, 1, self.width - 2, self.height - 2, " ")

    def draw_ui(self):
        a = 0
        f = 0
        for c in self.world.colonies:
            a += len(c.ants)
            f += c.food
        strings = [
            "Seed: {0}".format(str(self.world.seed)),
            "Colonies: {0}".format(len(self.world.colonies)),
            "Ants: {0}".format(a),
            "Food: {0}".format(f)
        ]
        l = 0
        for s in strings:
            l += len(s)
        self.console.draw_rect(2, 0, l, 1, " ")
        offset = 0
        for s in strings:
            self.console.draw_str(
                offset, 0, s
            )
            offset += len(s) + 1

        # for r in range(16):
        #     x = 0
        #     for c in range(r * 120, 100 + r * 120 + 120):
        #         x += 1
        #         self.console.draw_char(x, self.height - 1 - r, chr(c))

    def update(self, dt):
        redraw = False
        for event in tdl.event.get():
            if event.type == "KEYDOWN":
                if event.key == 'ESCAPE':
                    raise SystemExit()
                elif event.key == "1":
                    if not self.active_window == self.windows["world"]:
                        self.set_active_window("world")
                        self.paused = False
                elif event.key == "2":
                    self.set_active_window("settings")
                    self.paused = True
                elif event.key == "3":
                    self.set_active_window("pher")
                elif event.key == "4":
                    self.set_active_window("height")
                if self.active_window == self.windows["world"]:
                    if event.keychar.upper() in MOVEMENT_KEYS:
                        key_x, key_y = MOVEMENT_KEYS[event.keychar.upper()]
                        self.world.camera.move(key_x, key_y)
                        redraw = True
                    elif event.key == 'SPACE':
                        self.paused = not self.paused
                    elif event.key == "F1":
                        self.world.generate_world()
                        redraw = True
                    elif event.key == "F2":
                        x, y = self.world.get_gamepos(*self.mouse_pos)
                        self.world.spawn_colony(x=x, y=y)
                        redraw = True
                    elif event.key == "F3":
                        x, y = self.world.get_gamepos(*self.mouse_pos)
                        self.world.spawn_food(x, y)
                        redraw = True
                    elif event.key == "KPADD":
                        for c in self.world.colonies:
                            c.change_size(grow=1)
                        redraw = True
                    elif event.key == "KPSUB":
                        for c in self.world.colonies:
                            c.change_size(shrink=1)
                        redraw = True
                    elif event.keychar == "a":
                        for c in self.world.colonies:
                            for i in range(10):
                                c.spawn_ant(debug=True)
                    else:
                        print(event.keychar)
            elif event.type == 'MOUSEMOTION':
                self.mouse_pos = event.cell
                if self.active_window == self.windows["world"]:
                    if self.mouse_state["RIGHT"]:
                        self.world.camera.move(*event.motion)
                    continue
            elif event.type == "MOUSEDOWN":
                if event.button in self.mouse_state:
                    self.mouse_state[event.button] = True
                if self.mouse_state["LEFT"]:
                    if self.active_window == self.world.window:
                        x, y = self.world.get_gamepos(*event.cell)
                        self.world.build_wall(x, y)
                    elif self.active_window == self.windows["settings"]:
                        self.settings.click(event.cell)
            elif event.type == "MOUSEUP":
                if event.button in self.mouse_state:
                    self.mouse_state[event.button] = False

            if event.type == "QUIT":
                raise SystemExit("The window has been closed.")
        self.world.update()
        self.settings.update()
        self.pher_window.update()
        self.height_window.update()
        if redraw:
            self.world.render()

    def render(self, dt):
        if not self.paused:
            self.world.render()
        self.draw_bounds()
        self.console.blit(
            self.active_window,
            x=1, y=1,
            width=self.width - 2, height=self.height - 2
        )
        self.draw_ui()
        tdl.flush()


class World:
    def __init__(
        self, game, width=200, height=200, seed=random.randint(1, 50000)
    ):
        self.game = game
        self.seed = seed
        self.timer, self.fps = 0, 15
        self.width, self.height = width, height
        self.bg_console = tdl.Console(width, height)
        self.path_console = tdl.Console(width, height)
        self.console = tdl.Console(width, height)
        self.window = tdl.Window(
            self.console,
            x=width // 2 - (game.width - 2) // 2,
            y=height // 2 - (game.height - 2) // 2,
            width=game.width - 2, height=game.height - 2
        )
        self.parameters = dict(
            pher_evap_rate=0.005,
            pher_amount_walk=0.05,
            pher_amount_refill=0.50,
            pher_sensitivity=5.,
            terrain_awareness=1.,
            max_pher=1.,
            rand_dir_chance=10
        )
        self.colonies = []
        self.generate_world()
        self.camera = Camera(
            self, x=width // 2, y=height // 2
        )

    def check_on_screen(self, x, y):
        if x >= self.window.x and x <= self.window.x + self.window.width:
            if y >= self.window.y and y <= self.window.y + self.window.height:
                return True
        return False

    def get_pher_evap_rate(self):
        return self.parameters["pher_evap_rate"]

    def get_pher_refill_amnt(self):
        return self.parameters["pher_amount_refill"]

    def get_pher_walk_amnt(self):
        return self.parameters["pher_amount_walk"]

    def get_pher_sensitivity(self):
        return self.parameters["pher_sensitivity"]

    def change_pher_evap_rate(self, change=0, value=0):
        if change:
            self.parameters["pher_evap_rate"] += change
        elif value:
            self.parameters["pher_evap_rate"] = value

    def change_pher_refill_amnt(self, change=0, value=0):
        if change:
            self.parameters["pher_amount_refill"] += change
        elif value:
            self.parameters["pher_amount_refill"] = value

    def change_pher_walk_amnt(self, change=0, value=0):
        if change:
            self.parameters["pher_amount_walk"] += change
        elif value:
            self.parameters["pher_amount_walk"] = value

    def change_pher_sensitivity(self, change=0, value=0):
        if change:
            self.parameters["pher_sensitivity"] += change
        elif value:
            self.parameters["pher_sensitivity"] = value

    def get_gamepos(self, x, y):
        return x + self.window.x - 1, y + self.window.y - 1

    def spawn_colony(self, x=30, y=30):
        self.colonies.append(Colony(self, x=x, y=y))

    def build_wall(self, x, y):
        if (x, y) in self.walls:
            self.walls.remove((x, y))
            self.blocked_grid[x][y] = False
        elif self.blocked_grid[x][y]:
            pass
        else:
            self.walls.add((x, y))
            self.blocked_grid[x][y] = True

    def generate_world(self):
        self.game.draw_borders()
        random.seed()
        self.seed = random.randint(1, 99999)
        self.blocked_grid = [
            [False for y in range(self.height)] for x in range(self.width)
        ]
        self.path_grid = [
            [0. for y in range(self.height)] for x in range(self.width)
        ]
        self.pher_grid = [
            [0. for y in range(self.height)] for x in range(self.width)
        ]
        self.home_pher_grid = [
            [0. for y in range(self.height)] for x in range(self.width)
        ]
        self.color_array = [
            [(0, 0, 0) for y in range(self.height)] for x in range(self.width)
        ]
        self.food_grid = [
            [False for y in range(self.height)] for x in range(self.width)
        ]
        self.heightmap = [
            [1. for y in range(self.height)] for x in range(self.width)
        ]
        self.make_heightmap()
        self.walls = set()
        self.make_river()
        self.make_grass()
        self.make_puddles()
        self.make_rocks()
        self.make_path()
        self.path_console.set_colors(fg=None, bg=None)
        for x, y in self.bg_console:
            self.bg_console.draw_char(x, y, None, bg=self.color_array[x][y])
        self.path_console.blit(self.bg_console)
        self.colonies = []
        # self.spawn_colony(x=self.width // 2, y=self.height // 2)

    def make_heightmap(self):
        seed = self.seed
        octaves = 2
        freq = 32.
        for y in range(self.height):
            for x in range(self.width):
                self.heightmap[x][y] = pnoise3(
                    x / freq, y / freq, seed, octaves=octaves
                ) * 10 + 3

    def make_grass(self):
        octaves = random.uniform(0.5, 0.8)
        freq = 4.0 * octaves
        mx, mn = 0, 0
        for y in range(self.height):
            for x in range(self.width):
                value = (snoise2(x / freq, y / freq, 1) + 8) / 8
                self.color_array[x][y] = shade_color(
                    (75, 200, 15), light=value
                )
                n = self.heightmap[x][y]
                if n > mx:
                    mx = n
                c = self.color_array[x][y]
                if n >= 7.:
                    self.color_array[x][y] = shade_color(
                        c, light=1.4
                    )
                elif n >= 6:
                    self.color_array[x][y] = shade_color(
                        c, light=1.3
                    )
                elif n >= 5:
                    self.color_array[x][y] = shade_color(
                        c, light=1.2
                    )
                elif n >= 4:
                    self.color_array[x][y] = shade_color(
                        c, light=1.1
                    )
                elif n >= 3:
                    pass
                elif n >= 2.5:
                    self.color_array[x][y] = shade_color(
                        c, light=0.9
                    )
                elif n >= 2:
                    self.color_array[x][y] = shade_color(
                        c, light=0.8
                    )
                elif n >= 1.5:
                    self.color_array[x][y] = shade_color(
                        c, light=0.7
                    )
                elif n > 1.:
                    self.color_array[x][y] = shade_color(
                        c, light=0.6
                    )

    def spawn_food(self, x, y):
        if not self.blocked_grid[x][y] and not self.food_grid[x][y]:
            self.food_grid[x][y] = Food(x, y)

    # def get_pf_cost(self, origin, next):
    #     h1 = self.heightmap[origin[0]][origin[1]]
    #     # print(next)
    #     h2 = self.heightmap[next[0]][next[1]]
    #     # return abs(h1 - h2) * 10
    #     return int(h2 / 2)

    def make_puddles(self):
        for y in range(self.height):
            for x in range(self.width):
                ripple = (snoise2(x / 4, y / 4, 1) + 8) / 8
                n = self.heightmap[x][y]
                if n <= 0.2:
                    self.color_array[x][y] = shade_color(
                        (20, 110, 140), light=(ripple + 1) / 2
                    )
                elif n <= 0.5:
                    self.color_array[x][y] = shade_color(
                        (30, 120, 170), light=(ripple + 1) / 2
                    )
                elif n < 0.7:
                    self.color_array[x][y] = shade_color(
                        (100, 165, 205), light=(ripple + 1) / 2
                    )
                elif n < 1:
                    c = alpha_blend_color(
                        self.color_array[x][y],
                        (100, 75, 60), 0.7
                    )
                    self.color_array[x][y] = c

                if n < 0.7:
                    self.blocked_grid[x][y] = True

    def make_river(self):
        lowpoints = []
        target_nodes = []
        for x in range(self.width):
            for y in range(self.height):
                if self.heightmap[x][y] < 0.7:
                    lowpoints.append((x, y))
        random.shuffle(lowpoints)
        target_nodes.append(lowpoints[0])
        lowpoints.pop(0)
        while len(target_nodes) < 25:
            c = lowpoints[0]
            for tn in target_nodes:
                if check_range(c, tn, 10):
                    lowpoints.pop(0)
                    continue
            else:
                target_nodes.append(c)
                lowpoints.pop(0)
        r = gen_river(
            self.width, self.height, startnode=(32, 32), numnodes=100,
            custom_nodes=target_nodes
        )
        for px, py in r:
            for x, y in [(px + i, py + j) for i in (-3, 0, 3) for j in (-3, 0, 3) if i != 0 or j != 0]:
                try:
                    if self.heightmap[x][y] > 0:
                        self.heightmap[x][y] *= 0.8
                except IndexError:
                    pass
            for x, y in [(px + i, py + j) for i in (-2, 0, 2) for j in (-2, 0, 2) if i != 0 or j != 0]:
                try:
                    if self.heightmap[x][y] > 0:
                        self.heightmap[x][y] *= 0.8
                except IndexError:
                    pass
            for x, y in [(px + i, py + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if i != 0 or j != 0]:
                try:
                    if self.heightmap[x][y] > 0:
                        self.heightmap[x][y] *= 0.6
                except IndexError:
                    pass
            self.heightmap[px][py] = 0.

    def make_rocks(self):
        seed = self.seed * 3
        octaves = 1
        freq = 16.
        for y in range(self.height):
            for x in range(self.width):
                if not self.blocked_grid[x][y]:
                    n = pnoise3(
                        x / freq, y / freq, seed, octaves=octaves
                    ) * 8 + 4
                    if not random.randint(0, 3):
                        ripple = (snoise2(x / 4, y / 4, 1) + 2) / 2
                    else:
                        ripple = 1
                    if n <= 0.1:
                        self.color_array[x][y] = shade_color(
                            (120, 120, 120), ripple
                        )
                    elif n <= 0.3:
                        self.color_array[x][y] = (110, 110, 110)
                    elif n <= 0.5:
                        self.color_array[x][y] = (100, 100, 100)
                    elif n < 0.8:
                        self.color_array[x][y] = (90, 90, 90)
                # elif n < 1:
                #     self.color_array[x][y] = alpha_blend_color(
                #         self.color_array[x][y], (120, 120, 120), 0.7
                #     )
                    if n < 0.8:
                        self.blocked_grid[x][y] = True

    def make_path(self):
        for x, y in self.console:
            if self.path_grid[x][y]:
                if self.path_grid[x][y] >= 0.015:
                    self.path_grid[x][y] -= 0.015
                else:
                    self.path_grid[x][y] = 0.

    def draw_path(self):
        c = (100, 85, 50)
        for x, y in self.console:
            if self.path_grid[x][y]:
                if self.path_grid[x][y] > 0.05:
                    if self.check_on_screen(x, y):
                        if self.path_grid[x][y] > 0.95:
                            a = 0.98
                        else:
                            a = self.path_grid[x][y]
                        value = (snoise2(x / 2, y / 2, 1) + 8) / 8
                        new_c = shade_color(
                            c, light=value
                        )
                        new_c = alpha_blend_color(
                            self.color_array[x][y], new_c, a
                        )
                        self.path_console.draw_char(
                            x, y, None, bg=new_c
                        )

    def evaporate(self):
        rate = self.parameters["pher_evap_rate"]
        for x, y in self.console:
            if self.pher_grid[x][y]:
                if self.pher_grid[x][y] >= rate:
                    self.pher_grid[x][y] -= rate
                else:
                    self.pher_grid[x][y] = 0
            if self.home_pher_grid[x][y]:
                if self.home_pher_grid[x][y] >= rate:
                    self.home_pher_grid[x][y] -= rate
                else:
                    self.home_pher_grid[x][y] = 0

    def wear_path(self, x, y):
        wear = 0.05
        if (
            not self.path_grid[x][y] >= 1. and
            not self.path_grid[x][y] + wear > 1.
        ):
            self.path_grid[x][y] += wear

    def search_pheromone(self, pos, amount):
        x, y = pos
        t = self.pher_grid[x][y]
        if t + amount <= self.parameters["max_pher"]:
            self.pher_grid[x][y] += amount
        else:
            self.pher_grid[x][y] = self.parameters["max_pher"]

    def home_pheromone(self, pos, amount):
        x, y = pos
        t = self.home_pher_grid[x][y]
        if t + amount <= self.parameters["max_pher"]:
            self.home_pher_grid[x][y] += amount
        else:
            self.home_pher_grid[x][y] = self.parameters["max_pher"]

    def update(self):
        self.window.x = self.camera.x - self.window.width // 2
        self.window.y = self.camera.y - self.window.height // 2
        if not self.game.paused:
            self.timer += 1
            if not self.timer % 5:
                self.make_path()
            if not self.timer % 3:
                self.evaporate()
            for x in range(self.width):
                for y in range(self.height):
                    if self.food_grid[x][y]:
                        if not self.food_grid[x][y].check():
                            self.food_grid[x][y] = False
            for c in self.colonies:
                c.update()

    def render(self):
        self.console.clear()
        if not self.timer % self.fps:
            self.path_console.clear()
            self.path_console.blit(self.bg_console)
            self.draw_path()
        self.console.blit(self.path_console)
        for wx, wy in self.walls:
            self.console.draw_char(wx, wy, "#", fg=(100, 100, 100), bg=None)
        for x in range(self.window.x, self.window.x + self.window.width):
            for y in range(self.window.y, self.window.y + self.window.height):
                if (x, y) in self.console:
                    if self.food_grid[x][y]:
                        self.console.draw_char(
                            x, y, chr(10), fg=(170, 80, 30), bg=None
                        )
        for c in self.colonies:
            for a in c.ants:
                if self.check_on_screen(a.x, a.y):
                    self.console.draw_char(
                        a.x, a.y, a.get_symbol(), fg=(50, 50, 50), bg=None
                    )
        for c in self.colonies:
            c.draw()


class Camera:
    def __init__(self, world, x, y):
        self.x, self.y = x, y
        self.world = world

    def move(self, x, y):
        self.x += x
        self.y += y
        if self.world.game.paused:
            self.world.render()
        else:
            self.world.path_console.clear()
            self.world.path_console.blit(self.world.bg_console)
            self.world.draw_path()


class Colony:

    def __init__(self, world, x=10, y=10):
        self.world = world
        self.x, self.y = x, y
        self.size = 2
        # self.points = circle(self.x, self.y, self.size)
        self.generate_hill()
        self.spawn_cd = 10 - self.size
        self.cd_timer = 0
        self.ants = []
        self.max_capacity = 25 + 3 ** self.size
        self.food = self.max_capacity * 2

    def generate_hill(self):
        self.base = filled_circle(self.x, self.y, radius=self.size)
        self.mid = set()
        self.top = set()
        if self.size >= 3:
            self.mid = filled_circle(self.x, self.y, radius=self.size - 2)
        if self.size >= 5:
            self.top = filled_circle(self.x, self.y, radius=self.size - 4)

        to_del = []
        for (x, y) in self.base:
            try:
                if self.world.blocked_grid[x][y]:
                    to_del.append((x, y))
            except IndexError:
                to_del.append((x, y))
        for p in to_del:
            self.base.remove(p)
            if p in self.mid:
                self.mid.remove(p)
            if p in self.top:
                self.top.remove(p)

    def spawn_ant(self, debug=False):
        if debug:
            self.ants.append(Ant(self))
        else:
            if self.food > 0:
                self.food -= 1
                self.ants.append(Ant(self))

    def change_size(self, newsize=None, grow=None, shrink=None):
        if newsize:
            self.size = newsize
        elif grow:
            self.size += grow
        elif shrink:
            self.size -= shrink
        self.generate_hill()
        self.max_capacity = 25 + 3 ** self.size
        self.spawn_cd = 10 - self.size
        if self.spawn_cd < 0:
            self.spawn_cd = 0
        if self.size <= 0:
            self.world.colonies.remove(self)

    def check_in_colony(self, x, y):
        return check_range((x, y), (self.x, self.y), self.size + 1)

    def update(self):
        for a in self.ants:
            a.update()
        if self.cd_timer <= 0:
            if len(self.ants) < self.max_capacity:
                self.spawn_ant()
                self.cd_timer = self.spawn_cd
        else:
            self.cd_timer -= 1

        if (
            len(self.ants) >= self.max_capacity and
            self.food >= (25 + 3 ** (self.size + 1)) * 2
        ):
            self.change_size(grow=1)
        elif (
            len(self.ants) < 25 + 3 ** (self.size - 1) and
            self.food <= 0
        ):
            self.change_size(shrink=1)

    def draw(self):
        # self.world.console.draw_rect(
        #     self.x, self.y, self.size, self.size, chr(176),
        #     fg=(200, 150, 100), bg=(100, 75, 50)
        # )
        for (x, y) in self.base:
            self.world.console.draw_char(
                x, y, chr(176),
                fg=(200, 150, 100), bg=(100, 75, 50)
            )
        for (x, y) in self.mid:
            self.world.console.draw_char(
                x, y, chr(177),
                fg=(200, 150, 100), bg=(110, 80, 55)
            )
        for (x, y) in self.top:
            self.world.console.draw_char(
                x, y, chr(178),
                fg=(200, 150, 100), bg=(120, 85, 60)
            )


class Ant:

    def __init__(self, colony):
        self.colony = colony
        self.x, self.y = colony.x, colony.y
        self.direction = (random.randint(-1, 1), random.randint(-1, 1))
        self.visited = []
        self.mode = 0   # 0: search, 1: home
        self.energy = 600
        self.max_energy = 600
        self.food = 0
        self.capacity = 2

    def get_symbol(self):
        dx, dy = self.direction
        symbol = self.colony.world.game.symbols
        if (
            dx == -1 and dy == -1 or
            dx == 1 and dy == 1
        ):
            return symbol["diag1"]
        elif (
            dx == -1 and dy == 1 or
            dx == 1 and dy == -1
        ):
            return symbol["diag2"]
        elif (
            dx == 1 and dy == 0 or
            dx == -1 and dy == 0
        ):
            return symbol["horizontal"]
        elif (
            dx == 0 and dy == -1 or
            dx == 0 and dy == 1
        ):
            return symbol["vertical"]
        else:
            return "o"

    def move(self):
        w = self.colony.world
        self.choose_dir()
        x = self.x + self.direction[0]
        y = self.y + self.direction[1]
        if not (x, y) == (self.x, self.y):
            if (x, y) in w.console:
                if not w.blocked_grid[x][y]:
                    pher_amount = w.parameters[
                        "pher_amount_walk"
                    ]
                    self.x, self.y = x, y
                    w.wear_path(x, y)
                    if not self.mode:
                        w.search_pheromone((x, y), pher_amount)
                    elif self.mode == 1:
                        w.home_pheromone((x, y), pher_amount)
                    self.visited.append((x, y))

    def change_direction(self, d=None):
        self.direction = d

    def choose_dir(self):
        w = self.colony.world
        ldir, fdir, rdir = tiles_in_front(self.direction)
        l = (self.x + ldir[0], self.y + ldir[1])
        f = (self.x + fdir[0], self.y + fdir[1])
        r = (self.x + rdir[0], self.y + rdir[1])
        lw, fw, rw = 0., 0.1, 0.

        sensitivity = w.parameters["pher_sensitivity"]
        # terrain_awareness = w.parameters["terrain_awareness"]

        # Heightmap weight
        hm = w.heightmap
        cur_val = hm[self.x][self.y]
        try:
            lw += 1 - abs(cur_val - hm[l[0]][l[1]])
        except IndexError:
            lw = 0
        try:
            fw += 1 - abs(cur_val - hm[f[0]][f[1]])
        except IndexError:
            fw = 0
        try:
            rw += 1 - abs(cur_val - hm[r[0]][r[1]])
        except IndexError:
            rw = 0

        # print(lw, fw, rw)

        if self.mode == 0:
            pher = w.pher_grid
        elif self.mode == 1:
            pher = w.home_pher_grid
        try:
            lw += pher[l[0]][l[1]] * sensitivity
        except IndexError:
            lw = 0
        try:
            fw += pher[f[0]][f[1]] * sensitivity
        except IndexError:
            fw = 0
        try:
            rw += pher[r[0]][r[1]] * sensitivity
        except IndexError:
            rw = 0

        if not self.mode:
            try:
                if w.food_grid[l[0]][l[1]]:
                    lw += 1
            except IndexError:
                lw = 0
            try:
                if w.food_grid[f[0]][f[1]]:
                    fw += 1
            except IndexError:
                fw = 0
            try:
                if w.food_grid[r[0]][r[1]]:
                    rw += 1
            except IndexError:
                rw = 0

        # fw = max(0.2, fw)
        lw, fw, rw = max(0, lw), max(0, fw), max(0, rw)
        # rand_chance = sum([lw, rw, fw]) / 3 / rand_dir_chance

        # choices = [
        #     ("left", lw),
        #     ("right", rw),
        #     ("forward", fw),
        #     ("random", rand_chance)
        # ]
        # print(lw, fw, rw)
        # print(rand_chance)
        # c = weighted_choice(choices)
        # print(c)
        # # print(choices, c)
        # if c == "left":
        #     self.change_direction(ldir)
        # elif c == "right":
        #     self.change_direction(rdir)
        # elif c == "forward":
        #     pass
        # elif c == "random":
        #     self.change_direction(random.choice([rdir, ldir]))

        rand_dir_chance = w.parameters["rand_dir_chance"]
        if random.randint(0, rand_dir_chance):
            if lw > max([fw, rw]):
                self.change_direction(ldir)
            elif rw > max([fw, lw]):
                self.change_direction(rdir)
            else:
                self.change_direction(fdir)
        else:
            self.change_direction(random.choice([rdir, ldir]))

    def deliver_food(self):
        self.colony.food += self.food
        self.refill_trail()
        self.food = 0
        self.mode = 0
        self.visited = []

    def refill_trail(self):
        pher_amount = self.colony.world.parameters["pher_amount_refill"]
        l = min(len(self.visited), self.max_energy // 2)
        for v in self.visited[l:]:
            if not self.mode:
                self.colony.world.home_pheromone(v, pher_amount)
                self.colony.world.search_pheromone(v, pher_amount)
            elif self.mode == 1:
                self.colony.world.home_pheromone(v, pher_amount)

    def turn(self, d):
        new_dir = turn(self.direction, d)
        self.change_direction(new_dir)

    def die(self):
        self.colony.ants.remove(self)

    def update(self):
        if self.energy <= 0:
            self.die()
            turns = 0
        turns = 1
        if turns:
            if not self.mode:
                if self.energy <= self.max_energy // 2:
                    self.mode = 1
                    self.visited = []
                if self.food < self.capacity:
                    if self.colony.world.food_grid[self.x][self.y]:
                        f = self.colony.world.food_grid[self.x][self.y].take()
                        self.food += f
                        turns -= 1
                        self.energy += 50
                else:
                    self.refill_trail()
                    self.visited = []
                    behind = (self.direction[0] * -1, self.direction[1] * -1)
                    self.change_direction(d=behind)
                    self.mode = 1
            elif self.mode == 1:
                for c in self.colony.world.colonies:
                    if c.check_in_colony(self.x, self.y):
                        self.deliver_food()
                        behind = (
                            self.direction[0] * -1, self.direction[1] * -1
                        )
                        self.change_direction(d=behind)
                        self.energy = self.max_energy
                        break

        if self.energy:
            self.energy -= 1

        if turns:
            self.move()


class Food:

    def __init__(self, x, y, amount=500):
        self.x, self.y = x, y
        self.amount = 500

    def take(self, amount=1):
        if self.amount >= amount:
            self.amount -= amount
            return amount
        elif self.amount:
            a = self.amount
            self.amount = 0
            return a
        else:
            return 0

    def check(self):
        if self.amount <= 0:
            return False
        else:
            return True


if __name__ == "__main__":
    g = Game()
    while True:
        g.update(0)
        g.render(0)
