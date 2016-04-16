###############################################
# Calculate the turnover moments from BLS Data
##############################################

"""
Julien Pascal
Script that calculates the moments to match
and that draws a lot of graphs using mainly data 
from the BLS
"""

import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from more_itertools import unique_everseen
import pylab
import matplotlib.dates as mdates
from math import exp, log
import math
from datetime import date, timedelta as td
import statsmodels.api as sm
import scipy
from tabulate import tabulate
import csv
import statsmodels.formula.api as smm #OLS

#locate in the correct directory:
path = '/home/julien/master-s_thesis/data' #path to the data
path_figure = '/home/julien/master-s_thesis/figures/' #where to save the figures
path_table = '/home/julien/master-s_thesis/tables/' #where to save the tables
os.chdir(path) #locate in the folder with the data


def estimated_autocorrelation(x):
	"""
	http://stackoverflow.com/q/14297012/190597
	http://en.wikipedia.org/wiki/Autocorrelation#Estimation
	"""
	n = len(x)
	variance = x.var()
	x = x-x.mean()
	r = np.correlate(x, x, mode = 'full')[-n:]
	assert np.allclose(r, np.array([(x[:n-k]*x[-(n-k):]).sum() for k in range(n)]))
	result = r/(variance*(np.arange(n, 0, -1)))
	return result

#################################################
# Select what date to begin with and when to stop
starting_year = 1951 #first quarter 1951. starting point for the HWI
starting_month = 1
starting_date = date(starting_year, starting_month, 1)

stop_year = 2015 #third quarter 2010
stop_month = 7
stop_date = date(stop_year, stop_month, 1)


df = pd.read_csv("LNS.csv") # Date on employment and unemployment

# 1. Create a column with dates objects:
df['Date'] = 0
for i in range(0,len(df['Series ID'])):
	df.ix[i,'Date'] = date(df.ix[i,'Year'], df.ix[i,'Period'], 1)

#keep the selected time period: 
df = df.loc[df['Date'] <= stop_date]
df = df.loc[df['Date'] >= starting_date]

# 2. Create a vector with dates:
Year = df.loc[df['Series ID'] == 'LNS12000000','Year'].values
Month = df.loc[df['Series ID'] == 'LNS12000000','Period'].values

#Remark: indexing start at 0
dateList = []
for i in range(0,len(Year)):
    dateList.append(date(Year[i], Month[i], 1))
#############################
# EMPLOYMENT AND UNEMPLOYMENT
#############################
#Employed: LNS12000000
Employed = df.loc[df['Series ID'] == 'LNS12000000','Value']

#Unemployed: LNS13000000
Unemployed = df.loc[df['Series ID'] == 'LNS13000000','Value']

#Unemployed for less than 5 weeks : LNS13008396
U_5 = df.loc[df['Series ID'] == 'LNS13008396','Value']

#Unemployed for 5-14 Weeks: LNS13008756
U_15 = df.loc[df['Series ID'] == 'LNS13008756','Value']

#Unemployed for 27 Weeks and over: LNS13008636
U_27 = df.loc[df['Series ID'] == 'LNS13008636','Value']

# Unemployment rate:
Unemployment_rate =[]
Unemployment_rate =(Unemployed.values/(Unemployed.values+Employed.values))*100 

# Plot Employed, Unemployed: : 
fig, ax1 = plt.subplots() 
ax1.plot(dateList, Employed, color='r')
ax1.plot(dateList, Unemployed, color='g')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('Employed and unemployed in thousands', color='k')

ax2 = ax1.twinx()
#ax2.plot(dateList, Unemployment_rate, color='b')
#ax2.plot(dateList, Participation_rate, color='K', ls ='--')
ax2.set_ylabel('Unemployment rate', color='k' )

ax1.legend(['Employed', 'Unemployed'], loc='best', fancybox = True, framealpha=0.5)
ax2.fill_between(dateList, 0, Unemployment_rate, color='b', alpha=0.2)

ax2.legend(['Unemployment rate'], loc='best', fancybox = True, framealpha=0.5)

plt.savefig(path_figure + 'Unemployment_1948_2016')
plt.show()

#############################################
# Labor Force Participation Rate Statistics: 
############################################
# A. Participation rates:
Participation_rate = df.loc[df['Series ID'] == 'LNS11300000','Value'] #LNS11300000: all sex, 16 and older
Participation_men = df.loc[df['Series ID'] == 'LNS11300001','Value']  #LNS11300001: men, 16 and older
Participation_women = df.loc[df['Series ID'] == 'LNS11300002','Value'] #LNS11300001: women, 16 and older
Participation_16_19 = df.loc[df['Series ID'] == 'LNS11300012','Value']  #'LNS11300012: all sex, between  16 and 19

#B. Monthly recession data: 1 = month of recession
#Source: https://research.stlouisfed.org/fred2/series/USREC
recession_monthly = pd.read_csv("quarterly_recession_indicator.csv") #1 = recession

# keep only the dates inside the good interval:
# Create a column with dates objects:
recession_monthly['Date'] = 0
for i in range(0,len(recession_monthly['observation_date'])):
	recession_monthly.ix[i,'Date'] = date(recession_monthly.ix[i,'Year'], recession_monthly.ix[i,'Month'], 1)

#keep the selected time period: 
recession_monthly = recession_monthly.loc[recession_monthly['Date'] <= stop_date]
recession_monthly = recession_monthly.loc[recession_monthly['Date'] >= starting_date]

#keep only the dates for which recession = 1:
recession_monthly = recession_monthly.loc[recession_monthly['USRECQ'] == 1]

#create a vector of recession dates:
recession_vector_monthly = recession_monthly['Date'].values

# C. Data on discouraged workers from the OECD:
df_OECD = pd.read_csv('Incidence_of_discouraged_workers_OECD.csv')

# Keep series for women and men:
df_OECD = df_OECD.loc[df_OECD['SEX'] == 'MW',]

# Keep share of the population:
df_OECD = df_OECD.loc[df_OECD['Series'] == 'Share of population',]

Year_OECD = df_OECD['Time'].values
# Create a column with dates objects:
	#df_OECD['Date'] = 0
