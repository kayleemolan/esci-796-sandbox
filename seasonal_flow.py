#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Calculate and display seasonal flow statistics.

This script reads a text-separated USGS RDB data file of daily average flow, 
then calculates discharge frequencies for each day of the year. Results 
are displayed in a plot and saved as a CSV file. 

Parameters
----------
infile_name : str
    The name of the file to be analyzed; must be in working directory 
outfile_name : str
    Name of the file where data should be saved
title : str
    Desired title for output figure
freq_vec : list of floats
    Frequency values to calculate and display 
"""

#%% Import libraries 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
 
#%% Input parameters
infile_name = "lamprey_daily.txt" 
outfile_name = "lamprey_freqs.csv" 
freq_vec = [0.1, 0.25, 0.5, 0.75, 0.9]
title = 'Lamprey River, NH'

#%% Load USGS daily discharge data using read_csv 
data = pd.read_csv(infile_name,delimiter="\t",comment='#',
                      na_values=['Bkw','Fld', 'Ice', 'Mnt', 'Rat', 'Zfl'])

# Slice the resulting data frame to remove USGS format codes in first row
data = data.iloc[1:]     
          
#%% Convert datetime column to dates, then set as index 
data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d %H:%M')
data.set_index(['datetime'], inplace = True)

#%% Wrangle discharge column 
# Identify which column contains discharge data using the USGS code for 
# discharge data, which is 00060. 
data = data.filter(like='00060',axis=1)  

# Two columns contain this code: the discharge data, and a second with text 
# flags about the discharge data. Keep the first column only (as a series)
data = data.iloc[:, 0]  
    
# Convert discharge data to numeric data 
data = pd.to_numeric(data) 

#%% Find first 10/1 and last 9/30 in record
startdate = data.loc[(data.index.month == 10) & (data.index.day == 1)].index[0]
enddate = data.loc[(data.index.month == 9) & (data.index.day == 30)].index[-1]

#%% Trim data to whole water years 
data = data[startdate:enddate]   # contains discharge data in cfs 

#%% Initialize empty data frame for results 
maxdoy = 366  # Maximum number of days in a year
dfcum = pd.DataFrame(np.full((maxdoy,len(freq_vec)),np.nan),
                     columns=freq_vec,index=np.arange(1,maxdoy+1))

#%% Average seasonal record over all years 
for freq in freq_vec:
    dfcum[freq] = data.groupby(data.index.dayofyear).quantile(freq)

#%% Create bonus rows containing NaN's in between each year 
newdates = pd.date_range(startdate,enddate,freq = 'Y')+pd.Timedelta(1, unit='hour')
newvalues = pd.Series(np.full(len(newdates),np.nan),index=newdates)

#%% Add bonus rows to data series (to avoid plotting overlap) 
data = pd.concat([data,newvalues])
data.sort_index(inplace = True)

#%% Plot time series of seasonal discharge
fig, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(data.index.dayofyear,data,'-',
        color = 'gray',label = 'Historical')
for freq in freq_vesc:
    ax.plot(dfcum[freq],'-', label = f'{freq*100:.0f}th')
ax.set_ylabel('Discharge (cfs)')
ax.set_xlabel('Day of year')
ax.set_xlim(left = 0, right = 366)
ax.set_yscale('log')
ax.legend()
ax.set_title(title)

#%% Save results to file 
dfcum.to_csv(outfile_name,sep=',')
