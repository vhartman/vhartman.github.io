---
layout: post
title:  "On variable timestepping in model predicitve control"
#subtitle: "or: .."
date:   2024-08-07 12:00:00 +0200
permalink: /variable-dt-mpc/
categories: mpc science
---

The model predicitve control you learn about during your studies is always presented with uniform timestepping.
Ever since I learned about MPC, I was wondering if the whole thing would not be much more efficient by using a variable timestep.
This can be motivated quite simply: We only need to be _really_ accurate for the timestep we are applying in the next control update.
In general, the rest is only there to get some intuition on what happens after, and - at least intuitively - does not have to be as accurate.

# What are we going to do?
We will be looking at model predicitve contouring control for a racecar (as done here []).
But instead of doing the whole 'every timestep is exactly the same' we'll increase the timesteps over the prediction horizon.

That is, instead of the typical MPC formulation

$$
\begin{align}
u^* = & \min_{x, u} j_N(x_N) + \sum_i^{N-1} j(x_i, u_i)\\
\text{s.t.} \ \ & x_0 = x(0)\\
&x_{t+i} = x_i + \Delta t f(x_i, u_i) \\
& x_i\in \mathcal{X},  u_i \in \mathcal{U}\\
& x_i\leq g(x_i, u_i)
\end{align}
$$

Here, $$j$$ is a possibly non-convex cost term, $$f$$ are the dynamics of the system we are interested in, $$\mathcal{X}, \mathcal{U}$$ are the domains of the state and the input respectively, and $$g$$ is a constraint function.
Compared to this more or less standard formulation, I want to have a look at

$$
\begin{align}
u^* = & \min_{x, u} j_N(x_N) + \sum_i^{N-1} j(x_i, u_i)\\
\text{s.t.} \ \ & x_0 = x(0)\\
&x_{t+i} = x_i + \Delta t_if(x_i, u_i) \\
& x_i\in \mathcal{X},  u_i \in \mathcal{U}\\
& x_i\leq g(x_i, u_i)
\end{align}
$$

which is virtually the same, except that there is the index $$i$$ on the timestep $$\Delta t$$.

Of course, this variable timestepping approach could be implemented in any optimal control setting with a receding horizon such as vanilla MPC, dynamic programming approaches, or MPPI (model predictive path integral control).{% include sidenote.html text='It might even be advantageous in some settings of a trajectory optimization setting to not use completely uniform discretizations.'%}

In this post, I will have a look at an iLQR implementation, and a MPC implementation with variable timesteps.

#### Related work
I always assumed that something similar to what I had in mind here must already have been done _somewhere_, but maybe its just not the thing that the academic community is interested in?

In most of the open source MPC libraries I looked at (do mpc, matlab, adrl control toolbox), variable timestepping was also not an option. 
Acados was the only library that I found that has the option to use variable timesteps.

Recently, when reading something completely different, I found papers that follow a similar approach: 
- [STORM: An Integrated Framework for Fast Joint-Space Model-Predictive Control for Reactive Manipulation](https://proceedings.mlr.press/v164/bhardwaj22a/bhardwaj22a.pdf) which uses the approach for MPPI.
- [An integrated system for real-time Model Predictive Control of
humanoid robots](https://homes.cs.washington.edu/~todorov/papers/ErezHumanoids13.pdf) which mentions this approach at thevery end of section III.
- [Distributing Collaborative Multi-Robot Planning with Gaussian Belief Propagation](https://arxiv.org/pdf/2203.11618.pdf) - there is a brief mention of 'increasing time-gaps between consecutive states', but this is never elaborated after, and not really visible in the video demonstration.

I am interested in how you should choose your timesteps, and what improvement you can expect _at a constant compute time_.
There is little discussion of that in any of those papers above, only the mention that "there is a design tradeoff", and that "small steps in the beginning, and large steps later" are better.

And while I completely belive that this strategy is the correct one, I would like to see some more experiments on it, get an intuition how much compute time can be saved, and check if this is really the best strategy.

There were two more papers that I could find that go in a similar direction, albeit going a step further: they are automatically adjusting the timestep-size to get a dense representation of the system at points where it matters, and a finer one where it does not:

- [A Variable-Sampling Time Model Predictive Control Algorithm for Improving Path-Tracking Performance of a Vehicle](https://www.mdpi.com/1424-8220/21/20/6845)
- [Variable Sampling MPC via Differentiable Time-Warping Function](https://arxiv.org/abs/2301.08397)

The objective in those papers seems to be an increased accuracy, not a decreased computational cost though.

# The problems

To test the variable timestepping approach, I will have a look at two problems here:

- The inverted pendulum on a cart pole (_the_ classical control benchmark).<br><br>
  The dynamic of the cart pole problem can be found here, and the state is four dimensional, and the input is scalar.
  The goal here is to swing the pendulum up, and stabilize it at the top (the unstable equilibrium).
  There are input and state constraints.
  A possible solution to the problem looks like this:
  <div style="width: 90%;margin:auto; text-align: center;">
    <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
  </div>
- Steering a racecar around a racetrack using model predictive contouring control (MPCC).<br><br>
  The dynamics of the racecar are taken from here, and are approximated by the bycicle model.
  The state is XX dimensional, and the input has two dimensions.
  As MPCC introduces additional states and inputs, the resulting system is XX dimensional, with three input states.<br><br>
  The racetrack also has boundaries that we will introduce by enforcing a maximum distance between the middle line and the center of the car.
  The constraints are then velocity constraints, acceleration constraints, and the track constraints.
  A possible solution looks like this:
  <div style="width: 90%;margin:auto; text-align: center;">
    <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
  </div>

# Experiments
I have implemented this whole thing in ...{% include sidenote.html text='Code is available [].'%}

[Animation]

#### Results
- lap times
- run times

# Outlook

- Incorporating stepsize control from numerical integration in MPC like approaches