dateListOECD = []
for i in range(0,len(Year_OECD)):
	#df_OECD.ix[i,'Date'] = date(Year_OECD[i], 1, 1) 
	dateListOECD.append(date(Year_OECD[i], 1, 1))

#store the starting date of the discouraged workers series:
start_date_OECD = dateListOECD[0]
end_date_OECD = dateListOECD[len(Year_OECD)-1]

#D. Data on discouraged workers from the CPS:
# Stats on 1994
# LNU05026645: Monthly data; number in thousands
number_discouraged = df.loc[(df['Series ID'] == 'LNU05026645'),'Value']

start_date_discouraged = date(1994, 1, 1)
Unemployed_since_1994 = df.loc[(df['Series ID'] == 'LNS12000000') & (df['Date'] >= start_date_discouraged),'Value']
Employed_since_1994 =  df.loc[(df['Series ID'] == 'LNS13000000') & (df['Date'] >= start_date_discouraged),'Value']

share_discouraged_workers = (number_discouraged.values/(Unemployed_since_1994.values+Employed_since_1994.values))*100 


#################################################
# Plot Participation rate and discourage workers :
#################################################
fig, ax1 = plt.subplots() 
ax1.plot(dateList, Participation_rate, color='b')
ax1.plot(dateList, Participation_men, color='k')
ax1.plot(dateList, Participation_women, color='r')
ax1.plot(dateList, Participation_16_19, color='g')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('Participation rate', color='k')

#add recession vertical lines:
for i in range(0,len(recession_vector_monthly)):
	ax1.axvline(recession_vector_monthly[i], color='silver', linewidth = 2, zorder=0)

#ax2 = ax1.twinx()
##ax2.plot(dateListOECD, df_OECD['Value'], color='teal')
#ax2.set_ylabel('', color='teal' )
#ax2.fill_between(dateListOECD, 0, df_OECD['Value'], color='teal', alpha=0.3)

ax1.legend(['All persons','Men','Women','All persons between 16 and 19'], loc='lower center' , fancybox = True, framealpha=0.5)
#ax2.legend(['Share of discourage workers in the population'], loc='best' , fancybox = True, framealpha=0.5)

plt.savefig(path_figure +'Participation_rates')
plt.show()

########################################################
# Create plot showing the influence of discourage wokers
# The series on discourage workers starts only in 1994:
# Shorten the other series in consequence:
#######################################################
Participation_rate_short = df.loc[(df['Series ID'] == 'LNS11300000')&(df['Date'] >= start_date_discouraged ),'Value'] #LNS11300000: all sex, 16 and older
Participation_men_short = df.loc[(df['Series ID'] == 'LNS11300001') & (df['Date'] >= start_date_discouraged ),'Value']  #LNS11300001: men, 16 and older
Participation_women_short = df.loc[(df['Series ID'] == 'LNS11300002') & (df['Date'] >= start_date_discouraged ),'Value'] #LNS11300001: women, 16 and older
Participation_16_19_short = df.loc[(df['Series ID'] == 'LNS11300012') & (df['Date'] >= start_date_discouraged ),'Value']  #'LNS11300012: all sex, between  16 and 19

dateList_short = df.loc[(df['Series ID'] == 'LNS11300000')&(df['Date'] >= start_date_discouraged),'Date'] 

#keep only the dates for which recession = 1:
recession_monthly_short = recession_monthly.loc[(recession_monthly['USRECQ'] == 1) & (recession_monthly['Date'] >= start_date_discouraged )]

#create a vector of recession dates:
recession_vector_monthly_short = recession_monthly_short['Date'].values

fig, ax1 = plt.subplots() 
ax1.plot(dateList_short, Participation_rate_short, color='b')	
ax1.plot(dateList_short, Participation_men_short, color='k')
ax1.plot(dateList_short, Participation_women_short, color='r')
ax1.plot(dateList_short, Participation_16_19_short, color='g')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('Participation rate', color='k')

#add recession vertical lines:
for i in range(0,len(recession_vector_monthly_short)):
	ax1.axvline(recession_vector_monthly_short[i], color='silver', linewidth = 6, zorder=0,alpha=0.7)

ax2 = ax1.twinx()
ax2.plot(dateList_short, share_discouraged_workers, color='teal', linestyle = '--', alpha=0.8)
ax2.set_ylabel('Discouraged workers share', color='teal')

ax1.legend(['All persons','Men','Women','All persons between 16 and 19'], loc='lower left' , fancybox = True, framealpha=0.5)
ax2.legend(['Discouraged workers share \n (in % of total labor force) '], loc='upper right' , fancybox = True, framealpha=0.5)

plt.savefig(path_figure + 'Participation_and_discouragement')
plt.show()



# Plot unemployed by category:
plt.plot(dateList, U_5, color = 'b')
plt.plot(dateList, U_15, '--k')
plt.plot(dateList, U_27, color = 'r')

plt.title('Unemployed by duration in the US')
plt.legend(['Unemployed for less than 5 weeks', 'Unemployed for 5-14 weeks', 'Unemployed for 27 Weeks and over'], loc='best', fancybox = True, framealpha=0.5)
plt.savefig(path_figure + 'Unemployed_by_category')
plt.show()

#######################################
# Construct Exit Rate from Unemployment
#######################################
F_BLS = []
dateList2 = []
for i in range(0,len(Year)-1):
	F_BLS.append(1 - (Unemployed.values[i+1] - U_5.values[i+1])/Unemployed.values[i])
	dateList2.append(date(Year[i], Month[i], 1))

S_BLS = []
for i in range(0,len(Year)-1):
	S_BLS.append((U_5.values[i+1])/Employed.values[i])


plt.subplot(211)
plt.plot(dateList2, F_BLS, color = 'navy')
plt.fill_between(dateList2, 0, F_BLS, color='navy', alpha=0.2)

#plt.yscale('')
plt.title('Exit rate from unemployment')

plt.subplot(212)
plt.plot(dateList2, S_BLS, color = 'r')
plt.fill_between(dateList2, 0, S_BLS, color='r', alpha=0.2)

