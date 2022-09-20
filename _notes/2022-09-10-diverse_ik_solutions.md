---
layout: post
title:  "Computing diverse IK solutions"
date:   2022-09-10 12:00:00 +0200
permalink: /diverse-ik/
categories: science research
---

# Computing an IK solution
Computing an inverse kinematics solution to a problem can be done in closed form for some robots, but typically, optimization approaches are used, as the goal that should be reached is often underspecified (e.g. in the pen plotting case, we do not care about the orientation of the pen around its axis, and we are given quite a bit of freedom of the angle of the axis with respect to the paper we want to make a dot on).

However, the resulting problem is very nonlinear due to collision avoidance requirements.

# Finding diverse solutions
It can be the case that we want to find multiple diverse soltions to a problem. 
The motivation for me is from [this paper](https://vhartmann.com/multi-robot/) or [this blog post on stippling with multiple robots](https://vhartmann.com/robo-stippling-p2/).
In both cases, I want multiple valid solutions to find sets of solutions for multiple robots that do not conflict with other robots, i.e. do not collide with other robots.
As described in the blog post, this can - in the case of two robots - be showsn as a bipartite graph.

#### How?
The dumb approach is simply randomizing the initial pose from which the optimization algorithm starts.
There is some more intricate research going on here though:
- Learning based with normalizing flows: [IKFlow](https://sites.google.com/view/ikflow)
- [Learning Reachable Manifold and Inverse Mapping for a Redundant Robot manipulator.](https://ieeexplore.ieee.org/document/9561589)

On the topic of quickly generating _valid_ sequences for manipulation planning problems, I was involved in some research:
- [Learning Efficient Constraint Graph Sampling for Robotic Sequential Manipulation](https://arxiv.org/pdf/2011.04828.pdf) 

In other fields:
- Constraint programming: [General overview](https://en.wikipedia.org/wiki/Constraint_programming)
  - ["Finding Diverse Solutions of High Quality to Constraint Optimization Problems"](https://www.ijcai.org/Proceedings/15/Papers/043.pdf)
  - ["Finding Diverse and Similar Solutions in Constraint Programming"](https://www.aaai.org/Papers/AAAI/2005/AAAI05-059.pdf)
