#Brian Lloyd
#1/2017
#Finds a solution to a sliding puzzle with 15 pieces "123456789ABCDEF "
#Supports DFS, BFS, DLS, GBFS, and A*
import sys
from math import sqrt
from collections import deque
from heapq import heappush, heappop

class Direction:
    East, South, West, North = range(4)

class SearchMethod:
    BFS, DFS, GBFS,AStar, DLS = range(5)

def parseSearchMethod(inputSearch):
    if inputSearch == "bfs":
        return SearchMethod.BFS
    if inputSearch == "dfs":
        return SearchMethod.DFS
    if inputSearch == "dls":
        return SearchMethod.DLS
    if inputSearch == "gbfs":
        return SearchMethod.GBFS
    return SearchMethod.AStar

class Heuristic:
    Distance, OutOfPlace = range(2)

def parseHeuristic(inputString):
    if inputString == "h1":
        return Heuristic.OutOfPlace
    return Heuristic.Distance

# Swap two characters in a string;
def swap (s, i, j):
    #print("Swap i:" + str(i) + " J: " + str(j))
    if  len(s) -1  == j :
        return ''.join((s[:i], s[j], s[i + 1:j], s[i]))

    return ''.join((s[:i], s[j],s[i+1:j],s[i],s[j+1:]))


def calculateBoardPosition(state, character):
    pos = state.index(character)
    row = pos % dimension
    column = pos // dimension
    return [row, column]

def calculateMisplacedHeuristic(state):
    count = 0
    for i in range(0,len(state)):
        if (state[i] != goalState[i]):
            count += 1
    return count

def calculateDistanceHeuristic(state):
    total = 0
    for i in range(0,len(state)):
        # Get the goal row and column for character
        goalPosition = goalDict[state[i]]
        statePosition = calculateBoardPosition(state,state[i])
        #total = (goal row - state row) + (goal column - state column)
        total += abs(goalPosition[0] - statePosition[0]) + abs(goalPosition[1] - statePosition[1])
    return total

#Calculates the row and column for each character in the goal state and saves
# it to a dictionary to prevent recalculation
def calculateGoalDict():
    global goalDict
    global goalState
    for i in range(0, len(goalState)):
        goalDict[goalState[i]] = calculateBoardPosition(goalState,goalState[i])

#Tree node that represents a game state
class TreeNode:
    def __init__(self,parent,state, lastDirection):
        self.data = state
        self.lastDirection = lastDirection
        self.parent = parent
        self.depth = 0
        self.heuristic = 0
        if (parent != None):
            self.depth = self.parent.depth + 1

    #Comparison for matching heap sort tuples
    def __lt__(self, other):
        return self.data < other.data

    def addChild(self,data, lastDirection):
        node = TreeNode(self,data,lastDirection)
        return node

#Data structure for unexpanded nodes
class Fring:
    def __init__(self, searchMethod, heuristic):
        self.searchMethod = searchMethod
        self.size = 0
        self.maxSize = 0
        if searchMethod == SearchMethod.GBFS or searchMethod == SearchMethod.AStar:
            self.dataStore = []
        else:
            self.dataStore = deque()
        self.heuristic = heuristic

    def add(self, node):
        self.size += 1
        if self.maxSize < self.size:
            self.maxSize = self.size

        #Use a queue as a stack or queue
        if self.searchMethod != SearchMethod.AStar and self.searchMethod != SearchMethod.GBFS:
            self.dataStore.append(node)
        else:
            #Handle Heuristic
            nodeHeuristic = 0
            if self.heuristic == Heuristic.Distance:
                nodeHeuristic = calculateDistanceHeuristic(node.data)
            else:
                nodeHeuristic = calculateMisplacedHeuristic(node.data)
            if self.searchMethod == SearchMethod.AStar:
                nodeHeuristic += node.depth
            node.heuristic = nodeHeuristic
            #print("Adding to Heap: " + str(nodeHeuristic) + " State:" + node.data)
            # Use priority queue
            heappush(self.dataStore, (nodeHeuristic, node))

    def remove(self):
        if not self.dataStore:
            return None
        self.size -= 1
        if self.searchMethod == SearchMethod.BFS:
            return self.dataStore.popleft()
        if self.searchMethod == SearchMethod.DFS or self.searchMethod == SearchMethod.DLS:
            return self.dataStore.pop()
        #Priority Queue
        returnNode = heappop(self.dataStore)[1]
        #print("Heap Pop: " + str(returnNode.heuristic) + " State:" + returnNode.data)
        return returnNode

