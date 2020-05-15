from room import Room
from player import Player
from world import World

import random
from collections import deque, defaultdict
import heapq
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
# map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph = literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []
directions_map = {'n': 's', 's': 'n', 'w': 'e', 'e': 'w'}

def longest_stride(room, direction):
    stride = 0
    while room.get_room_in_direction(direction) is not None:
        stride+=1
        room = room.get_room_in_direction(direction)
    return stride, direction
visited = {}
current_room = world.starting_room
room_stack = deque()
# room_stack.append()
room_id_path = []
# until we have visited all rooms
while len(visited) < len(world.rooms):
    # traverse the graph depth fisrt
    # every time we change current node, add it to path
    # if the current node is not visited, mark it as visited
    if current_room.id not in visited:
        # set the connections to None, as we don't know the room id's yet
        visited[current_room.id] = dict.fromkeys(
            current_room.get_exits(), None)
        room_id_path.append(current_room.id)
    # find unvisited neighbors
    unvisited = [direction for direction in visited[current_room.id]
                 if visited[current_room.id][direction] == None]
    if len(unvisited):
        room_stack.append(current_room)
        move_direction = max([longest_stride(current_room, direction) for direction in unvisited])[1]


        # move_direction = random.choice(unvisited)
        next_room = current_room.get_room_in_direction(move_direction)
        visited[current_room.id][move_direction] = next_room.id
        if next_room.id not in visited:
            visited[next_room.id] = dict.fromkeys(
                next_room.get_exits(), None)
            visited[next_room.id][directions_map[move_direction]] = current_room.id
        room_id_path.append(next_room.id)
        traversal_path.append(move_direction)
        current_room = next_room
    else:
        previous_room = current_room
        current_room = room_stack.pop()
        direction, = [d for d in visited[previous_room.id]
                      if visited[previous_room.id][d] == current_room.id]
        traversal_path.append(direction)
        room_id_path.append(current_room.id)

# transform graph into an array of arrays for simplicity sake
graph = [[value for value in v.values() if value is not None]
         for k, v in sorted(visited.items(), key=lambda x: x[0])]


def bfs(starting_vertex, destination_vertex):
    """
    Return a list containing the shortest path from
    starting_vertex to destination_vertex in
    breath-first order.
    """
    visited = set()
    visited.add(starting_vertex)
    paths = deque()
    paths.appendleft([starting_vertex])
    # print(starting_vertex)
    # store a queue of paths
    while len(paths):
        path = paths.pop()
        node = path[-1]
        # if the path ends with destination vertex, that the path we need, bfs ensures it's the shortest
        if node == destination_vertex:
            return path
        # else, look at all the neghbours, and add new paths to the queue
        else:
            for adjacent in graph[node]:
                if adjacent not in visited:
                    visited.add(node)
                    new_path = path+[adjacent]
                    paths.appendleft(new_path)


from math import inf

def shortestPathLength(graph, starting_room):
    nodeCount = len(graph)
    
    # NOTE
    # We are using BFS here because it's better suited for 'shortest path'
    # types of problems.

    # Thoughts:
    # 1. start the starting node, do BFS to try reaching all other nodes.
    # 2. Must keep track of visited nodes, else infinite loop may happen.
    # 3. But each node may have to be visited multiple times, as described in the problem
    #    statement. So we cannot be too strict in limiting searches
    # 4. We must describe the state during a search, we need:
    #    - The current path we are on
    #    - Nodes we have visited 

    # each search is described by (currentPathHEAD, visited)
    # same search does _not_ have to be repeated, since if re-visited with
    # the same state, it would yield the same result.
    # NOTE this does not prevent revisiting the same node again,
    # it just prevents revisiting it with the same STATE!

    # conceptually masks[k] indicates that only node k has been visited
    masks = [frozenset([i]) for i in range(nodeCount)]
    # used to check whether all nodes have been visited (11111...111)
    allVisited = frozenset(range(nodeCount))
    queue = deque([([starting_room], masks[starting_room])])
    steps = 0

    # encoded_visited in visited_states[node] iff
    # (node, encoded_visited) has been pushed onto the queue
    visited_states = [{masks[i]} for i in range(nodeCount)]
    # states in visited_states will never be pushed onto queue again

    while queue:
        # number of nodes to be popped off for current steps size
        # this avoids having to store steps along with the state
        # which consumes both time and memory
        count = len(queue)

        while count:
            current_path, visited = queue.popleft()
            currentNode = current_path[-1]
            if visited == allVisited:
                return steps, current_path

            # start bfs from each neighbor
            for nb in graph[currentNode]:
                new_visited = visited | masks[nb]
                new_path = current_path+[nb]
                # pre-check here to for efficiency, as each steps increment may results
                # in huge # of nodes being added into queue
                if new_visited == allVisited:
                    return steps + 1, new_path
                if new_visited not in visited_states[nb]:
                    visited_states[nb].add(new_visited)
                    queue.append((new_path, new_visited))

            count -= 1
        steps += 1
    # no path which explores every node
    return inf


