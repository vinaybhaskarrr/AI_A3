import util 
from util import* 
from engine.const import Const
import random
import math

# Class: Estimator
#----------------------
# Maintain and update a belief distribution over the probability of a car being in a tile.
class Estimator(object):
    def __init__(self, numRows: int, numCols: int):
        self.belief = util.Belief(numRows, numCols) 
        self.transProb = util.loadTransProb() 
            
    ##################################################################################
    # [ Estimation Problem ]
    # Function: estimate (update the belief about a StdCar based on its observedDist)
    # ----------------------
    # Takes |self.belief| -- an object of class Belief, defined in util.py --
    # and updates it *inplace* based onthe distance observation and your current position.
    #
    # - posX: x location of AutoCar 
    # - posY: y location of AutoCar 
    # - observedDist: current observed distance of the StdCar 
    # - isParked: indicates whether the StdCar is parked or moving. 
    #             If True then the StdCar remains parked at its initial position forever.
    # 
    # Notes:
    # - Carefully understand and make use of the utilities provided in util.py !
    # - Remember that although we have a grid environment but \
    #   the given AutoCar position (posX, posY) is absolute (pixel location in simulator window).
    #   You might need to map these positions to the nearest grid cell. See util.py for relevant methods.
    # - Use util.pdf to get the probability density corresponding to the observedDist.
    # - Note that the probability density need not lie in [0, 1] but that's fine, 
    #   you can use it as probability for this part without harm :)
    # - Do normalize self.belief after updating !!

    ###################################################################################
    def estimate(self, posX: float, posY: float, observedDist: float, isParked: bool) -> None:
        # BEGIN_YOUR_CODE
        particles=1000
        m=self.belief.numRows
        n=self.belief.numCols
        mat=self.belief.grid
        list_pos=[]
        list_prob=[]
        for i in range(m):
            for j in range(n):
                if(mat[i][j]!=0):
                    list_pos.append([i,j])
                    list_prob.append(mat[i][j])
                    self.belief.setProb(i,j,0.0)
        random_pos=random.choices(list_pos,weights=list_prob,k=particles)

        # belief=[[0]*n]*m
        new_belief=Belief(m,n,value=0.0)
        dict=self.transProb
        for a in random_pos:
            list_pos2=[]
            list_prob2=[]
            for i in range(m):
                for j in range(n):
                    temp=dict.get(((a[0],a[1]),(i,j)))
                    if(temp!=None):
                        list_pos2.append([i,j])
                        list_prob2.append(temp)
            if len(list_pos2)!=0:
                rand=random.choices(list_pos2,weights=list_prob2,k=1)
                for b in rand:
                    dis=math.sqrt(((colToX(b[1])-posX)**2)+((rowToY(b[0])-posY)**2))
                    self.belief.addProb(b[0],b[1],pdf(dis,Const.SONAR_STD,observedDist))
            else:
                dis=math.sqrt(((colToX(a[1])-posX)**2)+((rowToY(a[0])-posY)**2))
                self.belief.addProb(a[0],a[1],pdf(dis,Const.SONAR_STD,observedDist))
        
        # self.belief.grid=belief
        # self.belief=new_belief
        self.belief.normalize()
        # print("fdsa")
        # print(self.belief.getSum())
        # END_YOUR_CODE
        return
  
    def getBelief(self) -> Belief:
        return self.belief

   