#plt.yscale('')
plt.title('Job destruction rate')
plt.savefig(path_figure + 'Turnover_rates_BLS')
plt.show()

#############################################################
# Construct Exit Rate from Unemployment for different workers:
#############################################################

# Number of unemployed workers with duration greater than 5:
U_5p = Unemployed.values - U_5.values

# Number of unemployed workers with duration greater than 15:
U_15p = Unemployed.values - U_5.values- U_15.values

U_27p = U_27.values

F_5 = []
F_15 = []
F_27 = []

for i in range(0,len(Year)):
	F_5.append(-4*log(U_5p[i]/Unemployed.values[i])/5)
	F_15.append(-4*log(U_15p[i]/Unemployed.values[i])/15)
	F_27.append(-4*log(U_27p[i]/Unemployed.values[i])/27)

# Plot unemployed by duration:
plt.plot(dateList, F_5, color = 'b')
plt.plot(dateList, F_15, '--k')
plt.plot(dateList, F_27, color = 'r')

plt.title('Exit rate from unemployment by duration')
plt.legend(['More than 5 weeks', 'More than 15 weeks ', 'More than 27 Weeks'], loc='best', fancybox = True, framealpha=0.5)
plt.savefig(path_figure +'Exit_rate_by_duration')
plt.show()

# Unemploylent by diploma:
# Less than a high school diploma LNS14027659
U1 = df.loc[df['Series ID'] == 'LNS14027659','Value']/100

#High school diploma: LNS14027660
U2 = df.loc[df['Series ID'] == 'LNS14027660','Value']/100

#(Seas) Unemployment Rate - Some College or Associate Degree, 25 yrs. & over: LNS14027689
U3 = df.loc[df['Series ID'] == 'LNS14027689','Value']/100

# Bachelor's degree and Higher: LNS14027662
U4 = df.loc[df['Series ID'] == 'LNS14027662','Value']/100

# Date for education
dateListEdu = []
for i in range(0,len(U1)):
    dateListEdu.append(date(df.loc[df['Series ID'] == 'LNS14027659','Year'].values[i],df.loc[df['Series ID'] == 'LNS14027659','Period'].values[i], 1))

# Plot unemployed by education:
plt.plot(dateListEdu, U1, color = 'b')
plt.plot(dateListEdu, U2, '--k')
plt.plot(dateListEdu, U3, color = 'r')
plt.plot(dateListEdu, U4, color = 'g')

#fill in between:
plt.fill_between(dateListEdu, U2, U1, color='b', alpha=0.2)
plt.fill_between(dateListEdu, U3, U2, color='k', alpha=0.2)
plt.fill_between(dateListEdu, U4, U3, color='r', alpha=0.2)
plt.fill_between(dateListEdu, 0, U4, color='g', alpha=0.2)

#plt.title('Unemployment educational attainment')
plt.legend(['Less than a High School Diploma', 'With a High School Diploma', 'Some College or Associate Degree','Bachelors Degree and Higher'], loc='best', fancybox = True, framealpha=0.5)
plt.savefig(path_figure + 'Unemployment_rate_by_education')
plt.show()

#Compute standard deviation of unemployment rate by education:
print(np.std(U1))
print(np.std(U2))
print(np.std(U3))
print(np.std(U4))

#Plot unemployment rate by education versus overall unemployment rate:

#keep the same years:
Unemployment_rate_selected_years  = []
for i in range(0,len(Year)):
	if date(Year[i], Month[i], 1) >= dateListEdu[0]: #keep the matching dates only
		Unemployment_rate_selected_years.append(Unemployment_rate[i]/100) #divide by 100 to be consistent with the other series

degree_line = []
for i in range(0,len(Unemployment_rate_selected_years)):
	degree_line.append(Unemployment_rate_selected_years[i])

plt.scatter(Unemployment_rate_selected_years, U1, color = 'b', alpha=0.5)
plt.scatter(Unemployment_rate_selected_years, U2, color = 'k', alpha=0.5)
plt.scatter(Unemployment_rate_selected_years, U3, color = 'r', alpha=0.5)
plt.scatter(Unemployment_rate_selected_years, U4, color = 'g', alpha=0.5)
#plt.scatter(Unemployment_rate_selected_years, degree_line, color = 'grey', alpha=0.2)
plt.legend(['Less than a High School Diploma', 'With a High School Diploma', 'Some College or Associate Degree','Bachelors Degree and Higher'], loc='best', fancybox = True, framealpha=0.5)
plt.xlabel('Overall unemployment rate')
plt.ylabel('Group specific unemployment rate')
plt.savefig(path_figure + 'Overall_vs_group_edu_u_rate')
plt.show()

#Calculate the variance of group specific unemployment levels
#and create a latek table:
table_std_group_unemployment = [['Std.', np.std(U1), np.std(U2), np.std( U3), np.std(U4)]]
print(tabulate(table_std_group_unemployment, headers=['', 'Less High School', 'High School D.', 'Some College or A. Degree', 'B. Degree and Higher'], floatfmt=".3f", tablefmt="latex"))

#save the table in a csv format:
with open(path_table + 'table_std_group_unemployment.csv', 'w') as csvfile:
	writer = csv.writer(csvfile)
	[writer.writerow(r) for r in table_std_group_unemployment]

#################################
#Data for productivity and wages:
#################################

#Load the data:
df2 = pd.read_csv("PRS.csv") 

#1. Create date objects:
df2['Date'] = 0 #initialization
for i in range(0,len(df2['Series ID'])):
	df2.ix[i,'Date'] = date(df2.ix[i,'Year'], df2.ix[i,'Month'], 1)

#2.keep the selected time period: 
df2 = df2.loc[df2['Date'] <= stop_date]
df2 = df2.loc[df2['Date'] >= starting_date]

# 1. Seasonally adjusted real value added in the non farm business sector, Index 2009=100: PRS85006043
Real_output = df2.loc[df2['Series ID'] == 'PRS85006043','Value'].values

# 2. Nonfarm Business Sector: Real Compensation Per Hour, Index 2009=100, Quarterly, Seasonally Adjusted
Real_compensation_hour = df2.loc[df2['Series ID'] == 'COMPRNFB','Value'].values

