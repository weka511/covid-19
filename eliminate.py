# eliminate.py

# Copyright (C) 2020 Greenweaves Software Limited

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.GA

# You should have received a copy of the GNU General Public License
# along with GNU Emacs.  If not, see <http://www.gnu.org/licenses/>.

import sepir
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import random

def create_NPIs(start=150,R0=2.5,lower_bound=0.9,upper_bound=0.99,dt=5):
     NPIs = []
     t = start
     while R0>=1.0:
          factor = random.uniform(lower_bound,upper_bound)
          NPIs.append((t,factor))
          R0 *= factor
          t += random.randint(1,dt)
     return NPIs
          
def evolve(t0,t1,y,R0):
     return solve_ivp(sepir.dy, 
                     (t0,t1),
                     y,
                     args=(5000, 0.1, 0.25,
                           sepir.get_beta(R0=R0,gamma=0.1,delta=1.0,epsilon=0.15),
                           0.1, 1.0, 0.15, 2/100, 1/100, 300, 1.25/100))

def change_R0(R0=2.5,t_range=(0,400),npis=[(145,0.7),(150,0.8),(155,0.9),(160,0.75)]):
     t0 = t_range[0]
     t1 = npis[0][0]
     sols = [evolve(t0,t1,[1-20/5000000, 20/5000000, 0, 0, 0, 0, 0],R0=R0)]
     R0s  = [R0]
     for i in range(len(npis)-1):
          t0 = t1
          t1 = npis[i+1][0]
          R0*= npis[i][1]
          sols.append(evolve(t0,t1,[y[-1] for y in sols[-1].y],R0=R0))
          R0s.append(R0)
     t0 = t1
     t1 = t_range[1]
     R0*= npis[len(npis)-1][1]
     sols.append(evolve(t0,t1,[y[-1] for y in sols[-1].y],R0=R0))
     R0s.append(R0)
     return sols,R0s


if __name__=='__main__':
     random.seed(None)
     for i in range(5):
          sols,R0s=change_R0(npis=create_NPIs())
          plt.figure()
          for sol,R0 in zip(sols,R0s):
               plt.plot(sol.t,sepir.aggregate(sol.y,selector=range(3,5)),label=f'{R0:.3f}')     
          plt.legend(title='R0')
     plt.show()