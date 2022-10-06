### Description
<p align="justify">
TAlgorithm to characterize global fire regimes using fire occurence data from Google Earth Engine. Given a list of years, the algorithm will derive annual, global maps of fire occurrences, depicting per-pixel counts of months with active fires. These are then translated into multi-temporal metrics that characterize the recurrence of fires:
</p>

<br>

* <i>Fire Return Interval (FRI) - </i>Mean number of years between fires
* <i>Min. return time (MRI1) - </i>Minimum between-burn interval
* <i>Mean return time (MRI2) - </i>Mean between-burn interval
* <i>Maximum return time (MRI3) - </i>Maximum between-burn interval

<br>
<p align="justify">
The FRI is expressed as the quotient between the number of years with fires and the number of years in the time-series. Then, for each pixel, the <i>firemap</i> algorithm uses Running Length Encoding (RLE) to break a time-series of fire occurrences (with 1 for "fire" and 0 for "unburnt") into segments of equal value. The length of segments corresponding to "unburnt" periods are used to calculate MRI1, MRI2, and MRI3. These calculations are based on monthly fire occurrence data data derived with MODIS. For details on the source data, <a href="https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MCD64A1">see its description in GEE's data catalog</a>.
</p>

<br>

<img src="example.png" style='display: block;margin-left: auto;margin-right: auto;width:100%;'>
<p align='center'>Global differences between <i>IFRI</i> (a), <i>MRI1</i> (b), <i>MRI2</i> (c), and <i>MRI3</i> (d)</p>

<br>

### How to use
<p align="justify">
<i>firemap</i> is not currently in PyPI, and therefore should be installed manually. To do so, please download the current repository as a zip file and use 
</p>
<br>

```python
pip install firemap.zip
```

<br>

### Requirements.
<p align="justify">
Given this algorithm uses GEE, some configuration work is inposed on the user. Specifically, one should follow the <a href="https://www.earthdatascience.org/tutorials/intro-google-earth-engine-python-api/">GEE api configuration tutorial<a/>, which grants access to data and computational resources.
</p>

<br>

### Desclaimer
<p align="justify">
At present, the algorithm works with arrays at a 1-km resolution, limited by: 1) GEE quotas on direct downloads, 2) memory requirements. This is meant to support my immediate needs, and scalability was not a priority concerned. Applying this algorithm at finer resolutions and for different spatial extents will require manual changes.
</p>