dateList3 = []
for i in range(0,len(Real_output)):
    dateList3.append(date(df2['Year'].values[i],df2['Month'].values[i], 1))


plt.plot(dateList3, Real_output , color = 'b')
plt.plot(dateList3, Real_compensation_hour, color = 'r')
plt.title('Real output and compensation in the non-farm business sector')
plt.legend(['Real output per person', 'Real compensation per hour'], loc='best', fancybox = True, framealpha=0.5)
plt.savefig(path_figure + 'Real_value_added_and_wages_raw_data')
plt.show()

#####################
# Data for vacancies
#####################
# Merge the help wanted index and JOLTS on data vacancies
# Based on the methodology from Lise and Robin (2014)


###############################################
# A. Load the vacancies data and do simple plot
###############################################
path_data = '/home/julien/Documents/COURS/5A/MASTER THESIS/Labor Market/Data/Data/'

#Help Wanted Index 1951 
#Source	: The Conference Board
#downloaded from http://www.econometricsociety.org/ecta/Supmat/9070_data and programs.zip. 
df_HWI = pd.read_stata(path_data + 'help_raw_m.dta')
#Adjust the units:
for i in range(0,len(df_HWI)):
	df_HWI.ix[i,'V'] = df_HWI.ix[i,'V']*100 #results in thousands vacancies

#JOLTS:
#source: http://data.bls.gov/
df_JOLTS = pd.read_csv(path_data + 'JOLTS.csv')
df_JOLTS = df_JOLTS.loc[df_JOLTS['Series ID'] == 'JTS00000000JOL'] #Keep only data on vacancy creation in the non farm sectors in thousands
#adjust the indexes:
new_indexes = []
for i in range(0,len(df_JOLTS)):
	new_indexes.append(i)

df_JOLTS  = df_JOLTS.set_index([new_indexes]) 

#Create date objects for both series;
df_JOLTS['Date'] = 0
for i in range(0,len(df_JOLTS['Series ID'])):
	df_JOLTS.ix[i,'Date'] = date(df_JOLTS.ix[i,'Year'], df_JOLTS.ix[i,'Month'], 1)

df_HWI['Date'] = 0
for i in range(0,len(df_HWI)):
	df_HWI.ix[i,'Date'] = date(df_HWI.ix[i,'year'], df_HWI.ix[i,'month'], 1)


dateList_HWI = []
Vacancies_HWI = []
for i in range(0,len(df_HWI)):
    dateList_HWI.append(date(df_HWI.ix[i, 'year'],df_HWI.ix[i, 'month'], 1))
    Vacancies_HWI.append(df_HWI.ix[i,'V']) 

dateList_JOLTS = []
Vacancies_JOLTS = []
for i in range(0,len(df_JOLTS)):
    dateList_JOLTS.append(date(df_JOLTS .ix[i, 'Year'],df_JOLTS.ix[i, 'Month'], 1))
    Vacancies_JOLTS.append(df_JOLTS.ix[i,'Value'])

plt.plot(dateList_JOLTS, Vacancies_JOLTS, color = 'r')
plt.plot(dateList_HWI, Vacancies_HWI, color = 'b')
plt.legend(['JOLTS','HWI'])
plt.show()

#########################
# B. Merge the two series
#########################

###############################################################
# A. Select the overlap period for both series: 12-2000, 7-2006
starting_year_overlap = 2000 #first quarter 1951
starting_month_overlap = 12
starting_date_overlap = date(starting_year_overlap, starting_month_overlap, 1)

stop_year_overlap = 2006 #third quarter 2010
stop_month_overlap = 7
stop_date_overlap = date(stop_year_overlap, stop_month_overlap, 1)

df_HWI_overlap = df_HWI.loc[(df_HWI['Date'] <= stop_date_overlap) & (df_HWI['Date'] >= starting_date_overlap)]

df_JOLTS_overlap = df_JOLTS.loc[(df_JOLTS['Date'] <= stop_date_overlap) & (df_JOLTS['Date'] >= starting_date_overlap)]

#should be of same length:
len(df_JOLTS_overlap) == len(df_HWI_overlap)

#Adjust indexes for both dataframes:
new_indexes = []
for i in range(0,len(df_JOLTS_overlap)):
	new_indexes.append(i)

df_JOLTS_overlap  = df_JOLTS_overlap.set_index([new_indexes]) 
df_HWI_overlap  = df_HWI_overlap .set_index([new_indexes]) 

#Merge both
df_ovelap_merged = pd.merge(df_HWI_overlap , df_JOLTS_overlap, on='Date')

plt.plot(df_JOLTS_overlap['Value'], color = 'r')
plt.plot(df_HWI_overlap['V'], color = 'b')
plt.legend(['JOLTS','HWI'])
plt.show()

##########################################
# B. Project the HWI into the JOLTS space:
# 'V': HWI
# 'Value': JOLTS
result_projection  = smm.ols(formula="V ~ Value", data=df_ovelap_merged).fit() #simple OLS
print(result_projection.summary())

intercept = result_projection.params[0]
beta = result_projection.params[1]

####################################################
# C. Predict the HWI values based on observed JOLTS:

#merge the complete HWI and JOLTS:
df_total_merged = pd.merge(df_HWI, df_JOLTS, how = 'outer', on=['Date'])

#Predict:
for i in range(0,len(df_total_merged)):
	if df_total_merged.ix[i,'Date'] >= starting_date_overlap: #Start predicting only in 12-2000
		df_total_merged.ix[i,'V'] = intercept + beta*df_total_merged.ix[i,'Value'] #Project on the JOLTS space
		df_total_merged.ix[i,'year'] = df_total_merged.ix[i,'Year']
		df_total_merged.ix[i,'month'] = df_total_merged.ix[i,'Month_y']


# Plot predicted and actual values
plt.plot(df_total_merged['Value'], color = 'r')
plt.plot(df_total_merged['V'], color = 'b') 
plt.legend(['JOLTS','HWI predicted'])
plt.show() #Visually check it makes sense

