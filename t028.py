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

import sepir, matplotlib.pyplot as plt, random, numpy as np, argparse, os
from scipy.integrate import solve_ivp

# create_NPIs
#
# Create a list of random reductions in R0, to be applied over a random set of (near) dates,
# which have the cumulative effect of reducing R0 below 1.

def create_NPIs(start=150, R0=2.5, lower_bound=0.9, upper_bound=1.0, dt=5):
     NPIs = []
     t = start
     while R0>=1.0:
          factor = random.uniform(lower_bound,upper_bound)
          NPIs.append((t,factor))
          R0 *= factor
          t += random.randint(1,dt)
     return NPIs

# evolve
#
# Evolve the state forward for a fixed time interval using fixed R0

def evolve(t0,t1,y,
           R0      = 2.5,      # Basic Reproduction number
           N       = 5000000,  # Population size
           c       = 0.1,      # Testing rate for symptomatic cases, per diem
           alpha   = 0.25,     # E to P transition rate, per diem 
           gamma   = 0.1,      # I to R transition, per diem
           delta   = 1,        # P to I, per diem
           epsilon = 0.15,     # relative infectiousness
           CFR1    = 2.0/100,  # case fatality rate for cases exceedinging ICU max 
           CFR0    = 1.0/100,  # case fatality rate for cases under ICU max
           nICU    = 300,      # number of ICU beds
           pICU    = 1.25/100, # proportion of cases requiring ICU
           atol    = 1e-7,
           rtol    = 1e-7):    # Maximum absolute error tolerance for ODE solver
     return solve_ivp(sepir.dy, 
                     (t0,t1),
                     y,
                     args=(N, c, alpha,
                           sepir.get_beta(R0=R0,gamma=gamma,delta=delta,epsilon=epsilon),
                           gamma, delta, epsilon, CFR1, CFR0, nICU, pICU),
                     atol=atol,
                     rtol=rtol)

# change_R0
#
# Evolve the state forward for a fixed time interval varying R0 by applying a series of NPIs 
def change_R0(R0      = 2.5,      # Initial value of Basic Reproduction number
              t_range = (0,400),  # Range of times (days)
              NPIs    = [],       # List od reductions to apply to R0 [(t1,f1),(t2,f2),...]
                                  # Apply factor f1 at time t1, etc.
              N       = 5000000,  # Population size
              initial = 20,       # Initial number exposed
              c       = 0.1,      # Testing rate for symptomatic cases, per diem
              alpha   = 0.25,     # E to P transition rate, per diem 
              gamma   = 0.1,      # I to R transition, per diem
              delta   = 1,        # P to I, per diem
              epsilon = 0.15,     # relative infectiousness
              CFR1    = 2.0/100,  # case fatality rate for cases exceedinging ICU max 
              CFR0    = 1.0/100,  # case fatality rate for cases under ICU max
              nICU    = 300,      # number of ICU beds
              pICU    = 1.25/100, # proportion of cases requiring ICU7
              rtol    = 1e-7,
              atol    = 1e-7):    # Maximum absolute error tolerance for ODE solver 
     
     # First evolve solution until it is time to apply the first NPI
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
                    pICU    = pICU,
                    atol    = atol,
                    rtol    = rtol)]
     # Now process each NPI in turn
     R0s  = [R0]
     for i in range(len(NPIs)-1):
          t0 = t1
          t1 = NPIs[i+1][0]
          R0*= NPIs[i][1]
          sols.append(evolve(t0,t1,
                             [y[-1] for y in sols[-1].y],
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
                             pICU    = pICU,
                             atol    = atol,
                             rtol    = rtol))
          R0s.append(R0)
     # Now we are at the end of NPEs, keep going with final R0     
     t0 = t1
     t1 = t_range[1]
     R0*= NPIs[len(NPIs)-1][1]
     sols.append(evolve(t0,t1,
                        [y[-1] for y in sols[-1].y],
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
                        pICU    = pICU,
                        atol    = atol,
                        rtol    = rtol))
     R0s.append(R0)

     return sols,R0s

# round
#
# Round number for display, e.g. to nearest thousand

