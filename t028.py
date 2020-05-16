# t028.py

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

import sepir, matplotlib.pyplot as plt, random, numpy as np
from scipy.integrate import solve_ivp

def create_NPIs(start=150, R0=2.5, lower_bound=0.9, upper_bound=1.0, dt=5):
     NPIs = []
     t = start
     while R0>=1.0:
          factor = random.uniform(lower_bound,upper_bound)
          NPIs.append((t,factor))
          R0 *= factor
          t += random.randint(1,dt)
     return NPIs
          
def evolve(t0,t1,y,
           R0      = 2.5,
           N       = 5000000, 
           c       = 0.1, 
           alpha   = 0.25,   
           gamma   = 0.1,  
           delta   = 1,   
           epsilon = 0.15, 
           CFR1    = 2.0/100,  
           CFR0    = 1.0/100,  
           nICU    = 300,   
           pICU    = 1.25/100 ):
     return solve_ivp(sepir.dy, 
                     (t0,t1),
                     y,
                     args=(N, c, alpha,
                           sepir.get_beta(R0=R0,gamma=gamma,delta=delta,epsilon=epsilon),
                           gamma, delta, epsilon, CFR1, CFR0, nICU, pICU))

def change_R0(R0      = 2.5,
              t_range = (0,400),
              NPIs    = [(145,0.7),(150,0.8),(155,0.9),(160,0.75)],
              N       = 5000000,
              initial = 20,
              c       = 0.1, 
              alpha   = 0.25,   
              gamma   = 0.1,  
              delta   = 1,   
              epsilon = 0.15, 
              CFR1    = 2.0/100,  
              CFR0    = 1.0/100,  
              nICU    = 300,   
              pICU    = 1.25/100):
     t0 = t_range[0]
     t1 = NPIs[0][0]
     sols = [evolve(t0,t1,
                    [1-initial/N, initial/N, 0, 0, 0, 0, 0],
                    R0      = R0,
                    N       = N, 
                    c       = c, 
                    alpha   = alpha,   
                    gamma   = gamma,  
                    delta   = delta,   
                    epsilon = epsilon, 
                    CFR1    = CFR1,  
                    CFR0    = CFR0,  
                    nICU    = nICU,   
                    pICU    = pICU)]
     R0s  = [R0]
     for i in range(len(NPIs)-1):
          t0 = t1
          t1 = NPIs[i+1][0]
          R0*= NPIs[i][1]
          sols.append(evolve(t0,t1,[y[-1] for y in sols[-1].y],R0=R0,gamma=gamma,delta=delta,epsilon=epsilon))
          R0s.append(R0)
     t0 = t1
     t1 = t_range[1]
     R0*= NPIs[len(NPIs)-1][1]
     sols.append(evolve(t0,t1,[y[-1] for y in sols[-1].y],R0=R0,gamma=gamma,delta=delta,epsilon=epsilon))
     R0s.append(R0)
     return sols,R0s