# Plot with only the predicted
#plt.plot(df_total_merged['V'], color = 'b')
plt.fill_between(df_total_merged['Date'].values, 0, df_total_merged['V'].values, color='k', alpha=0.4)
plt.legend(['Vacancies - thousands'])
plt.savefig(path_figure + 'Number_vacancies_monthly')
plt.show()


########################################
# Clean the merged dataframe and save it

#Change column names
df_total_merged=df_total_merged.rename(columns = {'V':'Vacancies_HWI_hat'}) #"hat" because starting in 2000, it was projected on the JOLTS space
df_total_merged=df_total_merged.rename(columns = {'Value':'Vacancies_JOLTS'}) #actual data from JOLTS
df_total_merged=df_total_merged.rename(columns = {'Month_x':'Month'}) #actual data from JOLTS

#Drop some useless columns:
df_total_merged = df_total_merged.drop('Series ID', 1)
df_total_merged = df_total_merged.drop('Year', 1)
df_total_merged = df_total_merged.drop('Period', 1)
df_total_merged = df_total_merged.drop('Month_y', 1)
df_total_merged = df_total_merged.drop('Description', 1)

df_total_merged.to_csv(path_table +'HWI_JOLTS_merged.csv')

# keep the same time frame as the other dataframes for coherence:
df_total_merged = df_total_merged.loc[df_total_merged['Date'] <= stop_date]
df_total_merged = df_total_merged.loc[df_total_merged['Date'] >= starting_date]


#####################
# HP Filter the Data:
#####################

################################################
# 0. Construct quarterly series for monthly data:
################################################

# Unemployment rate:
Unemployment_rate_quarterly = []
dateList4 = []
upper_index = math.floor(len(Unemployment_rate)/3) 
a = 0

for i in range(0,upper_index):
	#compute the mean for the quarter
	Unemployment_rate_quarterly.append((Unemployment_rate[a]+Unemployment_rate[a+1]+Unemployment_rate[a+2]+Unemployment_rate[a+3])/4)
	dateList4.append(dateList[a])
	a = a + 3

#Plot monthly vers quarterly to visually check the results:
#plt.plot(dateList, Unemployment_rate , color = 'b')
#plt.plot(dateList4, Unemployment_rate_quarterly, color = 'r')
#plt.show()

# Vacancies (in thousands):
Vacancies =  []
for i in range(0,len(df_total_merged)):
	Vacancies.append(df_total_merged.ix[i,'Vacancies_HWI_hat']) #monthly vacancies in thousands

Vacancies_quarterly = [] #initialize quarterly observations
upper_indexV = math.floor(len(Vacancies)/3) 
a = 0

for i in range(0,upper_indexV):
	#compute the mean for the quarter
	Vacancies_quarterly.append((Vacancies[a]+Vacancies[a+1]+Vacancies[a+2]+Vacancies[a+3])/4)
	a = a + 3

#Plot monthly vers quarterly to visually check the results:
plt.plot(dateList, Vacancies, color = 'b')
plt.plot(dateList4, Vacancies_quarterly, color = 'r')
plt.show()

#Scatter plot quarterly vacancies unemployment ratio:
plt.scatter(Unemployment_rate_quarterly, Vacancies_quarterly, color = 'b', alpha=0.5)
plt.xlabel('Unemployment rate %')
plt.ylabel('Vacancies in thousands')
plt.show()

########################################################
# 1st approach: take monthly average, as in Shimer 2005:
"""
# Exit rate from unemployment F_BLS:
F_BLS_quarterly = []
dateList5 = []
a = 0

for i in range(0,upper_index):
	#compute the mean for the quarter
	F_BLS_quarterly.append((F_BLS[a]+F_BLS[a+1]+F_BLS[a+2]+F_BLS[a+3])/4)
	dateList5.append(dateList2[a])
	a = a + 3

# job destruction rate S_BLS:
S_BLS_quarterly = []
a = 0

for i in range(0,upper_index):
	#compute the mean for the quarter
	S_BLS_quarterly.append((S_BLS[a]+S_BLS[a+1]+S_BLS[a+2]+S_BLS[a+3])/4)
	a = a + 3

"""

#############################################################
# 2nd approach: see Robin 2011
# Iteration of the monthly series to construct quarterly ones:

S_BLS_quarterly = []
F_BLS_quarterly = []
dateList5 = []
a = 0

for i in range(0,upper_index):
	F2_S = S_BLS[a+2]
	F2_F = F_BLS[a+2]
	F_S = S_BLS[a+1]
	F_F = F_BLS[a+1]
	S = S_BLS[a]
	F = F_BLS[a]
	# Quarterly job destruction rate S_BLS:
	S_BLS_quarterly.append(F2_S + (1 - F2_S - F2_F)*(F_S + (1 - F_S - F_F)*S)) #formula p1339
	dateList5.append(dateList2[a]) #store date
	# Quarterly job finding rate:
	F_BLS_quarterly.append(1 - S_BLS_quarterly[i] - (1 - S - F)*(1 - F_S - F_F)*(1 - F2_S - F2_F)) #formula p1339
	a = a + 3

# Plot this 2nd approach:
plt.subplot(2, 1, 1)
plt.plot(dateList5, F_BLS_quarterly, color = 'navy')
plt.fill_between(dateList5, 0, F_BLS_quarterly, color='navy', alpha=0.2)
plt.title('Quarterly job finding rate')

plt.subplot(2, 1, 2)
plt.plot(dateList5, S_BLS_quarterly, color = 'r')
plt.fill_between(dateList5, 0, S_BLS_quarterly, color='R', alpha=0.2)
plt.title('Quarterly job destruction rate')

plt.savefig(path_figure + 'Quarterly_job_finding_and_job_destruction_rates')
plt.show()


#############################################
# 1. log transformation of the quarterly data:
#############################################

log_Real_output = np.log(Real_output)

log_Real_compensation_hour = np.log(Real_compensation_hour)

log_Unemployment_rate = np.log(Unemployment_rate_quarterly) #Quarterly unemployment rate

log_F_BLS = np.log(F_BLS_quarterly)

log_S_BLS = np.log(S_BLS_quarterly)