#Get the values
def expandNode(root):
    global numExpanded
    global numCreated
    global dimension
    #Use temp collection to manipulate how the nodes are added to the fring
    #DFS was running backwards (needs to start with right
    newNodes = deque()
    numExpanded += 1
    #print("Expanding ")
    lastDirection = root.lastDirection
    state = root.data
    pos = state.index(" ")
    #print("State:" + state + " Position: " + str(pos) + " Last Direction:" + str(root.lastDirection))
    # Move Right
    if (pos % dimension != (dimension - 1)) and lastDirection != Direction.West:
        newstate = swap(state,pos,pos+1)
        if newstate not in visited:
            visited.add(newstate)
            child = root.addChild(newstate, Direction.East)
            newNodes.append(child)
            #print("Right: " + newstate)

    # Move Down
    if (pos + dimension < len(initialState)) and lastDirection != Direction.North:
        newstate = swap(state,pos,pos+dimension)
        if newstate not in visited:
            visited.add(newstate)
            child = root.addChild(newstate, Direction.South)
            newNodes.append(child)
            #print("Down: " + newstate)

    #Move Left
    if (pos % dimension != 0)  and lastDirection != Direction.East:
        newstate = swap(state,pos-1, pos);
        if newstate not in visited:
            visited.add(newstate)
            child = root.addChild(newstate, Direction.West)
            newNodes.append(child)
            #print("Left: " +newstate)

    #Move UP
    if (pos - dimension >= 0) and lastDirection != Direction.South :
        newstate = swap(state,pos-dimension, pos)
        if newstate not in visited:
            visited.add(newstate)
            child = root.addChild(newstate, Direction.North)
            newNodes.append(child)
            #print("UP: " + newstate)

    #Add all nodes to the fring
    #BFS nodes added right, left
    while newNodes:
        numCreated += 1
        if fring.searchMethod == SearchMethod.DFS or fring.searchMethod == SearchMethod.DLS:
            #Add nodes in reverse order so that right is the first direction searched in DFS
            fring.add(newNodes.pop())
        else:
            #Add nodes in the order they were expanded
            fring.add(newNodes.popleft())


# Get command args
# Initial state
initialState = sys.argv[1].upper()
#print("Input InitialState:" + initialState)
# SearchMethod
inputSearch = parseSearchMethod(sys.argv[2].lower())
#print("Input Search:" + str(inputSearch))
# Option (depth for DLS, heuristic for GBFS and A*
option = None
depthLimit = None
if inputSearch == SearchMethod.DLS:
    depthLimit = int(sys.argv[3])
if inputSearch == SearchMethod.AStar or inputSearch == SearchMethod.GBFS:
    option = parseHeuristic(sys.argv[3].lower())

# Global Vars
goalState = "123456789ABCDEF "
goalState2 ="123456789ABCDFE "
fring = Fring(inputSearch, option)
visited = set()
dimension = int(sqrt(len(initialState)))
numCreated = 1
numExpanded = 0
maxFring = 0
#Calculate Goal Position Dict
goalDict = {}
calculateGoalDict()

root = TreeNode(None, initialState, None)
found = False

#Main
fring.add(root)
visited.add(root.data)
node = fring.remove()

while not node == None:
    if node.data == goalState or node.data == goalState2:
        found = True
        break
    if fring.searchMethod == SearchMethod.DLS:
        if node.depth == depthLimit:
            node = fring.remove()
            continue
    expandNode(node)
    node = fring.remove()

if found:
    print(str(node.depth) + ", " + str(numCreated) + ", " + str(numExpanded) + ", " + str(fring.maxSize))
else:
    print("-1, -1, -1, -1")
