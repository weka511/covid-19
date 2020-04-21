# sepir-mc.py

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

class Person:
    def __init__(self):
        pass

class Exposed(Person):
    def __init__(self):
        super().__init__()
    def step(self):
        pass
        
N       = 5000000
NS      = N
NE      = 20
tmax    = 400
beta    = 0.2463
 
# Inject a few exposed individuals into the population

exposed = [Exposed() for i in range(NE)]
NS      = NS - len(exposed)

pre_symptomatic = []
infected        = []
recovered       = []
dead            = []

for i in range(tmax):
    newly_pre_symptomatic    = [e.step() for e in exposed] 
    newly_infected           = [p.step() for p in pre_symptomatic]
    newly_retired,newly_dead = [i.step() for i in infected]
    
