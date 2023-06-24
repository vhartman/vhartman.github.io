---
layout: post
title:  "On variable timestepping in model predicitve control"
#subtitle: "or: .."
date:   2023-06-22 12:00:00 +0200
permalink: /variable-dt-mpc/
categories: mpc science
---

The model predicitve control you learn about during your studies is always presented with uniform timestepping.
Ever since I learned about MPC, I was wondering if the whole thing would not be much more efficient by using a variable timestep.
This can be motivated quite simply: We only need to be _really_ accurate for the timestep we are applying in the next control update.
In general, the rest is only there to get some intuition on what happens after, and - at least intuitively - does not have to be as accurate.

# What are we going to do?
We will be looking at model predicitve contouring control for a racecar (as done here []).
But instead of doing the whole 'every timestep is exactly the same' we'll introduce a prediction horizon that will increase over time.

That is, instead of the typical MPC formulation

$$
\begin{align}
u^* = & \min_u \sum_i^N j(x_i, u_i)\\
\text{s.t.} \ \ & x_0 = x(0)\\
&x_{t+i} = x_i + \Delta t f(x_i, u_i) \\
& x_i\in \mathcal{X},  u_i \in \mathcal{U}\\
& x_i\leq g(x_i, u_i)
\end{align}
$$

I want to have a look at

$$
\begin{align}
u^* = & \min_u \sum_i^N j(x_i, u_i)\\
\text{s.t.} \ \ & x_0 = x(0)\\
&x_{t+i} = x_i + \Delta t_if(x_i, u_i) \\
& x_i\in \mathcal{X},  u_i \in \mathcal{U}\\
& x_i\leq g(x_i, u_i)
\end{align}
$$

which is virtually the same, except that there is the index $$i$$ on the timestep $$dt$$.

Of course, this variable timestepping approach could be implemented in any optimal control setting, such as vanilla MPC, MPPI (model predictive path integral control), or even normal trajectory optimization.

#### Related work
I always assumed that something similar to what I had in mind here must already have been done _somewhere_, but maybe its just not the thing that the academic community is interested in?

In most of the open source MPC libraries I looked at (do mpc, matlab, adrl control toolbox), variable timestepping was also not an option. 
Acados was the only library that I found that has the option to use variable timesteps.

Recently, when reading something completely different, I found two papers that follow a similar approach: 
- [STORM: An Integrated Framework for Fast Joint-Space Model-Predictive Control for Reactive Manipulation](https://proceedings.mlr.press/v164/bhardwaj22a/bhardwaj22a.pdf) which uses the approach for MPPI.
- [An integrated system for real-time Model Predictive Control of
humanoid robots](https://homes.cs.washington.edu/~todorov/papers/ErezHumanoids13.pdf) which mentions this approach at thevery end of section III.

I am interested in how you should choose your timesteps, and what improvement you can expect _at a constant compute time_.
There is little discussion of that in any of those papers above, only the mention that "there is a design tradeoff", and "that small steps in the beginning, and large steps later" are better.

There were two more papers that I could find that go in a similar direction, albeit going a step further: they are automatically adjusting the timestep-size to get a dense representation of the system at points where it matters, and a finer one where it does not.

# Model predicitve contouring control (MPCC)
Model predictive controuring control{% include sidenote.html text='More on it here.'%} is an approach that is based on MPC to track a given path, while maximizing the progress along that same path.

$$
\min_u \int e(\phi(\theta), x) dt
$$

That is, the goal is to move along a path as quickly as possible, while staying inside the constraints given.

# The setup
Instead of going for the racecar, we'll first have a look at steering a masspoint along a line, while respecting the boundaries, and joint limits (i.e. accelerations, velocities).

That being said, our system is simply a second order integrator for now - we'll later come back to the racecar dynamics.

$$
\alpha
$$

The racetrack is the following:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike-neurons/circle_path.png" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
</div>

and is represented as a spline.

The constraints are velocity constraints, acceleration constraints, and the track constraints.

# The implementation

Now, actually implementing the controller requires discretizing the equations above and linearizing them at each timestep.
But instead of the normal approach of using uniform timesteps, we'll test a set of non-uniform time stepping schemes.

The optimization problem we'll implement is:

$$
\min_u \sum ...
$$

# Experiments
I have implemented this whole thing in ...{% include sidenote.html text='Code is available [].'%}

[Animation]

#### Results
- lap times
- run times

# Outlook

- Incorporating stepsize control from numerical integration in MPC like approaches
