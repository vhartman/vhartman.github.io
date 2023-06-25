---
layout: post
title:  "Planning in unseen environments"
date:   2023-06-20 12:00:00 +0200
permalink: /unseen-envs/
categories: science review planning
---

This is a sort of a review of the current state of the art in planning in partially known environments.
It could also be seen as the related work section of a paper in the same topic.
I recently stumbled upon some papers in this area, and this is my way of trying to get a grasp on the topic and its difficulties and aproaches to solve them.

# Robotic Path Planning
There are a variety of approaches to do path planning in robotics. 
They are typically classified into search based methods, sampling based methods, and optimization based methods.
Those different approaches have different guarantees, and deal very differently with the various difficulties of the problems.

What they usually have in common is that they assume that the environment and the obstacles are fully known.
In the real world, something like this can be achieved if we have complete control over our environment, that is, e.g., in a robotic cell in a factory, or when assembling a car.

If we want to explore some more unstructured environments (e.g., when exploring a house, or a cave), that assumption does not really hold anymore, and we need to adapt our planners accordingly.

# Planning in unseen environments
The main difference to 'traditional' planning is that we do not know the environment, but need to slowly figure out where obstacles are while moving around.
This acquisition of the obstacle locations can be via line-of-sight sensors, or it could even be something like 'bumping into objects'.

This online acquisition of the environment might lead to previous plans becoming infeasible, and needing to replan due to obstacles where we did not assume any before.
This is something that does not happen if we assume a fully known environment.
Therefore, it is extremely desirable to do quick replanning, and in addition to that the planner should have 'good' closed-loop behaviour, i.e. the path that the planner returns should be stable, and not change too much to avoid some sort of 'oscillatory behaviour'.

There is also difference in objective: we are not necessarily looking for the shortest path, but we want to minimize overall (maybe expected?) travel time.

#### General approaches and insights
- It is very common to simply assume that the part of the map that we have not yet explored is completely obstacle free. That is, we are 'optimistic in the face of uncertainty'.
- Another approach is to essentially treat the environment as 'dynamic', and do incremental replanning.
- In more recent works, some researchers try to predict the map from the observations and do planning simultaneously.

#### Papers
- [Continuous motion planning in unknown environment for a 3D cartesian robot arm](https://ieeexplore.ieee.org/document/1087621)
- [Planning and acting in partially observable stochastic domains](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf)
- [D\* lite](http://idm-lab.org/bib/abstracts/papers/aaai02b.pdf)
- [Far planner: Fast, attemptable route planner using dynamic visibility update](https://frc.ri.cmu.edu/~zhangji/publications/IROS_2022.pdf)
- [Guided Sampling-Based Motion Planning with Dynamics in Unknown Environments](https://arxiv.org/pdf/2306.09229.pdf)
- [Map-Predictive Motion Planning in Unknown Environments](https://arxiv.org/pdf/1910.08184.pdf)
- [Safe Motion Planning in Unknown Environments: Optimality Benchmarks and Tractable Policies](https://arxiv.org/pdf/1804.05804.pdf)
- [Fuzzy Motion Planning of Mobile Robots in Unknown Environments](https://link.springer.com/content/pdf/10.1023/A:1024145608826.pdf)

#### Ideas
- This sounds like the ideal multiquery planning problem where parts of the environments change.
I recently worked on [*Efficient Path Planning In Manipulation Planning Problems by Actively Reusing Validation Effort*](/manipulation-path-planning/), which sounds like the perfect fit for this problem.

