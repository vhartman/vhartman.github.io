---
layout: cv
title: ST-RRT\*&#58; Asymptotically-Optimal Bidirectional Motion Planning through Space-Time
permalink: /strrt/
custom_css: cv
custom_title: ST-RRT\*&#58; Asymptotically-Optimal Bidirectional Motion Planning through Space-Time
---

*Francesco Grothe, Valentin N. Hartmann, Andreas Orthey, Marc Toussaint*
<p style="font-size:8pt">Machine Learning & Robotics Lab, University of Stuttgart, Germany<br>
Learning and Intelligent Systems Group, TU Berlin, Germany</p>

**Brief:**
We extend and modify RRT-Connect to a combination of space and time.
This allows us to plan paths for agents in environments that have moving obstacles with known trajectories.
ST-RRT\* is complete and asymptotically optimal.

We used an early version of ST-RRT\* in the [multi-agent-tamp solver](/multi-robot/).


**Abstract:**
<div style="display:block; margin: 0 2em 0 2em">
We present a motion planner for planning through space-time with dynamic obstacles, velocity constraints, and unknown arrival time. Our algorithm, Space-Time RRT* (STRRT*), is a probabilistically complete, bidirectional motion planning algorithm, which is asymptotically optimal with respect to the shortest arrival time. We experimentally evaluate ST-RRT* in both abstract (2D disk, 8D disk in cluttered spaces, and on a narrow passage problem), and simulated robotic path planning problems (sequential planning of 8DoF mobile robots, and 7DoF robotic arms). The proposed planner outperforms RRT-Connect and RRT* on both initial solution time, and attained final solution cost. The code for ST-RRT* is available in the Open Motion Planning Library (OMPL).
</div>

<hr style="margin: 2em 0 2em;">

### Paper 

Latest version: [arXiv](https://arxiv.org/abs/2203.02176)

<a href="https://arxiv.org/abs/2203.02176" target="_blank"><img src="/assets/strrt/strrt-thumb.png" style="display:block; margin:0 auto; border: 1px solid #555;"></a>

<hr style="margin: 2em 0 2em;">

### Code

Code is available on [Github](https://github.com/ompl/ompl/blob/main/src/ompl/geometric/planners/rrt/STRRTstar.h).

<hr style="margin: 2em 0 2em;">

###  Demo

The red disk needs to find a path through the moving obstacles (blue) to the goal (black).
<div style="text-align:center"><img style="width:40%" src="/assets/strrt/a1.gif"> <img style="width:40%" src="/assets/strrt/a3.gif"></div>


<br>

We sequentially plan the movement of a mobile robot from a random start to a random goal state.
<div style="text-align:center"><img style="width:90%" src="/assets/strrt/mobile.gif"></div>


<hr style="margin: 2em 0 2em;">

### Bibtex

```
@inproceedings{22-grothe-ICRA,
  title     = {ST-RRT*: Asymptotically-Optimal Bidirectional Motion Planning through Space-Time},
  author    = {Grothe, Francesco and Hartmann, Valentin N. and Orthey, Andreas and Toussaint, Marc},
  booktitle = {Proc{.} of the IEEE Int{.} Conf{.} on Robotics and
  		       Automation (ICRA)},
  year      = {2022},
  arxiv_pdf = {2203.02176}
}
```

<hr style="margin: 2em 0 2em;">

### Funding
The research has been supported by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany’s Excellence Strategy – EXC 2120/1 – 390831618 "IntCDC"
