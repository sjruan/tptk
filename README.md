# TPTK - Trajectory Preprocessing Toolkit

TPTK is a trajectory preprocessing toolkit in Python.

Note that, this is only my personal implementation. For the industrial level quality and efficiency, you're welcome to try our product [JUST](http://just.urban-computing.cn/ "京东城市时空数据引擎"). 

Currently, TPTK serves as a submodule of [DeepMG](https://github.com/sjruan/DeepMG "DeepMG").

## Features

* Basic Spatial Functions
    * Distance Calculation
    * Spatial Griding
    * Spatial Index
    * Line Segment Simplification

* Map Matching Support
    * Hidden Markov Map Matching

## Paper

If you find our code useful for your research, please cite our paper:

*Sijie Ruan, Ruiyuan Li, Jie Bao, Tianfu He, Yu Zheng. "CloudTP: A Cloud-based Flexible Trajectory Preprocessing Framework". ICDE 2018.*

## Requirements

TPTK uses the following dependencies with Python 3.6

* rtree==0.8.3
* networkx==2.3
* GDAL==2.3.2
