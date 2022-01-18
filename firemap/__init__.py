# -*- coding: utf-8 -*-
""" firemap
=====
This package provides functions to download annual fire frequencies from 
Google Earth Engine (i.e. number of months with active fires), based on 
monthly, global burned area maps derived with MODIS at a 500 m resolution. 
For details on the dataset, refer to the GEE's data catalog 
(https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MCD64A1). 
The download output is then used to derives spatial-temporal metrics that 
characterize pixel-level fire regimes:

The algorithm evaluates the fire regime of an area given GeoTiff images on 
annual fire occurrences. For every pixel, the algorithm will estimate the 
following metrics:
    
    * Fire Return Interval (FRI) - Mean number of years between firest
    * Min. return time (MRI1) - Minimum between-burn interval
    * Mean return time (MRI2) - Mean between-burn interval
    * Maximum return time (MRI3) - Maximum between-burn interval

The FRI is expressed as the quotient between the number of years with fires 
and the number of years in the time-series. Then, for each pixel, fire map 
uses Running Length Encoding (RLE) to break a time-series of fire occurrences 
(with 1 for "fire" and 0 for "unburnt") into segments of equal value. The 
length of segments corresponding to "unburnt" periods are used to calculate 
MRI1, MRI2, and MRI3.
Note: the algorithm was designed to download data with a maximum resolution 
of 1-km, which is limited by the quota imposed by GEE on the size of files 
that can be directly downloaded after processing. Applying this algorithm to 
larger files will require some modifications to the gee_download() function.
"""

from progress.bar import Bar
import urllib.request as ur
from os.path import join
from osgeo import gdal
import rasterio as rt
import numpy as np
import glob2 as g
import shutil
import rle
import os
import ee

def gee_download(data_path, year):
    
    """ Returns annaul 
 
    Sum and return the ages of your son and daughter
 
    Parameters
    ------------
        path: str
            Path to directory where to download the data
        path: str
            Year for which to download data
    Return
    -----------
        age : int
            The sum of your son and daughter ages. 
    """
    
    # connect to GEE
    ee.Initialize()
    
    #------------------------------------------------------------------------#
    bar = Bar('downloading data from GEE', max=162)
    #------------------------------------------------------------------------#
    
    ydir = os.path.join(data_path, year)
    if os.path.isdir(ydir) == False:
        os.mkdir(ydir)
    
    for x in range(0,18):
        
        for y in range(0,9):
            
            #================================================================#
            #
            #================================================================#
            
            # build name of zip file to download
            zfile = ydir + "{:02d}".format(x) + '-' + \
                "{:02d}".format(y) + '_' + year + '.zip'
            
            # build name of zip file to download
            zdir = ydir + "{:02d}".format(x) + '-' + \
                "{:02d}".format(y) + '_' + year
            
            #================================================================#
            #
            #================================================================#
            
            # output extent
            xmin = -180+(20*x)
            ymin = 90-(20*(y+1))
            xmax= -180+(20*(x+1))
            ymax = 90-(20*y)
            
            # boulding box to write
            geometry = ('[[' + str(xmin) + ' ,' + str(ymax) + 
                           '], [' + str(xmax) + ', ' + str(ymax) + 
                           '], [' + str(xmax) + ', ' + str(ymin) + 
                           '], [' + str(xmin) + ', ' + str(ymin) + ']]')
            
            # subset geometry
            geometry = ee.Geometry.Rectangle(xmin,ymin,xmax,ymax)
            
            #================================================================#
            #
            #================================================================#
            
            # read collection
            col = ee.ImageCollection('MODIS/006/MCD64A1').filterDate(
                year + '-01-01', year + '-12-31'
                ).filterBounds(geometry).select('BurnDate')
            
            #================================================================#
            #
            #================================================================#
            
            # boulding box to write
            geometry = ('[[' + str(xmin) + ' ,' + str(ymax) + 
                           '], [' + str(xmax) + ', ' + str(ymax) + 
                           '], [' + str(xmax) + ', ' + str(ymin) + 
                           '], [' + str(xmin) + ', ' + str(ymin) + ']]')
            
            def main(image):
                return image.expression('b("BurnDate") > 0').rename('burn')
            
            image = col.map(main).sum()
            
            # extract download link
            path = image.getDownloadUrl({'description':year, 'name':year, 
                                         'reducer':'mean', 'scale':1000, 
                                         'crs':'EPSG:4326', 'region':geometry})
            
            #================================================================#
            #
            #================================================================#
            
            # download file
            while os.path.isfile(zfile) == False:
                try:
                    ur.urlretrieve(path, zfile)
                except:
                    continue
            
            # create unziped directory
            if os.path.isfile(zdir) == False:
                os.mkdir(zdir)
            
            # unpack file into new directory
            shutil.unpack_archive(zfile, zdir)
            
            bar.next()
            print(str(x) + '-' + str(y))
            
            bar.next()
    
    bar.finish()
    
    #------------------------------------------------------------------------#
    bar = Bar('mosaic downloaded files', max=162)
    #------------------------------------------------------------------------#
    
    # list files
    files = g.glob(join(data_path, '**', '*.tif'))
    bar.next()
    
    iname = join(data_path, year, '.vrt')
    gdal.BuildVRT(iname, files)
    bar.next()
    
    oname = join(data_path, year, '.tif')
    gdal.Translate(iname, oname)
    bar.next()
    bar.finish()
    