log_Vacancies = np.log(Vacancies_quarterly) #Quarterly vacancies in thousands

###############
# 2. HP filter 
###############

# Choose the smoothing parameter:
smoothing_parameter = 2.5*math.pow(10,5) 
#smoothing_parameter = 1*math.pow(10,5) # as in Shimer 2005

# a. Real value added: 
cycle_Real_output, trend_Real_output = sm.tsa.filters.hpfilter(log_Real_output , smoothing_parameter)

# b. Real productivity per hour:
cycle_Real_compensation_hour, trend_Real_compensation_hour = sm.tsa.filters.hpfilter(log_Real_compensation_hour, smoothing_parameter)

# c. Unemployment rate:
cycle_Unemployment_rate, trend_Unemployment_rate = sm.tsa.filters.hpfilter(log_Unemployment_rate, smoothing_parameter)

# d. Job destruction rate S_BLS
cycle_S_BLS, trend_S_BLS = sm.tsa.filters.hpfilter(log_S_BLS, smoothing_parameter)

# e. Exit rate from unemployment F_BLS
cycle_F_BLS, trend_F_BLS = sm.tsa.filters.hpfilter(log_F_BLS, smoothing_parameter)

# f. Vacancies:
cycle_Vacancies, trend_Vacancies = sm.tsa.filters.hpfilter(log_Vacancies , smoothing_parameter)


#####################################
# 3. Exponentiate the detrended data: 
#####################################
exponentiated_cycle_Real_output = np.exp(cycle_Real_output)

exponentiated_cycle_Real_compensation_hour = np.exp(cycle_Real_compensation_hour)

exponentiated_cycle_Unemployment_rate = np.exp(cycle_Unemployment_rate)

exponentiated_cycle_F_BLS = np.exp(cycle_F_BLS)

exponentiated_cycle_S_BLS = np.exp(cycle_S_BLS)

exponentiated_cycle_Vacancies = np.exp(cycle_Vacancies)

##########################################
# 4.1 Plots the trend and cycle components:
##########################################

#####################
# a. Real Output: 
plt.subplot(2, 2, 1)
plt.plot(dateList3, log_Real_output, color="navy")
plt.title("Log Real Output")

plt.subplot(2, 2, 2)
plt.plot(dateList3, trend_Real_output, color="r",)
plt.title("Trend Component")

plt.subplot(2, 2, 3)
plt.plot(dateList3, cycle_Real_output, color="g")
plt.title("Cycle Component")

plt.subplot(2, 2, 4)
plt.plot(dateList3, exponentiated_cycle_Real_output, color="k")
plt.title("Exponentiated Cycle Component")
plt.savefig(path_figure + 'Detrend_output')
plt.show()


##############################
#b. Real productivity per hour:
plt.subplot(2, 2, 1)
plt.plot(dateList3, log_Real_compensation_hour, color="navy")

plt.subplot(2, 2, 2)
plt.plot(dateList3, trend_Real_compensation_hour, color="r",)
plt.title("Trend Component")

plt.subplot(2, 2, 3)
plt.plot(dateList3, cycle_Real_compensation_hour, color="g")
plt.title("Cycle Component")

plt.subplot(2, 2, 4)
plt.plot(dateList3, exponentiated_cycle_Real_compensation_hour, color="k")
plt.title("Exponentiated Cycle Component")
plt.show()

######################
#c. Unemployment rate:
plt.subplot(2, 2, 1)
plt.plot(dateList4, log_Unemployment_rate, color="navy")
plt.title("Log Quarterly Unemployment rate")

plt.subplot(2, 2, 2)
plt.plot(dateList4, trend_Unemployment_rate, color="r",)
plt.title("Trend Component")

plt.subplot(2, 2, 3)
plt.plot(dateList4, cycle_Unemployment_rate, color="g")
plt.title("Cycle Component")

plt.subplot(2, 2, 4)
plt.plot(dateList4, exponentiated_cycle_Unemployment_rate, color="k")
plt.title("Exponentiated Cycle Component")
plt.show()

#######################
# d. Job finding rate:
plt.subplot(2, 2, 1)
plt.plot(dateList5, log_F_BLS, color="navy")
plt.title("Log Quarterly Job Finding Rate")

plt.subplot(2, 2, 2)
plt.plot(dateList5, trend_F_BLS, color="r",)
plt.title("Trend Component")

plt.subplot(2, 2, 3)
plt.plot(dateList5, cycle_F_BLS, color="g")
plt.title("Cycle Component")

plt.subplot(2, 2, 4)
plt.plot(dateList5, exponentiated_cycle_F_BLS, color="k")
plt.title("Exponentiated Cycle Component")
plt.show()

#########################
# d. Job destruction rate:
plt.subplot(2, 2, 1)
plt.plot(dateList5, log_S_BLS, color="navy")
plt.title("Log Quarterly Job Destruction Rate")

plt.subplot(2, 2, 2)
plt.plot(dateList5, trend_S_BLS, color="r",)
plt.title("Trend Component")

plt.subplot(2, 2, 3)
plt.plot(dateList5, cycle_S_BLS, color="g")
plt.title("Cycle Component")

plt.subplot(2, 2, 4)
plt.plot(dateList5, exponentiated_cycle_S_BLS, color="k")
plt.title("Exponentiated Cycle Component")
plt.show()

###############
# e. Vacancies
plt.subplot(2, 2, 1)
plt.plot(dateList4, log_Vacancies, color="navy")
plt.title("Log Number of Vacancies in Thousands")

plt.subplot(2, 2, 2)
plt.plot(dateList4, trend_Vacancies, color="r",)
plt.title("Trend Component")

plt.subplot(2, 2, 3)
plt.plot(dateList4, cycle_Vacancies, color="g")
plt.title("Cycle Component")

plt.subplot(2, 2, 4)
plt.plot(dateList4, exponentiated_cycle_Vacancies, color="k")
plt.title("Exponentiated Cycle Component")
plt.show()


##########################################################################
#4.2 Plot the comovements of the Business cycle components with Real output
##########################################################################

