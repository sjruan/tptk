# TPTK - Trajectory Preprocessing Toolkit

TPTK is a trajectory preprocessing toolkit in Python.

Note that, this is only my personal implementation. For the industrial level quality and efficiency, you're welcome to try our product [JUST](http://just.urban-computing.cn/ "京东城市时空数据引擎"). 

Currently, TPTK serves as a basic library of [DeepMG](https://github.com/sjruan/DeepMG).

## Features

* Data Structures
    * SPoint
        * The fundamental spatial point class
    * MBR
        * Minimum bounding box
    * Trajectory
        * A sequence of time-ordered spatio-temporal points
    * Directed & Undirected Road Network
        * A custom class with routing and spatial query support
        * I/O with OpenStreetMap data (Please refer to [osm2rn](https://github.com/sjruan/osm2rn))

* Basic Spatial Functions
    * Distance Calculation
        * Haversine distance
    * Spatial Griding
        * Split a given mbr into specified size/interval grid cells
    * Line Segment Simplification
        * Douglas-Peucker algorithm
    
* Trajectory Preprocessing Algorithms
    * Noise Filtering
    
    * Segmentation
    
    * Stay Point Detection (TODO)
    
    * Map Matching
        * Hidden Markov Map Matching

## Papers

If you find our code useful for your research, please cite our papers:

*Sijie Ruan, Ruiyuan Li, Jie Bao, Tianfu He, Yu Zheng. "CloudTP: A Cloud-based Flexible Trajectory Preprocessing Framework". ICDE 2018.*

*Sijie Ruan, Cheng Long, Jie Bao, Chunyang Li, Zisheng Yu, Ruiyuan Li, Yuxuan Liang, Tianfu He, Yu Zheng. "Learning to Generate Maps from Trajectories". AAAI 2020.*

## Requirements

TPTK uses the following dependencies with Python 3.6

* rtree==0.8.3
* networkx==2.3
* GDAL==2.3.2

Other packages can be easily installed using `conda install`, while the following scripts are recommended for `gdal`.

```
conda install -c conda-forge gdal==2.3.2
```
