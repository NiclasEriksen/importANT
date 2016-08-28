

def neighbors(node, all_nodes):
    dirs = [[0, 1], [1, 0], [-1, 0], [0, -1]]
    ddirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    result = set()
    # cdef bool x
    for dir in dirs:
        nx, ny = node[0] + dir[0], node[1] + dir[1]
        try:
            all_nodes[nx][ny]
        except IndexError:
            pass
        else:
            result.add((nx, ny))
    for dir in ddirs:
        nx, ny = node[0] + dir[0], node[1] + dir[1]
        try:
            all_nodes[nx][ny]
        except IndexError:
            pass
        else:
            x, y = False, False
            for r in result:
                if nx - 1 == r[0] and ny == r[1]:
                    x = True
                elif nx + 1 == r[0] and ny == r[1]:
                    x = True
                if ny - 1 == r[1] and nx == r[0]:
                    y = True
                elif ny + 1 == r[1] and nx == r[0]:
                    y = True

            if y and x:
                result.add((nx, ny))

    return result


def get_score(c, node, goal, heightmap):
    score = c.score
    if c.node[0] != node[0] and c.node[1] != node[1]:
        score += 14
    else:
        score += 10
    gx = abs(goal[0] - c.node[0])
    gy = abs(goal[1] - c.node[1])
    score += (gx + gy) * 5
    penalty = heightmap[c.node[0]][c.node[1]] * 1
    # print(score, "penalty:", penalty)
    score -= penalty
    return score


class Candidate:

    def __init__(self, node, lastnode=None):
        self.node = node
        self.score = 0
        self.visited = False
        self.lastnode = lastnode


def get_path(all_nodes, node, goal, heightmap):
    open_list = []
    closed_list = []
    path_list = []
    final_list = []
    start = Candidate(node, None)
    current = Candidate(node, start)
    count, current.count = 0, 0
    while current.node != goal:
        candidates = []

        for n in neighbors(current.node, all_nodes):

            c = Candidate(n, current)
            candidates.append(c)

        for c in candidates:

            closed = False
            for cc in closed_list:
                if c.node == cc.node:
                    closed = True
            for co in open_list:
                if co.node == c.node:
                    closed = True

            if not closed:
                c.count = count
                count += 1
                c.score = get_score(c, current.node, goal, heightmap)

                open_list.append(c)

        open_list = sorted(
            open_list,
            key=lambda x: x.count,
            reverse=False
        )
        if len(open_list) > 0:
            # count += 1
            next_c = open_list[0]
            closed_list.append(next_c)
            current = next_c
            open_list.remove(next_c)
        else:
            print("Goal not found. Node {0} broke it.".format(node))
            break

    nextnode = current  # goal
    path_list = [nextnode.node]
    while nextnode.node != start.node:
        nextnode = nextnode.lastnode
        path_list.append(nextnode.node)

    for c in reversed(path_list):
        final_list.append(c)

    if len(final_list) > 0:
        print("Pathfinding successful!")
        print("Steps: {0}".format(len(final_list)))
        return final_list, True
    else:
        print("ERROR: Pathfinding went wrong, returning to start.")
        final_list = [start]
        return final_list, False
