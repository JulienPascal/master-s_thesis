[![Build Status](https://travis-ci.org/JulianPasc/Final-Project-Julien-Pascal.svg?branch=master)](https://travis-ci.org/JulianPasc/Final-Project-Julien-Pascal)

# Master's in Economics, Sciences Po Paris
## Master's thesis
## The Dynamics of Wage Inequality: A Search-and-matching Approach

This repository contains the replication files for my master's thesis. The determinants of wage inequality in a search-and-matching model are explored. The model designed Robin (2011) is estimated by the simulated method of moments using a differential evolution algorithm. Simulated data are used to analyse the relationship between the bargaining power of workers and the spread of the wage distribution. At business-cycle frequency, is the relative bargaining power of workers a major factor influencing the spread of the wage distribution? The present study shows that this is not the case. The structure of the code is presented in the flow chart below:

![myimage-alt-tag](https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/figures/Structure_code.png)
 

## Main elements of the model designed by Robin (2011):
This is a search-and-matching model with heterogeneous agents. Firms are assumed to be identical. Search is random and worker-firm associations are formed only when the match surplus is positive. Productivity shocks occur according to a Markov process. Following a shock in productivity, worker-firm pairs with negative surplus are destroyed. On-the-job search is permitted, and firms can make counter-offers to retain their workers. Wages are endogeneously determined according to a sequential auction model: unemployed workers are offered their reservation wage, while employed workers contacted by poaching firms are offered firms' reservation wage. Calibrated on the US labor market between 1951 and 2015, the model is able to replicated fairly well the variations in unemployment and wages. It also explains why low wages and high wages are more procycle than intermediate wages. 

## Stylized facts the U.S. Labor Market
###Monthly unemployment rate 1951 - 2015
![myimage-alt-tag](https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/figures/Unemployment_1948_2016.png)
Source:Author's calculations based on data from The Bureau of Labor Statistics. Series LNS12000000 and LNS13000000. generated by https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/src/Calculate_Moments.py

###Unemployment rate by educational attainment
![myimage-alt-tag](https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/figures/Overall_vs_group_edu_u_rate.png)Source: Source: Author's calculations based on data from The Bureau of Labor Statistics. Series LNS14027659, LNS14027660, LNS14027689 and LNS14027662. Notes: Series are not available prior 1992. generated by https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/src/Calculate_Moments.py

###Business cycle co-movements:
####Unemployment and productivity
![myimage-alt-tag](https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/figures/Cycle_unemployment_output.png)
Source:Author's calculations based on data from the Bureau of Labor Statistics and the National Bureau of Economic Research. Series LNS12000000 and LNS13000000 for unemployment rate; PRS85006043 for seasonally adjusted real output in the non-farm business sector; USRECM for recession periods. Notes: The data was successively log-transformed, HP-filtered with a smoothing parameter equal to 2.5\times10^{5}, detrended and exponentiated. The shaded areas represent the NBER-defined recessions. generated by https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/src/Calculate_Moments.py

####Wages and productivity
![myimage-alt-tag](https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/figures/Cycle_wages_output.png)Source:Author's calculations based on data from the Bureau of Labor Statistics and the National Bureau of Economic Research. Series PRS85006043 for seasonally adjusted real output in the non-farm business sector; COMPRNFB for seasonally adjusted real compensation per hour in the non-farm business sector; USRECM for recession periods. Notes: The data was successively log-transformed, HP-filtered with a smoothing parameter equal to 2.5\times10^{5}, detrended and exponentiated. The shaded areas represent the NBER-defined recessions. generated by https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/src/Calculate_Moments.py

###Empirical Moments
![myimage-alt-tag](https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/tables/moments_table.png)generated by https://github.com/JulianPasc/Final-Project-Julien-Pascal/blob/master/src/Calculate_Moments.py

### Requirements
## Julia
Julia Version 0.5.0-dev+3438, Commit a92c7ff, x86_64-linux-gnu. Until now, the code is not compatible with Julia version 0.4. To install Julia, see http://julialang.org/downloads/platform.html. The pacakges PyPlot, Distributions, StatsFuns, JLD, HDF5, NLopt, DataFrames, BlackBoxOptim and Copulas are required. They can be installed using the commange Pkg.add(name_of_package), except for the last one which can be obtained using Pkg.clone("https://github.com/floswald/Copulas.jl.git")

## Python
The part that estimates the empirical moments is a Python script. The following version was used: Python 3.5.1 |Anaconda 2.4.1 (64-bit)| (default, Dec  7 2015, 11:16:01) 
[GCC 4.4.7 20120313 (Red Hat 4.4.7-1)] on linux

## Before running the code
Paths are set up for my environment. You may want to adapt "path_main", which is the path in which the file "main.jl" is located. Change "path_main" in the following files: main.jl, calculate_moments.py, estimate_parameters.jl, test.jl, simulate_economy.jl, Bargaining_power_test.jl

## Updates:
Update 0:
- Code in Matlab

Update 1:
- Version that runs with Julia
- The value function iteration for the wages is slow (slightly more than 20 mn)

Update 2, 21/02/2016:
- Include two files that perform the estimation of the parameters by the Simulated Method of Moments: "estim_params.jl" and "objective_function.jl". To estimate the parameters, run "estim_params.jl"

Update 3, 10/03/2016:
-Include two files in python in the folder "Data" that calculate interesting moments for the model:
 - calculate_turnover_BLS.py HP filters the data and calculates the moments the model intends to match
 - calculate_volatility_wages.py calculate the volatility of the wage deciles
-The data necessary for the estimations is also in the folder "Data"

Update 4, 11/03/2016:
- Added some graphs that are produced by the files calculate_turnover_BLS.py and calculate_volatility_wages.py
[files removed since update 5]

Update 5, 16/04/2016:
- Major reorganization of the repository:
  - reorganize the repository with a structure "src; test; data; figures; surpluses"
  - move the matlab version in the folder "matlab_old"
  - create a main.jl file that rationalizes the code

Update 6, 18/04/2016:
 - Separate the analysis of the economy from its simulation 
 
Update 7, 26/04/2016:
- Correct one bug concerning the variable epsilon
- The package JLD has some issues with the version of Julia I am using (0.5.0-dev). I had to change the way objects are loaded
- Modify the way the parameters are estimated: 1st step, a global minimization algorithm; 2nd step, refinement using a local minimization routine

Update 8, 27/04/2016:
- Add the possibility of estimating the parameters using a simulated annealing approach. A function coded by Michael Creel following  Goffe, William L. (1996) "SIMANN: A Global Optimization Algorithm using Simulated Annealing " Studies in Nonlinear Dynamics & Econometrics Oct96, Vol. 1 Issue 3 is used. 

Update 9, 06/05/2016:
- Modification of the estimation procedure of the parameters: can choose between NLopt, Differential Evolution and Simulated Annealing; 1-step or 2-step approaches (optimal weighting matrix)
- Add a module "Bargaining_power_test.jl" that looks at the links between relative bargaining power of groups and wage inequality
- Need to slightly modify the code for the simulated annealing in the next update. Not functional in this version

Update 10, 06/05/2016:
- Add some rudimentary tests

Update 11, 20/05/2016:
- Improve the model "Bargaining_power_test.jl"