conv = np.vectorize(mdates.strpdate2num('%Y-%m-%d')) #used to for plotting vertical lines

# load the quarterly recession data:
# source: https://research.stlouisfed.org/fred2
# NBER based Recession Indicators for the United States from the Period following the Peak through the Trough, +1 or 0, Quarterly, Not Seasonally Adjusted
recession = pd.read_csv("quarterly_recession_indicator.csv") #1 = recession

# keep only the dates inside the good interval:
# Create a column with dates objects:
recession['Date'] = 0
for i in range(0,len(recession['observation_date'])):
	recession.ix[i,'Date'] = date(recession.ix[i,'Year'], recession.ix[i,'Month'], 1)

#keep the selected time period: 
recession = recession.loc[recession['Date'] <= stop_date]
recession = recession.loc[recession['Date'] >= starting_date]

#keep only the dates for which recession = 1:
recession = recession.loc[recession['USRECQ'] == 1]
recession['Date'].values

#create a vector of recession dates:
recession_vector = recession['Date'].values

#########
#a. Wage:
plt.subplot(1, 1, 1)
plt.plot(dateList3, exponentiated_cycle_Real_output, color = 'k', linestyle = '--')
plt.plot(dateList3, exponentiated_cycle_Real_compensation_hour, color = 'navy')

plt.fill_between(dateList3, 1, exponentiated_cycle_Real_output, color='k',alpha=0.4)
plt.fill_between(dateList3, 1, exponentiated_cycle_Real_compensation_hour, color='navy', alpha=0.1)

#add recession vertical lines:
for i in range(0,len(recession_vector)):
	plt.axvline(recession_vector[i], color='silver', linewidth = 2, zorder=0)

plt.legend(['Real output', 'Real compensation per hour'], loc='best', fancybox = True, framealpha=0.7)
plt.savefig(path_figure + 'Cycle_wages_output')
plt.show()

#######################
#b. Unemployment rate:
plt.subplot(1, 1, 1)
plt.plot(dateList3, exponentiated_cycle_Real_output, color = 'k', linestyle = '--')
plt.plot(dateList4, exponentiated_cycle_Unemployment_rate, color = 'navy')

plt.fill_between(dateList3, 1, exponentiated_cycle_Real_output, color='k', alpha=0.4)
plt.fill_between(dateList4, 1, exponentiated_cycle_Unemployment_rate, color='navy', alpha=0.1)

#add recession vertical lines:
for i in range(0,len(recession_vector)):
	plt.axvline(recession_vector[i], color='silver', linewidth = 2, zorder=0)

plt.legend(['Real output', 'Unemployment rate'], loc='best', fancybox = True, framealpha=0.7)
plt.savefig(path_figure + 'Cycle_unemployment_output')
plt.show()

#####################
#C. Job finding rate:
plt.subplot(1, 1, 1)
plt.plot(dateList3, exponentiated_cycle_Real_output, color = 'k', linestyle = '--')
plt.plot(dateList5, exponentiated_cycle_F_BLS, color = 'navy')

plt.fill_between(dateList3, 1, exponentiated_cycle_Real_output, color='k', alpha=0.4)
plt.fill_between(dateList5, 1, exponentiated_cycle_F_BLS, color='navy', alpha=0.1)

#add recession vertical lines:
for i in range(0,len(recession_vector)):
	plt.axvline(recession_vector[i], color='silver', linewidth = 2, zorder=0)

plt.legend(['Real output', 'Job finding rate'], loc='best', fancybox = True, framealpha=0.7)
plt.savefig(path_figure + 'Cycle_job_finding_rate_output')
plt.show()

#########################
#D. Job destruction rate:
plt.subplot(1, 1, 1)
plt.plot(dateList3, exponentiated_cycle_Real_output, color = 'k', linestyle = '--')
plt.plot(dateList5, exponentiated_cycle_S_BLS, color = 'navy')

plt.fill_between(dateList3, 1, exponentiated_cycle_Real_output, color='k', alpha=0.4)
plt.fill_between(dateList5, 1, exponentiated_cycle_S_BLS, color='navy', alpha=0.1)

#add recession vertical lines:
for i in range(0,len(recession_vector)):
	plt.axvline(recession_vector[i], color='silver', linewidth = 2, zorder=0)

plt.legend(['Real output', 'Job destruction rate'], loc='best', fancybox = True, framealpha=0.7)
plt.savefig(path_figure + 'Cycle_job_destruction_rate_output')
plt.show()

##############
# E. Vacancies
plt.subplot(1, 1, 1)
plt.plot(dateList3, exponentiated_cycle_Real_output, color = 'k', linestyle = '--')
plt.plot(dateList4, exponentiated_cycle_Vacancies, color = 'navy')

plt.fill_between(dateList3, 1, exponentiated_cycle_Real_output, color='k', alpha=0.4)
plt.fill_between(dateList4, 1, exponentiated_cycle_Vacancies, color='navy', alpha=0.1)

#add recession vertical lines:
for i in range(0,len(recession_vector)):
	plt.axvline(recession_vector[i], color='silver', linewidth = 2, zorder=0)

plt.legend(['Real output', 'Job destruction rate'], loc='best', fancybox = True, framealpha=0.7)
plt.savefig(path_figure + 'Cycle_vacancies_output')
plt.show()

#################
# BEVERIDGE CURVE

plt.scatter(cycle_Unemployment_rate, cycle_Vacancies, color = 'b', alpha=0.5)
plt.xlabel('Unemployment')
plt.ylabel('Vacancies')
plt.savefig(path_figure + 'Beveridge_curve')
plt.show()

#######################
# 5. Compute some stats
#######################

#Mean:
mean_data = []
mean_data.append('') #productivity, normalized to 1
mean_data.append(np.mean(Unemployment_rate_quarterly)/100)#quarterly unemployment rate
mean_data.append(np.mean(F_BLS_quarterly)) #quarterly exit rate from unemployment
mean_data.append(np.mean(S_BLS_quarterly)) #quarterly job destruction rate
mean_data.append('') #quarterly vacancies created - in thousands
mean_data.append('') #wage, normalized to 1


