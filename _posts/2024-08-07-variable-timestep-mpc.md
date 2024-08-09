---
layout: post
title:  "On variable timestepping in model predictive control"
#subtitle: "or: .."
date:   2024-08-07 12:00:00 +0200
permalink: /variable-dt-mpc/
categories: mpc science
---

Model predictive control is a control method that uses a model to predict what will happen in the future.
With this prediction, one can find the best control input for some user-defined objective function.
When implementing this, there is always a trade-off between how much control authority we have, the accuracy of the prediction, and how far into the future we predict the system.
Common wisdom is that we would like to have a prediction that goes into the future as far as possible, but we would also like to have a very good prediction accuracy.
This is computationally not feasible.

The model predicitve control you learn about during your studies is always presented with uniform timestepping.
Ever since I learned about MPC, I was wondering if the whole thing would not be much more efficient by using a variable timestep.
This can be motivated quite simply: We only need to be _really_ accurate for the timestep we are applying in the next control update.
In general, the rest is only there to get some intuition on what happens after, and - at least intuitively - does not have to be as accurate.

Code for everything can be found here.

# Motivating example

First, we want to show that a long time horizon can be crucial to find feasible solutions to some control problems.
Second, we want to show here that smaller timesteps are required for a high performing solution.

As motivating example, we will have a look at a very simple system, consisting of a one dimensional masspoint, which we model as double integrator, with [position, velocity] as state, and [acceleration] as control signal.

We'll also assume that our goal is simply steering the masspoint to [0, 0], starting from some non-zero position.
Crucially for our experiment, we'll also assume that we have constraints on the position, velocity, and acceleration.

We first show that a reasonably long horizon is important to being able to find a _feasible_ solution to this problem.
We do this by varying the prediction horizon in the controller, and plotting the solution below.
To ensure that we obtain some solution even when constraints are violated, we formulate the constraints as soft constraints with high weights.

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
</div>

It should be clearly visible that the shorter horizons violate the constraint.
Intuitively, what happens here is that the short horizon leads to a priorization of accelerating quickly, and only 'getting to know' about the constraint too late to slow down, thereby violating the constraint{% include sidenote.html text='To a certain extent, this could be alleviated with the "correct" final cost and final constraint, however, the final cost is hard to get "correct", and constraining the final set to a velocity from which we can safely stop makes the system too conservative.'%}.

For the second point, we now keep the prediction horizon the same for all runs, but we vary the size of the timestep that we use for the discretization, and plot the open loop cost below.
Next to it, we plot the time it took the solver to find a solution for the MPC problem.

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
</div>

While in this case, we always find _a_ solution, the solution quality when using a finer discretization is clearly superior{% include sidenote.html text='While there is a clear difference, it is not as large as it is in other (more nonlinear) systems like a quadcopter.'%}, but we also have the problem of a much larger compute time that is required.

Then, as claimed in the intro, in an ideal world, we would like to have a combination of small timesteps, and long prediction horizon in order to obtain the best solution we can get.

# What are we going to do?
Instead of doing the normal MPC discretization strategy of 'every timestep is exactly the same' we'll increase the timesteps over the prediction horizon.

The standard MPC formulation looks roughly like this:

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
u^* = & \min_{x, u} j_N(x_N) + \sum_i^{N-1} \Delta t_i j(x_i, u_i)\\
\text{s.t.} \ \ & x_0 = x(0)\\
&x_{t+i} = x_i + \Delta t_i f(x_i, u_i) \\
& x_i\in \mathcal{X},  u_i \in \mathcal{U}\\
& x_i\leq g(x_i, u_i)
\end{align}
$$

which is virtually the same, except that there is the index $$i$$ on the timestep $$\Delta t$$, and the stage-cost is scaled by the magnitude of the timestep.

Of course, this variable timestepping approach could be implemented in any optimal control setting with a receding horizon such as vanilla MPC, dynamic programming approaches, or MPPI (model predictive path integral control){% include sidenote.html text='It is more questionable if this works well for MPPI, since we do not do traditional optimization here which scales with the number of desicion variables. It could work well, as it still reduces the size of the decision space.'%}{% include sidenote.html text='It might even be advantageous in some settings of a trajectory optimization setting to not use completely uniform discretizations.'%}.

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


# Experiments

#### The problems
To test the variable timestepping approach, I will have a detailed look at two problems here{% include sidenote.html text='There are more systems (quadcopter, masspoint in N dimensions, double pendulum) in the code, and it is relatively straightforward to run them to produce the same plots as below.'%}:

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

#### What are we actually testing?

We are interested in figuring out if we can save time in our MPC controllers while keeping the performance approximately the same via variable timestepping.
Thus, what we test is an MPC controller with various numbers of timesteps with a nonuniform discretization, and plot the computation time and the quality of the solution.
What we would expect (hope to get) would something like this:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
</div>

This would allow us to fairly seamlessly trade off computation time and solution quality.
In this first experiment, we'll use a linearly increasing stepsize.
In order to isolate the compute time (which we want to analyze) from other effects, we'll fix the horizon length. That is, our timestep is

$$
\Delta t_i = \Delta t_0 + \alpha i
$$

with $$\alpha$$ defined by the constraint $$T = \sum_i^N \Delta t_0 + \alpha i$$.
This equation can be solved for $$\alpha$$.
Similarly, we can define our timestep to be

$$
\Delta t_i = \Delta t_0 (1+\alpha)^i
$$

with a similar constraint as before, which can again be (this time iteratievely) solved for alpha.

We compare these nonuniform disretizations to a constant discretizatoin with the same number of timesteps.
Note that this leads to larger timesteps in the beginning directly.

Running this experiment for both the cartpole system and the racecar looks like so:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
</div>

We clearly see what we hoped to see, and apparently get savings of up to XX percent in computation time, while staying relatively close to the 'optimal' solution that we get with a fine constant time discretization.

Similarly, we could keep the compute time somewhat constant (by fixing the number of discretization steps), and increase the time horizon.
In this case, we get the plots below:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
  <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
</div>


# Conclusion & Outlook

Looking at the results it is quite clear that one should not discretize the continuous control problem uniformly if one cares about performance.
I think the specific way to discretize is up for discussion, but the experiments show quite convincingly that a compareable solution quality can be obtained with much less computational cost when using a non-uniform disretization.

#### Next steps
There are many things one could do here. First should probably be an implementation in C++ to see how the results and speedups hold up in a real implementation compared to the python versions I have here.
I have no reason to expect drastic differences, but you never know.

Then, there are a variety of other things one should have a look at and analyze further. Amongst other things

- Conditioning the stepsize on something, possibly a reference trajectory, the solution of the previous timestep
- Incorporating stepsize control from numerical integration in MPC like approaches
- There is an open question how one could handle e.g. contacts that need to happen at a specific time, as for example in locomotion.
