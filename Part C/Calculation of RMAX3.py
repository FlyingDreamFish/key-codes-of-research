# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 11:25:55 2021

@author: 10467
"""
import netCDF4 as nc
import numpy as np
from osgeo import gdal,osr,ogr
import os
import glob

# For a given year and a certain date, judge the number of days the date falls in that year.
def judge_daynumber(year,month,day):
    months = (0,31,59,90,120,151,181,212,243,273,304,334)
    if 0 < month <= 12:
        sum = months[month - 1]
    else:
        print ('data error')
    sum += day
    leap = 0
    if (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0)):
        leap = 1
    if (leap == 1) and (month > 2):
        sum += 1
    return sum

#  Get all 21 nc model' names and return their paths for the given year
def search_match_file(year):
    for file in filenames:
        if file[-7:-3]==year:
            filepath=Input_folder+'\\'+file
            file_match.append(filepath)
    if len(file_match)==21:
        return file_match
    else:
        print('Search exception!')

# Read a nc model
def read_nc(path):
    nf = nc.Dataset(path)
    pr = nf.variables['pr'][:]
    data_pr = np.array(pr)
    return data_pr

# Get the precipitation data for 92 days between June 1 and August 31 in a nc model and return a list
def choose_time(starttime,endtime):
    for item in range(starttime,endtime):
        pre=data_pr[item]
        pre_row_r=pre[::-1]
        pre_row_r[pre_row_r[:,:]==1e+20]='NaN'# Set the missing value as Null
        pre_row_r_m=pre_row_r*86400 # Units converted from kg m-2 s-1 to mm
        target_pre=pre_row_r_m[238:252,456:472] # This is the position of the PLEEZ in the array. Consider modifying to your study area.
        target_list.append(target_pre) # Add each day's precipitation data of PLEEZ into a list.
    return target_list

# Calcute the RMAX3 for each pixel
def caculation(row,column):    
    # Store each daily value for a pixel in the lisf of "grid_list"
    for i in range(92):
        value=target_list[i][row][column]
        grid_list.append(value)
    # Calculate all the values of the 3-day rainfall for a pixel and 
    # select the maximum as the RMAX3 to store in the list of "plus_list"
    for index in range(len(grid_list)-2):
        plus_list.append(grid_list[index]+grid_list[index+1]+grid_list[index+2])
        max_value = max(plus_list)
    return max_value

# Transfrom a numpy array into tif format
def numpytotif(max_pre,tiffname):
    # Select the upper left and lower right coordinates of the PLEEZ. Please make changes according to your study area.
    LonMin,LatMax,LonMax,LatMin = [114.125,30.375,117.875,27.125]
    # Calculate the resolution
    N_Lat = max_pre.shape[0]
    N_Lon = max_pre.shape[1]
    Lon_Res = (LonMax - LonMin) /(float(N_Lon)-1)
    Lat_Res = (LatMax - LatMin) / (float(N_Lat)-1)
    # Create the tif
    driver = gdal.GetDriverByName('GTiff')
    out_tif_name = r'F:\Paper3_PoYang_202204\Main_material\内部修改\修改-Journal of Hydrology-20230505\Github上传材料\Part C\{}.tif'.format(tiffname) # Storage path of the generated tif
    out_tif = driver.Create(out_tif_name, N_Lon, N_Lat, 1, gdal.GDT_Float32)
    geotransform = (LonMin, Lon_Res, 0, LatMax, 0, -Lat_Res)
    out_tif.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out_tif.SetProjection(srs.ExportToWkt())
    out_tif.GetRasterBand(1).WriteArray(max_pre)
    out_tif.FlushCache()
    out_tif = None
    
if __name__ == '__main__':
    # Judge what day of the year June 1 is.
    year=2020
    month=6
    day=1
    startday=judge_daynumber(year,month,day)
    endday=startday+92
    # Get all the nc files' paths for the given year, that is 21 models' paths
    year_string=str(year)
    file_match=[]
    Input_folder = r'G:\GDDP-NEX-Prec\original\rcp45'
    filenames=os.listdir(Input_folder)
    match_nc_name=search_match_file(year_string)
    # Extract the RMAX3 for each nc model and transfrom into tif format.
    All_nc=[]
    for item in range(len(match_nc_name)):
        filename=match_nc_name[item]
        data_pr=read_nc(filename)
        target_list=[]
        grid_list=[]
        plus_list=[]
        # Construct a zero array for storing the RMAX3. 
        # Consider adjust the row and column number based on your own study area size.
        max_pre=np.zeros(shape=(14,16))
        # Get the specific model name
        tiffname=filename[44:-3]
        print('The {}th nc model named as {} starts the computing.'.format(item+1,tiffname))
        # Get the precipitation data for 92 days between June 1 and August 31
        target_list=choose_time(startday,endday)
        # Calculate the RMAX3 for each pixel and add each of them into the list "max_pre"
        for row in range(14):
            for column in range(16):
                max_value=caculation(row,column)
                print('The RMAX3 value in row {}, column {} was {} mm.'.format(row,column,max_value))
                max_pre[row][column]=max_value
                grid_list=[]
                plus_list=[]
        numpytotif(max_pre,tiffname)
        All_nc.append(max_pre)
        print('The {}th nc model named as {} has been computed.'.format(item,tiffname))
        print('-'*70)
        
    # Calculate the average RMAX3 for the 21 models
    value_list=[]
    average_list=np.zeros(shape=(14,16))
    print('The average RMAX3 of Year {} starts computing.'.format(year))
    for row in range(14):
        for column in range(16):
            for item in range(len(All_nc)):
                value=All_nc[item][row][column]
                value_list.append(value)
            average=np.mean(value_list)
            average_list[row][column]=average
            value_list=[] # Clear the list for next run
            print('The average RMAX3 value in row {}, column {} was {} mm.'.format(row,column,average))
    resultname=tiffname[:5]+'_'+tiffname[-4:]
    # Store the average RMAX3 tif
    numpytotif(average_list,resultname)
    print('The average RMAX3 of Year {} have been computed.'.format(year))