#Standard deviation of quarterly observations:
std_data = []
std_data.append(np.std(cycle_Real_output))
std_data.append(np.std(cycle_Unemployment_rate))
std_data.append(np.std(cycle_F_BLS))
std_data.append(np.std(cycle_S_BLS))
std_data.append(np.std(cycle_Vacancies))
std_data.append(np.std(cycle_Real_compensation_hour))


#Skewness:
skew_data = []
skew_data.append(scipy.stats.skew(cycle_Real_output))
skew_data.append(scipy.stats.skew(cycle_Unemployment_rate))
skew_data.append(scipy.stats.skew(cycle_F_BLS))
skew_data.append(scipy.stats.skew(cycle_S_BLS))
skew_data.append(scipy.stats.skew(cycle_Vacancies))
skew_data.append(scipy.stats.skew(cycle_Real_compensation_hour))

#Kurtosis, Normal = 3
kurtosis_data = []
kurtosis_data.append(scipy.stats.kurtosis(cycle_Real_output, fisher=False))
kurtosis_data.append(scipy.stats.kurtosis(cycle_Unemployment_rate, fisher=False))
kurtosis_data.append(scipy.stats.kurtosis(cycle_F_BLS, fisher=False))
kurtosis_data.append(scipy.stats.kurtosis(cycle_S_BLS, fisher=False))
kurtosis_data.append(scipy.stats.kurtosis(cycle_Vacancies, fisher=False))
kurtosis_data.append(scipy.stats.kurtosis(cycle_Real_compensation_hour, fisher=False))

#Autocorrelation:
autocorrelation_data = []
autocorrelation_data.append(estimated_autocorrelation(cycle_Real_output)[1])
autocorrelation_data.append(estimated_autocorrelation(cycle_Unemployment_rate)[1])
autocorrelation_data.append(estimated_autocorrelation(cycle_F_BLS)[1])
autocorrelation_data.append(estimated_autocorrelation(cycle_S_BLS)[1])
autocorrelation_data.append(estimated_autocorrelation(cycle_Vacancies)[1])
autocorrelation_data.append(estimated_autocorrelation(cycle_Real_compensation_hour)[1])

#Correlation with production:
corr_prod_data = []
corr_prod_data.append(np.corrcoef(cycle_Real_output, cycle_Real_output)[0,1])
corr_prod_data.append(np.corrcoef(cycle_Unemployment_rate, cycle_Real_output[0:(len(cycle_Real_output)-1)])[0,1])#drop the last quarter for output so vectors have the same length
corr_prod_data.append(np.corrcoef(cycle_F_BLS, cycle_Real_output[0:(len(cycle_Real_output)-1)])[0,1]) #drop the last quarter for output so vectors have the same length
corr_prod_data.append(np.corrcoef(cycle_S_BLS, cycle_Real_output[0:(len(cycle_Real_output)-1)])[0,1]) #drop the last quarter for output so vectors have the same length
corr_prod_data.append(np.corrcoef(cycle_Vacancies, cycle_Real_output[0:(len(cycle_Real_output)-1)])[0,1])
corr_prod_data.append(np.corrcoef(cycle_Real_compensation_hour, cycle_Real_output)[0,1])


#Correlation with unemployment:
corr_unemployment_data = []
corr_unemployment_data.append(np.corrcoef(cycle_Real_output[0:(len(cycle_Real_output)-1)], cycle_Unemployment_rate)[0,1]) #drop the last quarter for output so vectors have the same length
corr_unemployment_data.append(np.corrcoef(cycle_Unemployment_rate, cycle_Unemployment_rate)[0,1])
corr_unemployment_data.append(np.corrcoef(cycle_F_BLS, cycle_Unemployment_rate)[0,1]) 
corr_unemployment_data.append(np.corrcoef(cycle_S_BLS, cycle_Unemployment_rate)[0,1])
corr_unemployment_data.append(np.corrcoef(cycle_Vacancies, cycle_Unemployment_rate)[0,1])
corr_unemployment_data.append(np.corrcoef(cycle_Real_compensation_hour[0:(len(cycle_Real_compensation_hour)-1)], cycle_Unemployment_rate)[0,1])

# Create a table:
table = [['Mean', mean_data[0], mean_data[1], mean_data[2], mean_data[3], mean_data[4], mean_data[5]], 
['Std', std_data[0], std_data[1], std_data[2], std_data[3], std_data[4], std_data[5]],
['Skewness', skew_data[0], skew_data[1], skew_data[2], skew_data[3], skew_data[4], skew_data[5]],
['Kurtosis', kurtosis_data[0], kurtosis_data[1], kurtosis_data[2], kurtosis_data[3], kurtosis_data[4], kurtosis_data[5]],	
['Autocorrelation', autocorrelation_data[0], autocorrelation_data[1], autocorrelation_data[2], autocorrelation_data[3], autocorrelation_data[4], autocorrelation_data[5]],
['Corr. with production', corr_prod_data[0], corr_prod_data[1], corr_prod_data[2], corr_prod_data[3], corr_prod_data[4], corr_prod_data[5]],
['Corr. with unemployment', corr_unemployment_data[0], corr_unemployment_data[1], corr_unemployment_data[2], corr_unemployment_data[3], corr_unemployment_data[4], corr_unemployment_data[5]]]

#print the table
print(tabulate(table, headers=['', 'Productivity', 'Unemployment rate', 'Exit rate from Un.', 'Job destruction rate', 'Vacancies', 'Wage'], floatfmt=".3f", tablefmt="latex"))

#save the table in a csv format:
with open(path_table + 'table_moments.csv', 'w') as csvfile:
	writer = csv.writer(csvfile)
	[writer.writerow(r) for r in table]

##############################################################################
# Variance covariance matrix of estimators used in Method of Simulated Moments:
# i.e. [mean_prod; std_prod; mean_unemployment; std_unemployment; kurtosis_unemployment; mean_exit_rate]; 
#moments_to_match = [cycle_Real_output, cycle_Real_output, cycle_Unemployment_rate, cycle_Unemployment_rate, cycle_Unemployment_rate, cycle_F_BLS]
#np.cov(moments_to_match)