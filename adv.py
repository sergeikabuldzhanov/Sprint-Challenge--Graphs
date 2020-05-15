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
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph = literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
# world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []
directions_map = {'n': 's', 's': 'n', 'w': 'e', 'e': 'w'}

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
        move_direction = unvisited[0]
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

graph = [[value for value in v.values() if value is not None]
         for k, v in sorted(visited.items(), key=lambda x: x[0])]


def find_depth(graph , node, visited_before = set()):
    """
    Polls the depth of the node and finds the longest path

    """
    queue = deque([([node], visited_before.copy())])
    max_path = [node]
    # find the max length
    while queue:
        current_path, current_visited = queue.popleft()
        # print(len(current_path), len(current_visited))
        current_node = current_path[-1]
        if len(current_path) > len(max_path):
            max_path = current_path
        for n in graph[current_node]:
            if n not in current_visited:
                new_visited = current_visited.copy()
                new_visited.add(n)
                new_path = current_path + [n]
                queue.append((new_path, new_visited))
    # figure if the path is a cycle, if it is, prioritise it
    isCycle = False
    # if we hit a node previously visited by the main path, we are in a cycle.
    for n in graph[max_path[-1]]:
        if n in visited_before:
            isCycle = True
    return max_path, node, isCycle

# print(find_depth( graph, 5, set([0,5])))

def bfs_closest_unvisited(graph, starting_vertex, visited_before = set()):
    """
    Return a list containing the shortest path from
    starting_vertex the closest visited node with unvisited neighbors.
    """
    visited = set()
    visited.add(starting_vertex)
    paths = deque()
    paths.appendleft([starting_vertex])
    # store a queue of paths
    while len(paths):
        path = paths.pop()
        # print(path)
        node = path[-1]
        # look at the current node
        # if it has been visited before, and has neighbors which have not been visited before
        # return path to that node
        if node in visited_before:
            neighbors_unvisited_by_main_path = [n for n in graph[node] if n not in visited_before]
            if len(neighbors_unvisited_by_main_path):
                # print(path)
                return path
        # else, continue bfs
        for adjacent in graph[node]:
            if adjacent not in visited:
                visited.add(node)
                new_path = path+[adjacent]
                paths.appendleft(new_path)

# print(bfs_closest_unvisited(graph, 0, set([0,1,3,5,7])))

def find_path(graph, starting_room):
    """
    Finds an approximate shortest path that visits
    all nodes in a graph, using the 'shallowest depth subgraph' heuristic.
    """
    # start with the given room, mark it as visited and add to the path
    # to attain the shortest path between all nodes, we need to minimise backtracking
    # if no backtracking was needed, a simple dfs would do the job.
    # the way to minimise backtracking seems to be to take the shortest paths first
    # you can see it in the test_loop.txt and test_loop_fork.txt maps.
    # thus, before every move we take, we need to test the maximum 'depth' of all the potential
    # paths we can take, without hitting an already visited node
    # and take the direction of the minimum 'depth' path.
    current_node = starting_room
    visited = set()
    path = []
    while len(visited)<len(graph):
        # print(current_node)
        path.append(current_node)
        # do a DFS while using depth polling to decide where to go next
        if current_node not in visited:
            visited.add(current_node)
        # get all the unvisited neighbors
        unvisited_neighbors = [n for n in graph[current_node]if n not in visited]
        # print(unvisited_neighbors)1
        # if it has any, poll them for depth and choose the shallowest as the next node in the path
        if unvisited_neighbors:
            shortest_path,current_node, isCycle = min([find_depth(graph, n, visited) for n in unvisited_neighbors], key=lambda x: len(x[0]))
            # print(shortest_path,current_node)
        # if there are no unvisited neighbors, we either hit a dead end
        # or we hit a previously visited part of the path. Which means there's a cycle in the graph
        # it means that now we have to backtrack until we find a node with unvisited neighbors.
        # for naive implementation, we could use a stack to store our path, and fill in the backtracking parts
        # but it would miss some of the edge cases, like  having a closed off loop in a graph.
        else:
            path_back = bfs_closest_unvisited(graph, current_node, visited)
            if path_back:
                path.extend(path_back[1:-1])
                current_node = path_back[-1]
        # print(len(path), len(visited))
    return path, len(path)

# print(find_path(graph, 0))
def convert_id_path_to_directions(id_path, direction_graph):
    direction_path = []
    for i in range(len(id_path)-1):
        current = id_path[i]
        target = id_path[i+1]
        direction = [direction for direction in direction_graph[current] if direction_graph[current][direction]==target]
        direction_path.extend(direction)
    return direction_path


# world.print_rooms()
traversal_path = convert_id_path_to_directions(find_path(graph, 0)[0], visited)
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
#                                        #
#      017       002       014           #
#       |         |         |            #
#       |         |         |            #
#      016--015--001--012--013           #
#                 |                      #
#                 |                      #
#      008--007--000--003--004           #
#       |         |                      #
#       |         |                      #
#      009       005                     #
#       |         |                      #
#       |         |                      #
#      010--011--006--018                #
#                                        #

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