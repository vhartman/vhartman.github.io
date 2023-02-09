---
layout: post
title:  "Sampling based kinodynamic motion planning"
date:   2023-02-09 12:00:00 +0200
permalink: /sampling-kinodynamic/
categories: science research
---

This post is for me to organize some of my thoughts on kinodynamic motion planning, and might serve as an entry to 'parallels of motion planning to RL'.

# Problem
Kinodynamic motion planning has the goal to find a trajectory that steers a (possibly nonlinear) system to a specified goal, ideally not colliding with the environment.
Along the way, we might want to minimize some objective - common examples are minimizing time, or minimizing energy.

The problem can be written as:

$$
\begin{aligned}
\tau = &{\arg\min}_{x, u} J(x, u) \\
\text{with} \ \ & x_0 \ \text{given}\\
\text{s.t.} \ \ & x_{t+1} = f(x, u)\\
& x_t \in C_\text{free}\\
& u_t \in \mathcal{U}\\
& x_t \in \mathcal{X}
\end{aligned}
$$

where $$\tau$$ is the trajectory, consisting of the states of the system $$x$$ and the input $$u$$.

There are various approaches to solve this problem: The ones that I know of, and am most familiar are RL, optimization, sampling based planning, and search.

Which method work best generally depends on the assumptions we make (i.e. what do we assume to know?), and what we really want as a result, as the output of the methods above is not exactly the same{% include sidenote.html text='RL gives us a _policy_ (possibly a goal conditioned policy) for the whole space, Planning and Search give us trajectories, Optimization approaches can give us both policies (if we run it as a controller (e.g. MPC)), but also simply trajectories.'%}. In this set of notes, I am focussing on sampling based methods.

# Sampling based approaches
A simple approach to tackle the kinodynamic problem above, taking _lots_ of inspiration from geometric RRTs is the one described in this [paper](https://skat.ihmc.us/rid=1K7WQT337-XQJP8C-1YHM/Randomized%20Kinodynamic%20Planning.pdf):

In essence, a tree is grown by randomly sampling a state $$x_\text{rand}$$ in the state space, and then extending the tree towards it.
This 'extend' step consists of finding the 'closest' vertex $$x_\text{near}$$ that is part of the tree, and applying a random input $$u$$ for some timestep $$\Delta t$$ that hopefully gives us a state $$x_\text{new}$$ that is closer to the originally sampled state than the vertex we started with. 

A typical approach for this is sampling multiple control inputs $$u$$, and times $$\Delta t$$, apply all of them, and take the one that gives the minimum distance to the state we sampled.

A crucial detail here is that we do only assume access to a function $$f$$ which tells us how the system evolves for a given start state, input, and timestep, and not much else{% include sidenote.html text='This is very similar to the assumptions that RL makes.'%}.

Some work that followed this initial paper:
- It was proven that the approach above is [incomplete when using a fixed timestep](http://www.tobiaskunz.net/pubs/KunzWAFR14-RrtIncomplete.pdf).
- It was then (only ~20 years after the first paper!) given a [completeness proof](https://ieeexplore.ieee.org/ielaam/7083369/8581687/8584061-aam.pdf).

Most other methods are modifications and extensions of this simple approach.

The works in [here](http://arl.cs.utah.edu/pubs/ICRA2013-1.pdf) and [here](https://lis.csail.mit.edu/pubs/perez-icra12.pdf) linearize the systems around the operating point to provide a better 'extend'-functionality, and provide better optimality properties.
Particularly, the distance function was improved, i.e., some principled way of computing the distance between two points in a space with differential constraints was proposed.

[This work](https://upcommons.upc.edu/bitstream/handle/2117/125331/2080-Randomized-Kinodynamic-Planning-for-Constrained-Systems.pdf) shows how to build a version of the algorithm above that works well for constrained systems, e.g. a parallel manipulator.
In this case, it is not straightforward how to find valid control inputs.

The works [here](http://biorobotics.ri.cmu.edu/papers/sbp_papers/integrated1/latombe_kinematic_obst.pdf) deals with moving obstacles, the one [here](https://www.ije.ir/article_136801_cd076228a90014fa04cda30c9ee8dd49.pdf) with a dynamic environment, and the specific case of planning for a quadrotor.

The work in [here](https://ieeexplore.ieee.org/abstract/document/7274361) works on the specific case of planning for a car, and is thus able to work with b-splines, instead of the 'black-box' function $$f$$ for state-propagation.
With this simplification, we can also extend the single tree-approach from the beginning to a bidirectional tree search.
In the other methods, we were not able to this, since we only assume to have access to the _forward_ propagation{% include sidenote.html text='There are systems where the reverse function can be computed from the forward propagation, but e.g. a system that involves pushing objects around, getting this function is close to impossible.'%}.

#### Short side note: Control
Going a bit more to the control side, we can also build tree structures for planning with kinodynamic systems.
[LQR-trees](https://groups.csail.mit.edu/robotics-center/public_papers/Tedrake09a.pdf) give us a policy to steer an agent towards a goal by constructing a series of funnels that are linked together, and eventually steer the system towards the goal (and stabilize it there if so desired).
This work is not only giving us a _path_, but a control policy.

The previous work is extended to graphs instead of trees [here](https://groups.csail.mit.edu/robotics-center/public_papers/Majumdar11.pdf).
This allows for reuse of previous controllers and computations.

#### Multiquery
The [work](https://kavrakilab.org/publications/shome2021-bundle-of-edges.pdf) presents a possible approach to extend this forward-propagation-of-states to graphs instead of only trees.

This would allow a multiquery planning approach.
However, as done, since the edges need to be re-created for every start-state, and it was not evaluated on true multi-query problems, it is unclear how much of a benefit this brings.
Further, there was no bidirectional search.

#### Allowing discontinuities
All the approaches above assume that we do not have a dicontinuity in the path itself.
This limits us to applying an input to a specific start state (i.e. growing directly from the tree), or we would need to use an optimizer to solve a Two-Value-Boundary-Problem, which is generally computationally expensive.

[db-A*](https://arxiv.org/abs/2203.11108) allows for discontinuities in the solution, and runs an optimizer over the resulting trajectory to fix it.
The implicit assumption is that if the discontinuity that we allow is small enough, we can fix this ('steer a bit to the left', 'go a little faster') to actually go to the starting position of the next state, respectively to move the next state to the point that we reach.

#### Other
This [here](https://stanfordasl.github.io/wp-content/papercite-data/pdf/Allen.Pavone.AIAAGNC16.pdf) seems to be the first kinodynamic sampling based planner that runs in realtime.
