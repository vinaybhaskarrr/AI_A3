'''
Licensing Information: Please do not distribute or publish solutions to this
project. You are free to use and extend Driverless Car for educational
purposes. The Driverless Car project was developed at Stanford, primarily by
Chris Piech (piech@cs.stanford.edu). It was inspired by the Pacman projects.
'''
import util
import itertools
from turtle import Vec2D
from engine.const import Const
from engine.vector import Vec2d
from engine.model.car.car import Car
from engine.model.layout import Layout
from engine.model.car.junior import Junior
from configparser import InterpolationMissingOptionError
from util import*

# Class: Graph
# -------------
# Utility class
class Graph(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

# Class: IntelligentDriver
# ---------------------
# An intelligent driver that avoids collisions while visiting the given goal locations (or checkpoints) sequentially. 
class IntelligentDriver(Junior):

    # Funciton: Init
    def __init__(self, layout: Layout):
        self.burnInIterations = 30
        self.layout = layout 
        # self.worldGraph = None
        self.worldGraph = self.createWorldGraph()
        self.checkPoints = self.layout.getCheckPoints() # a list of single tile locations corresponding to each checkpoint
        self.transProb = util.loadTransProb()
        
    # ONE POSSIBLE WAY OF REPRESENTING THE GRID WORLD. FEEL FREE TO CREATE YOUR OWN REPRESENTATION.
    # Function: Create World Graph
    # ---------------------
    # Using self.layout of IntelligentDriver, create a graph representing the given layout.
    def createWorldGraph(self):
        nodes = []
        # edges = []
        # create self.worldGraph using self.layout
        numRows, numCols = self.layout.getBeliefRows(), self.layout.getBeliefCols()
        # edges=[[[]]*numCols]*numRows
        edges=[]
        for i in range(numRows):
            t=[]
            for j in range(numCols):
                t.append([])
            edges.append(t)

        print(len(edges[0][0]))
        # NODES #
        ## each tile represents a node
        nodes = [(x, y) for x, y in itertools.product(range(numRows), range(numCols))]
        # print(nodes)
        
        # EDGES #
        ## We create an edge between adjacent nodes (nodes at a distance of 1 tile)
        ## avoid the tiles representing walls or blocks#
        ## YOU MAY WANT DIFFERENT NODE CONNECTIONS FOR YOUR OWN IMPLEMENTATION,
        ## FEEL FREE TO MODIFY THE EDGES ACCORDINGLY.

        ## Get the tiles corresponding to the blocks (or obstacles):
        blocks = self.layout.getBlockData()
        blockTiles = []
        for block in blocks:
            row1, col1, row2, col2 = block[1], block[0], block[3], block[2] 
            # some padding to ensure the AutoCar doesn't crash into the blocks due to its size. (optional)
            row1, col1, row2, col2 = row1-1, col1-1, row2+1, col2+1
            blockWidth = col2-col1 
            blockHeight = row2-row1 

            for i in range(blockHeight):
                for j in range(blockWidth):
                    blockTile = (row1+i, col1+j)
                    blockTiles.append(blockTile)

        ## Remove blockTiles from 'nodes'
        nodes = [x for x in nodes if x not in blockTiles]
        tt=0
        for node in nodes:
            if tt<6:
                tt+=1
                print(edges)
            x, y = node[0], node[1]
            adjNodes = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
            
            # only keep allowed (within boundary) adjacent nodes
            adjacentNodes = []
            for tile in adjNodes:
                if tile[0]>=0 and tile[1]>=0 and tile[0]<numRows and tile[1]<numCols:
                    if tile not in blockTiles:
                        adjacentNodes.append(tile)
            # edges[x][y].append(adjacentNodes)
            print(len(adjacentNodes))
            for tile in adjacentNodes:
                edges[node[0]][node[1]].append(tile)
                if node[0]==0 and node[1]==0:
                    print("harsha")
                # edges[tile[0]][tile[1]].append(node)
                # edges.append((node, tile))
                # edges.append((tile, node))

        print(numCols,numRows)
        print(len(edges[0][0]))
        return Graph(nodes, edges)

    #######################################################################################
    # Function: Get Next Goal Position
    # ---------------------
    # Given the current belief about where other cars are and a graph of how
    # one can driver around the world, chose the next position.
    #######################################################################################
    def getNextGoalPos(self, beliefOfOtherCars: list, parkedCars:list , chkPtsSoFar: int):
        '''
        Input:
        - beliefOfOtherCars: list of beliefs corresponding to all cars
        - parkedCars: list of booleans representing which cars are parked
        - chkPtsSoFar: the number of checkpoints that have been visited so far 
                       Note that chkPtsSoFar will only be updated when the checkpoints are updated in sequential order!
        
        Output:
        - goalPos: The position of the next tile on the path to the next goal location.
        - moveForward: Unset this to make the AutoCar stop and wait.

        Notes:
        - You can explore some files "layout.py", "model.py", "controller.py", etc.
         to find some methods that might help in your implementation. 
        '''
        goalPos = (0, 0) # next tile 
        moveForward = True
        threashold_prob=0.02
        numRows, numCols = self.layout.getBeliefRows(), self.layout.getBeliefCols()
        curr_Pos = self.getPos() # the current 2D location of the AutoCar (refer util.py to convert it to tile (or grid cell) coordinate)
        currPos=[yToRow(curr_Pos[1]),xToCol(curr_Pos[0])]
        edges=self.worldGraph.edges
        print("fds")
        
        # BEGIN_YOUR_CODE 
        adj_mat=edges[currPos[0]][currPos[1]]
        abv_thres_list=[]
        print(len(adj_mat))
        if len(adj_mat)!=0:
            belief_sum=[0]*len(adj_mat)
            for belief in beliefOfOtherCars:
                for i in range(len(adj_mat)):
                    belief_sum[i]+=belief.grid[adj_mat[i][0]][adj_mat[i][1]]
            
            for i in range(len(belief_sum)):
                if(belief_sum[i]<=threashold_prob):
                    abv_thres_list.append(adj_mat[i])
        else:
            if (currPos[0]-1,currPos[1]) in self.worldGraph.nodes:
                abv_thres_list.append((currPos[0]-1,currPos[1]))
            if (currPos[0]+1,currPos[1]) in self.worldGraph.nodes:
                abv_thres_list.append((currPos[0]+1,currPos[1]))
            if (currPos[0],currPos[1]-1) in self.worldGraph.nodes:
                abv_thres_list.append((currPos[0],currPos[1]-1))
            if (currPos[0],currPos[1]+1) in self.worldGraph.nodes:
                abv_thres_list.append((currPos[0],currPos[1]+1))
            # for i in range(numRows):
            #     for j in range(numCols):
            #         if currPos in edges[i][j]:
            #             abv_thres_list.append((i,j))
        if len(abv_thres_list)==0:
            moveForward=False
        else:
            
            queue_list=[]
            visited=[]
            for i in range(numRows):
                t=[]
                for j in range(numCols):
                    t.append(0)
                visited.append(t)
            size=len(abv_thres_list)
            print("check")
            print(size)
            print(len(queue_list))
            for i in range(size):
                g=abv_thres_list[i]
                queue_list.append([g])
                visited[g[0]][g[1]]=1
            temp_goal=self.checkPoints[chkPtsSoFar]
            flag=True
            idx=-1
            while(flag):
                for i in range(size):
                    new_queue=[]
                    for a in queue_list[i]:
                        if(a==temp_goal):
                            flag=False
                            print(i)
                            idx=i
                            break
                        else:
                            visited[a[0]][a[1]]=1
                            for b in edges[a[0]][a[1]]:
                                if visited[b[0]][b[1]]==0:
                                    new_queue.append(b)
                    queue_list[i]=new_queue

                    if(flag==False):
                        break
                    # x=queue_list[i].pop(0)
                    # if(x==temp_goal):
                    #     flag=False
                    #     idx=i
                    #     break
                    # else:
                    #     for a in edges[x[0]][x[1]]:
                    #         queue_list[i].append(a)
            position=abv_thres_list[idx]
            goalPos=(colToX(position[1]),rowToY(position[0]))
                    

        # END_YOUR_CODE
        print(moveForward)
        return goalPos, moveForward

    # DO NOT MODIFY THIS METHOD !
    # Function: Get Autonomous Actions
    # --------------------------------
    def getAutonomousActions(self, beliefOfOtherCars: list, parkedCars: list, chkPtsSoFar: int):
        # Don't start until after your burn in iterations have expired
        if self.burnInIterations > 0:
            self.burnInIterations -= 1
            return[]
       
        goalPos, df = self.getNextGoalPos(beliefOfOtherCars, parkedCars, chkPtsSoFar)
        vectorToGoal = goalPos - self.pos
        wheelAngle = -vectorToGoal.get_angle_between(self.dir)
        driveForward = df
        actions = {
            Car.TURN_WHEEL: wheelAngle
        }
        if driveForward:
            actions[Car.DRIVE_FORWARD] = 1.0
        return actions
    
    