def round(x,n=1000):
     return n*(x//n)

# get_ticks
#
# Used to etablish ticks for plot: max/min, mean, mean+/- sigma
def get_ticks(y):
     mu    = np.mean(y)
     sigma = np.std(y)
     return [round(min(y)),round(mu-sigma),round(mu),round(mu+sigma),round(max(y))]

# Get coefficient of variation

def get_cv(y):
     return np.std(y)/np.mean(y)

def plot_details(sols,out='./figs',plot='details.png',indices=[3,4]):
     plt.figure(figsize=(20,6))
     for i in indices:
          plt.plot([t for sol in sols for t in sol.t],
                   [sol.y[i][j] for sol in sols for j in range(len(sol.t))],
                   label=sepir.names[i])
     plt.legend() 
     plt.savefig(os.path.join(out, plot))
    
     plt.close()
     
def parse_args():
     parser = argparse.ArgumentParser('Model COVID19 evolution (see Transmission T-028: Sidney Redner on exponential growth processes)')
     parser.add_argument('--M',         type=int,   default=1000,       help='Number of runs for Monte Carlo simulation')
     parser.add_argument('--R0',        type=float, default=2.5,        help='Initial value of Basic Reproduction number. This will be reduced to below 1.0 by applying NPIs.')
     parser.add_argument('--initial',   type=int,   default=20,         help='Number of exposed people at start of simulation.')
     parser.add_argument('--N',         type=int,   default=5000000,    help='Population size.')
     parser.add_argument('--nICU',      type=int,   default=300,        help='Number of ICU beds.')
     parser.add_argument('--end',       type=int,   default=400,        help='Number of days to be simulated.')
     parser.add_argument('--c',         type=float, default=0.1,        help='Testing rate for symptomatic cases, per diem.')
     parser.add_argument('--alpha',     type=float, default=0.25,       help='E to P transition rate, per diem.')
     parser.add_argument('--gamma',     type=float, default=0.1,        help='I to R tranition, per diem.')
     parser.add_argument('--delta',     type=float, default=1.0,        help='P to I, per diem.')
     parser.add_argument('--epsilon',   type=float, default=0.15,       help='Relative infectiousness.')
     parser.add_argument('--CFR1',      type=float, default=2.0/100,    help='Case Fatality Rate for cases exceeding ICU max.')
     parser.add_argument('--CFR0',      type=float, default=1.0/100,    help='Case Fatality Rate for cases under ICU max.')
     parser.add_argument('--pICU',      type=float, default=1.25/100,   help='Proportion of cases requiring ICU.')
     parser.add_argument('--show',                  default=False,      help='Show plots at end of run.', action='store_true')
     parser.add_argument('--out',                   default='./figs',   help='Pathname for plot file.')
     parser.add_argument('--plot',                  default='T028.png', help='Plot file name.')
     parser.add_argument('--seed',      type=int,   default=None,       help='Seed for random number generator.')
     parser.add_argument('--start',     type=int,   default=150,        help='Start applying NPIs.')
     parser.add_argument('--dt',        type=int,   default=5,          help='Average interval between NPIs.')
     parser.add_argument('--average',   type=float, default=0.95,       help='Average effect of an NPI on R0.')
     parser.add_argument('--tolerance', type=float, default=1e-6,       help='Tolerance for exposed, presymptomatic and '
                                                                           'infected at end of run. If any of these exceed'
                                                                           ' tolerance, run will be discarded from plots.')
     parser.add_argument('--atol',      type=float, default=1e-9,      help='Absolute tolerance for ode solver')
     parser.add_argument('--rtol',      type=float, default=1e-9,      help='relative tolerance for ode solver')
     parser.add_argument('--details',   type=int,   default=None,      help='Produce detailed plots for debugging', nargs='+')
     return parser.parse_args()

if __name__=='__main__':
      
     args=parse_args()
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
                                                   dt          = 2*args.dt),
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
                             pICU    = args.pICU,
                             atol    = args.atol,
                             rtol    = args.rtol)
          
          #  Calculate number affected and mortality. Start by getting the last solution curve, 
          #  last point in that curve.
          final_sequence   = sols[-1].y
          final_population = [final_sequence[j][-1]  for j in range(0,final_sequence.shape[0])]
          
          # Make sure population has stabilized  
          if abs(max(final_population[i] for i in [sepir.Indices.EXPOSED.value,
                                                   sepir.Indices.PRE_SYMPTOMATIC.value,
                                                   sepir.Indices.INFECTIOUS_UNTESTED.value,
                                                   sepir.Indices.INFECTIOUS_TESTED.value])) < args.tolerance: 
               
     #         Since people progress from Exposed to either Recovered or Dead, the final number of Susceptibles
     #         represents those who weren't affected at all.
               affected         = 1 - final_population[sepir.Indices.SUSCEPTIBLE.value]
               infections.append(args.N*affected)
               
     #         Following on, anyone who was affected either recoveres or dies, so we can compute number of deaths
               deaths           = affected - final_population[sepir.Indices.RECOVERED_UNTESTED.value] - \
                                             final_population[sepir.Indices.RECOVERED_TESTED.value]          
               mortalities.append(args.N*deaths)

     
     #         We want to know when the infection peaks          
               ys    = [y for sol in sols for y in sepir.scale(sepir.aggregate(sol.y,
                                                                               selector=[sepir.Indices.INFECTIOUS_UNTESTED.value,
                                                                                         sepir.Indices.INFECTIOUS_TESTED.value]),
                                                               N=args.N)]
               ts    = [t for sol in sols for t in sol.t]
               ipeak = np.argmax(ys)
               peaks.append(ys[ipeak])
               durations.append(ts[ipeak])
               if args.details!=None:
                    plot_details(sols,out=args.out,plot=f'details{i}.png',indices=args.details)
          else:
               print (f'Final population of simulation {i} outside tolerance {args.tolerance}: results discarded.')

#    Plot results

     fig = plt.figure(figsize=(20,6))
     fig.suptitle(f'Duration and mortality: M={args.M}, average={args.average}')
     
     ax1 = plt.subplot(221)
     ax1.hist(durations,color='c')
     ax1.set_xlabel(f'Time to peak (days): CV={get_cv(durations):.2}')
     
     #ax2 = plt.subplot(222)
     #ax2.hist(mortalities,color='c')
     #ax2.set_xlabel(f'Deaths: CV={get_cv(mortalities):.2}')
     #ax2.set_xticks(get_ticks(mortalities))
     
     ax3 = plt.subplot(223)
     ax3.hist(peaks,color='c')
     ax3.set_xlabel(f'Peak infections: CV={get_cv(peaks):.2}')
     ax3.set_xticks(get_ticks(peaks))
     
     ax4 = plt.subplot(224)
     ax4.hist(infections,color='c')
     ax4.set_xlabel(f'Infections: CV={get_cv(infections):.2}')
     ax4.set_xticks(get_ticks(infections))     
     
     plt.savefig(os.path.join(args.out, args.plot))   
     
#    decide whether to display
     if args.show:
          plt.show()