def fire_regime(input_path, output_path):
    
    #------------------------------------------------------------------------#
    # list input images 
    #------------------------------------------------------------------------#
    
    files = sorted(g.glob(join(input_path, '*.tif')))
    
    #------------------------------------------------------------------------#
    # use first image as a reference and extract metadata
    #------------------------------------------------------------------------#
    
    p = rt.open(files[0]).meta.copy()
    p.update(dtype='float32', compress='deflate', predict=2, zlevel=9)
    
    #------------------------------------------------------------------------#
    bar = Bar('estimate Fire Recurrence Interval (FRI)', max=len(files)+2)
    #------------------------------------------------------------------------#
    
    # estimate sum of years with fires
    ia = np.zeros((p['height'],p['width']), dtype='uint8')
    for f in files:
        ia = ia + (rt.open(f).read(1) > 0).astype('uint8')
        bar.next()
    
    # find non-zero pixels
    px = np.where(ia > 0)
    
    # estimate average interval
    oa = np.zeros(ia.shape, dtype='float32')
    oa[px] = ia[px] / len(files)
    bar.next()
    
    #------------------------------------------------------------------------#
    # write fire regime image
    #------------------------------------------------------------------------#
    
    ods = rt.open(join(output_path, 'fire_recurrence_interval.tif'), 'w', **p)
    ods.write(oa, indexes=1)
    ods.close()
    bar.next()
    bar.finish()
    
    #------------------------------------------------------------------------#
    bar = Bar('evaluate intervals between fires', max=len(px[0])+len(files)+3)
    #------------------------------------------------------------------------#
    
    # use non-zero pixel indices to derive a new matrix with all years
    ia = np.zeros((len(px[0]),len(files)))
    for i in range(0,len(files)):
        ia[:,i] = rt.open(files[i]).read(1)[px]
        bar.next()
    
    # create empty ouput array
    oa = np.zeros((len(px[0]),3))
    
    # derive metrics on the longest time without fires
    for i in range(0,len(px[0])):
        unique_id, id_length = rle.encode(ia[i,:]) # find sequences
        ind = np.where(np.array(unique_id) == 0)
        if len(ind[0]) > 0:
            oa[i,0] = np.min(np.array(id_length)[ind]) # min. interval
            oa[i,1] = np.max(np.array(id_length)[ind]) # mean interval
            oa[i,2] = np.mean(np.array(id_length)[ind]) # max. interval
        
        bar.next()
        
    #------------------------------------------------------------------------#
    # write metrics
    #------------------------------------------------------------------------#
    
    # update metadata to reduce file size
    p.update(dtype='uint8')
    
    # assign estimate metric to output array
    fr = np.zeros((p['height'],p['width']), dtype='uint8')
    fr[px] = oa[:,0]
    
    # write output
    ods = rt.open(join(input_path, 'mininum_return.tif'), 'w', **p)
    ods.write(fr, indexes=1)
    ods.close()
    bar.next()
    
    # assign estimate metric to output array
    fr = np.zeros((p['height'],p['width']), dtype='uint8')
    fr[px] = oa[:,1]
    
    # write output
    ods = rt.open(join(input_path, 'maximum_return.tif'), 'w', **p)
    ods.write(fr, indexes=1)
    ods.close()
    bar.next()
    
    # assign estimate metric to output array
    fr = np.zeros((p['height'],p['width']), dtype='uint8')
    fr[px] = oa[:,2]
    
    # write output
    ods = rt.open(join(input_path, 'mean_return.tif'), 'w', **p)
    ods.write(fr, indexes=1)
    ods.close()
    bar.next()
    bar.finish()