print(shortestPathLength(graph, 0))
# shortest_paths = [[bfs(starting_node, target_node)
#                    for target_node in range(len(graph))]for starting_node in range(len(graph))]
# print(shortest_paths)

# print(room_id_path)
# print(traversal_path)
# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)
for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(
        f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")

"""
#######
# UNCOMMENT TO WALK AROUND
#######
player.current_room.print_room_description(player)
while True:
    cmds = input("-> ").lower().split(" ")
    if cmds[0] in ["n", "s", "e", "w"]:
        player.travel(cmds[0], True)
    elif cmds[0] == "q":
        break
    else:
        print("I did not understand that command.")
"""
"""
#####
#                                                                                                                                                           #
#                                                        434       497--366--361  334--384--435  476                                                        #
#                                                         |                   |    |              |                                                         #
#                                                         |                   |    |              |                                                         #
#                                              477--443  425            386--354--321  338  313  380--445--446                                              #
#                                                    |    |              |         |    |    |    |    |                                                    #
#                                                    |    |              |         |    |    |    |    |                                                    #
#                                                   408  350  483  385  388  285  304  278  287--353  480                                                   #
#                                                    |    |    |    |    |    |    |    |    |                                                              #
#                                                    |    |    |    |    |    |    |    |    |                                                              #
#                                    442  461  426  392--281  223--169  257  253  240  196--224  255  373                                                   #
#                                     |    |    |         |         |    |    |    |    |         |    |                                                    #
#                                     |    |    |         |         |    |    |    |    |         |    |                                                    #
#                                    417  422--394--318--199--197--165--163--228  233--152  192--239--336--421                                              #
#                                     |              |                   |              |    |                                                              #
#                                     |              |                   |              |    |                                                              #
#                          491  453--351  444  374--340  328--200--204  148--178  143  147--154--184  282  363  389                                         #
#                           |         |    |                   |         |         |    |              |    |    |                                          #
#                           |         |    |                   |         |         |    |              |    |    |                                          #
#                          489  441  332  387  341--316  195  175--141  121--123--138--139--176  136--231--294--311--499                                    #
#                           |    |    |    |         |    |         |    |                        |                                                         #
#                           |    |    |    |         |    |         |    |                        |                                                         #
#                     396--391  319  295  331  307  292--185--155  107  111--114--120  172  146  109  186--262--390--398                                    #
#                           |    |    |    |    |              |    |    |              |    |    |    |              |                                     #
#                           |    |    |    |    |              |    |    |              |    |    |    |              |                                     #
#           452--428--411--324--289--250  277  208--166  140  082  102--064  101  093  132  086--095  098  245--343  487                                    #
#                 |                   |    |         |    |    |         |    |    |    |    |         |    |                                               #
#                 |                   |    |         |    |    |         |    |    |    |    |         |    |                                               #
#           451--429  397  357--342--221--174  210  161  063--061  033  060  091  051  073  084  078--090--142  381--431                                    #
#                      |                   |    |    |         |    |    |    |    |    |    |    |              |                                          #
#                      |                   |    |    |         |    |    |    |    |    |    |    |              |                                          #
#      492--400--399--358  352  297--207  124--112--106--079--046--017--028  037--042  056--067  075--088--125--238--293                                    #
#                      |    |         |                             |    |    |         |         |    |    |                                               #
#                      |    |         |                             |    |    |         |         |    |    |                                               #
#           414--365--333--303  171--168--137  085  074  032  047--014  030  031  027--055  048--053  103  198--270--300--320                               #
#                 |         |              |    |    |    |         |         |    |         |                             |                                #
#                 |         |              |    |    |    |         |         |    |         |                             |                                #
#                447  301--187--167--108--081--045--040--019--015--013--009  020--026  035--044--059--189--275--283--376  471                               #
#                                          |                             |    |         |                             |                                     #
#                                          |                             |    |         |                             |                                     #
#                436  470  227--194--128--092  069--041--036--021  004  007--012--018--034--039--071--150--251  325  468                                    #
#                 |    |              |    |    |    |         |    |    |         |         |    |              |                                          #
#                 |    |              |    |    |    |         |    |    |         |         |    |              |                                          #
#           465--368--284--254--205--162  100  072  076  011--003--000--001--022  024--025  052  115--160--214--246--412                                    #
#                      |                        |         |         |    |         |    |                                                                   #
#                      |                        |         |         |    |         |    |                                                                   #
#           479--418--349  274--222--190--129  089  083--080  016--008  002--010  029  043--049--119--131--329--407                                         #
#                 |                        |    |    |                   |    |    |    |         |                                                         #
#                 |                        |    |    |                   |    |    |    |         |                                                         #
#                463--458  379  226--225--105--104  099  058--023--006--005  038  054  077--130  219--305--330--454                                         #
#                      |    |    |              |    |         |    |    |                        |         |                                               #
#                      |    |    |              |    |         |    |    |                        |         |                                               #
#           486--462  359  266--260  235--158--126  122  068--057  062  050--070--087  182--211  242  326  348                                              #
#                 |    |                   |    |              |    |    |    |    |    |    |    |    |                                                    #
#                 |    |                   |    |              |    |    |    |    |    |    |    |    |                                                    #
#                367--344--230  243  180--164  135  145--113--094  065  066  116  117--170  248  286--288--498                                              #
#                           |    |              |    |         |    |    |    |    |         |    |                                                         #
#                           |    |              |    |         |    |    |    |    |         |    |                                                         #
#                339--314--220--215--177--156--149  183  153--097  134  096  159  127--173  272  309--377--456                                              #
#                 |                        |    |              |    |    |         |    |         |                                                         #
#                 |                        |    |              |    |    |         |    |         |                                                         #
#           482--404  258--236--216--213--209  191  188  157--110  144  179--201  212  202--249  371--430--440                                              #
#            |              |         |         |    |         |    |    |    |    |    |                                                                   #
#            |              |         |         |    |         |    |    |    |    |    |                                                                   #
#           484  433--372--263  271--217  241--193  151--133--118--218  181  206  229  267--302--402--403--439                                              #
#                           |    |         |    |         |         |         |    |                                                                        #
#                           |    |         |    |         |         |         |    |                                                                        #
#      494--457--355--312--299  310  327--256  203  247--234--259  252  244--232  237--370  364--401--427--474                                              #
#                      |    |         |    |    |    |    |    |    |    |    |              |    |    |                                                    #
#                      |    |         |    |    |    |    |    |    |    |    |              |    |    |                                                    #
#                437--347  356  469--362  279  269  369  280  291  261  264  265--273--298--360  420  438                                                   #
#                      |    |         |    |    |              |    |    |    |    |              |    |                                                    #
#                      |    |         |    |    |              |    |    |    |    |              |    |                                                    #
#                393--375  405  423--395  323  315--335--378  306  345  290  268  296--308--337  464  448--490                                              #
#                      |    |                   |    |    |    |    |         |    |    |    |         |                                                    #
#                      |    |                   |    |    |    |    |         |    |    |    |         |                                                    #
#           493--478--413  432--473       410--406  346  466  415  409  322--276  382  317  383       475                                                   #
#                      |    |                             |         |    |    |    |    |    |         |                                                    #
#                      |    |                             |         |    |    |    |    |    |         |                                                    #
#                     419  449--450                      472--495  488  424  459  455  416  460       496                                                   #
#                                                         |                   |                                                                             #
#                                                         |                   |                                                                             #
#                                                   485--481                 467                                                                            #
#                                                                                                                                                           #
"""