def round(x,n=1000):
     return n*(x//n)

def get_ticks(y):
     mu = np.mean(y)
     sigma = np.std(y)
     return [round(min(y)),round(mu-sigma),round(mu),round(mu+sigma),round(max(y))]
     
if __name__=='__main__':
     import argparse, os

     parser = argparse.ArgumentParser('Model COVID19 evolution (see Transmission T-028: Sidney Redner on exponential growth processes)')
     parser.add_argument('--M',       type=int,   default=1000,     help='Number of runs for Monte Carlo simulation')
     parser.add_argument('--R0',      type=float, default=2.5,      help='Basic Reproduction number')
     parser.add_argument('--initial', type=int,   default=20,       help='Number of exposed people at start')
     parser.add_argument('--N',       type=int,   default=5000000,  help='Population size')
     parser.add_argument('--nICU',    type=int,   default=300,      help='Number of ICU beds')
     parser.add_argument('--end',     type=int,   default=400,      help='Number of days to be simulated')
     parser.add_argument('--c',       type=float, default=0.1,      help='Testing rate for symptomatic cases, per diem')
     parser.add_argument('--alpha',   type=float, default=0.25,     help='E to P transition rate, per diem')
     parser.add_argument('--gamma',   type=float, default=0.1,      help='I to R tranition, per diem')
     parser.add_argument('--delta',   type=float, default=1.0,      help='P to I, per diem')
     parser.add_argument('--epsilon', type=float, default=0.15,     help='Relative infectiousness')
     parser.add_argument('--CFR1',    type=float, default=2.0/100,  help='Case Fatality Rate for cases exceeding ICU max')
     parser.add_argument('--CFR0',    type=float, default=1.0/100,  help='Case Fatality Rate for cases under ICU max')
     parser.add_argument('--pICU',    type=float, default=1.25/100, help='Proportion of cases requiring ICU')
     parser.add_argument('--show',                default=False,    help='Show plots at end of run', action='store_true')
     parser.add_argument('--out',                 default='./figs', help='Pathname for output')
     parser.add_argument('--seed',    type=int,   default=None,     help='Seed for random number generator')
     parser.add_argument('--start',   type=int,   default=150,      help='Start applying NPIs')
     parser.add_argument('--dt',      type=int,   default=5,        help='Interval between NPIs')
     parser.add_argument('--average', type=float, default=0.95,     help='Average effect of an NPI on R0')
     
     args = parser.parse_args()

#    Monte Carlo simulation

     random.seed(args.seed)
     durations   = []
     mortalities = []
     peaks       = []
     infections  = []
     
     for i in range(args.M):
          sols,R0s=change_R0(t_range =(0,args.end),
                             R0      = args.R0,
                             NPIs    = create_NPIs(R0          = args.R0,
                                                   start       = args.start,
                                                   lower_bound = 2*args.average-1,
                                                   upper_bound = 1,
                                                   dt          = args.dt),
                             initial = args.initial,
                             N       = args.N,
                             c       = args.c, 
                             alpha   = args.alpha,   
                             gamma   = args.gamma,
                             delta   = args.delta,
                             epsilon = args.epsilon,
                             CFR1    = args.CFR1,  
                             CFR0    = args.CFR0,  
                             nICU    = args.nICU,   
                             pICU    = args.pICU)

#         Calculate number affected and mortality. Start by getting the last solution curve, 
#         last point in that curve.
          final_sequence   = sols[-1].y
          final_population = [final_sequence[j][-1]  for j in range(0,final_sequence.shape[0])]
#         Since people progress from Exposed to either recovered of dead, the final number of susceptibles
#         represents those who weren't affected.
          affected         = 1 - final_population[0]
#         Following on, anyone who was affacted either recoveres or dies, so re can compute number of deaths
          deaths           = affected - final_population[-1]-final_population[-2]
          mortalities.append(args.N*deaths)
          infections.append(args.N*affected)

#         We want to know when the infection peaks          
          ys               = [y for sol in sols for y in sepir.scale(sepir.aggregate(sol.y,selector=range(3,5)),N=args.N)]
          ts               = [t for sol in sols for t in sol.t]
          ipeak            = np.argmax(ys)
          peaks.append(ys[ipeak])
          durations.append(ts[ipeak])

          #mortalities.append((1-sepir.aggregate(sols[-1].y,selector=range(5,7))[-1])*args.N)

#    Plot results

     fig = plt.figure(figsize=(20,6))
     fig.suptitle(f'Duration and mortality: M={args.M}, average={args.average}')
     
     ax1 = plt.subplot(221)
     ax1.hist(durations)
     ax1.set_xlabel('Time to peak (days)')
     
     ax2 = plt.subplot(222)
     ax2.hist(mortalities)
     ax2.set_xlabel('Deaths')
     ax2.set_xticks(get_ticks(mortalities))
     
     ax3 = plt.subplot(223)
     ax3.hist(peaks)
     ax3.set_xlabel('Peak infections')
     ax3.set_xticks(get_ticks(peaks))
     
     ax4 = plt.subplot(224)
     ax4.hist(infections)
     ax4.set_xlabel('Infections')
     ax4.set_xticks(get_ticks(infections))     
     
     plt.savefig(os.path.join(args.out,'T028.png'))   
     
#    decide whether to display

     if args.show:
          plt.show()