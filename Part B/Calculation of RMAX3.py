# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 11:13:25 2021

@author: Kezhen Yao
"""
from osgeo import gdal
import sys
import numpy as np
import os

# Read all tifs' names for a given folder
def get_tif_name(filepath): 
    Tifnames=os.listdir(filepath)
    Tifnames.sort(key=lambda x:int(x[4:-4])) 
    return Tifnames

# Read a tif and transform it as a numpy array
def load_tif_to_array(tifname):
    dataset=gdal.Open(tifname)
    # Judge if there  a tif exsits for this path
    if dataset is None:
        print('No such file: {}.tif'.format(tifname))
        sys.exit(1)
    tif_array=dataset.ReadAsArray()
    projection = dataset.GetProjection()
    transform = dataset.GetGeoTransform()
    return tif_array,projection,transform

# Calcute the RMAX3 for each pixel
def caculation(row,column,dimension):    
    # Store each daily value for a pixel in the lisf of "grid_list"
    for i in range(dimension):
        value=tifarray_list[i][row][column]
        grid_list.append(value)
    # Calculate all the values of the 3-day rainfall for a pixel and 
    # select the maximum as the RMAX3 to store in the list of "plus_list"
    for index in range(len(grid_list)-2):
        plus_list.append(grid_list[index]+grid_list[index+1]+grid_list[index+2])
        max_value = max(plus_list)
    index=plus_list.index(max(plus_list))
    # Print the date of the RMAX3 for the pixel
    print('The date when RMAX3 occured in row {}, column {} was day {} to {}.'.format(row,column,index+1,index+3))
    return max_value

# Transfrom a numpy array into tif format
def numpyto_tif(img_array,store_path,projection,transform):
    row=img_array.shape[0]
    column=img_array.shape[1]
    dim=1
    driver=gdal.GetDriverByName('GTiff')
    dst_ds=driver.Create(store_path,column,row,dim,gdal.GDT_Float32)
    dst_ds.SetProjection(projection)
    dst_ds.SetGeoTransform(transform)
    dst_ds.GetRasterBand(1).WriteArray(img_array)
    dst_ds.FlushCache()
    dst_ds=None

if __name__ == '__main__':
    tifarray_list=[]
    grid_list=[]
    plus_list=[]
    # Read all tifs' names for the "CHIRPS_2020_1KM" folder
    Tifnames=get_tif_name(r'\Please modify this path according to your own set!\Step2\CHIRPS_2020_1KM')
    # Transform each tif into a numpy array and then add it into the list of "tifarray_list"
    for tifname in Tifnames:
        tifname='\Please modify this path according to your own set!\Step2\CHIRPS_2020_1KM\\'+tifname
        tif_array,projection,transform=load_tif_to_array(tifname)
        tifarray_list.append(tif_array)
    # Construct a array to store the RMAX3 for each pixel
    row_number=tifarray_list[0].shape[0]
    column_number=tifarray_list[0].shape[1]
    max_pre=np.zeros(shape=(row_number,column_number))
    dimension=len(tifarray_list)
    # Calculate the RMAX3 for each pixel and add each of them into the list "max_pre"
    for row in range(row_number):
        for column in range(column_number):
            max_value=caculation(row,column,dimension)
            print('The RMAX3 value in row {}, column {} was {} mm.'.format(row,column,max_value))
            print('-'*70)
            max_pre[row][column]=max_value
            grid_list=[] # clear the list for next run
            plus_list=[] # clear the list for next run
    # Transform the RMAX3 array into a new tif representing the RMAX3 of 2020
    store_path=r'Please modify this path according to your own set!\Pre_2020.tif'
    numpyto_tif(max_pre,store_path,projection,transform)
