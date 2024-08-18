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
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_5.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_10.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_20.png" style="width:29%; padding: 10px">
  <figcaption><span style="color: #1f77b4;">Blue</span> is position, <span style="color: #ff7f0e;">orange</span> is velocity, and <span style="color: #2ca02c;">green</span> is acceleration. The constraints for each variable are shown in the corresponding color.</figcaption>
</div>
<br>

It should be clearly visible that the shorter horizons violate the constraint.
Intuitively, what happens here is that the short horizon leads to a priorization of accelerating quickly, and only 'getting to know' about the constraint too late to slow down, thereby violating the constraint{% include sidenote.html text='To a certain extent, this could be alleviated with the "correct" final cost and final constraint, however, the final cost is hard to get "correct", and constraining the final set to a velocity from which we can safely stop makes the system too conservative.'%}.

For the second point, we now keep the prediction horizon the same for all runs, but we vary the size of the timestep that we use for the discretization, and plot the open loop cost below.
Next to it, we plot the time it took the solver to find a solution for the MPC problem.

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_cost.png" style="width:46%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_comp_time.png" style="width:46%; padding: 10px">
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

- The inverted pendulum on a cart pole (_the_ classical control benchmark).
  The dynamics equations of the cart pole problem can be found [here](https://metr4202.uqcloud.net/tpl/t8-Week13-pendulum.pdf), and the state is four dimensional, and the input is scalar.
  The goal here is to swing the pendulum up, and stabilize it at the top (the unstable equilibrium).
  There are input and state constraints.
  A possible solution to the problem looks like this:
  <div style="width: 90%;margin:auto; text-align: center;">
    <img src="{{ site.url }}/assets/nu_mpc/cartpole_anim.gif" style="width:75%; padding: 10px">
  </div>

- Recovering a 2D quadcopter from an inverted position. The dynamics of this are again relatively standard, and can be found e.g. [here](https://cookierobotics.com/052/).
  A solution looks like this:
  <div style="width: 90%;margin:auto; text-align: center;">
    <img src="{{ site.url }}/assets/nu_mpc/quadcopter_animation.gif" style="width:75%; padding: 10px">
  </div>

#### What are we actually testing?

We are interested in figuring out if we can save time in our MPC controllers while keeping the performance approximately the same via variable timestepping.
Thus, what we test is an MPC controller with various numbers of timesteps with a nonuniform discretization, and plot the computation time and the quality of the solution.

What we would expect (hope to get) is something like a pareto optimality front, where the nonuniform discretization hopefully has the lowest cost at a given ompute time, respectively has the lowest compute time at a given cost.
This would allow us to fairly seamlessly trade off computation time and solution quality.
In order to isolate the compute time (which we want to analyze) from other effects, we'll fix the prediction horizon length. 
In this first experiment, we'll test two different discretization strategies, namely a linearly incresing one, and a exponentially increasing one. That is, our timestep for the the linearly increasing approach is

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

We compare these nonuniform disretizations to a constant discretization with the same number of timesteps.
Note that this leads to larger timesteps in the beginning directly.

In the following, we'll run each experiment multiple times in order to ensure that we get sensible compute times, and not just one off results.

Before running this experiment on the systems introduced above, we run the MPC controllers on the masspoint example that we used as motivation:
<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/masspoint_cost_comp.png" style="width:46%; padding: 10px">
</div>

And as we hoped, we get a curve that results in better cost solutions at lower computation times.
This is however a relatively simple system, and the cost difference is quite small.

Continuing with the cartpole system and the quadcopter looks like so:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/cartpole_cost_comp.png" style="width:46%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/quadcopter_cost_comp.png" style="width:46%; padding: 10px">
</div>

We clearly see what we hoped to see, and apparently get savings of up to 80% percent in computation time, while staying relatively close to the 'optimal' solution that we get with a fine constant time discretization.

Similar to the motivational experiment before, the cost differences that can be obtained are not _huge_ in these experiments.
This can partially be ascribed to the fact that the systems are still relatively simple.
However, in the cartpole experiment, we can also see a nice demonstration of the non-uniform discretization: Controllers with a lower compute time (~50% of the uniformly discretized) MPC controller still find a solution, and achieve a good cost.
Compared to that, all solutions with a cost >1000 do not find a solution, and do not manage to control the cart pole system to the instable equilibrium at the top.

It does appear like there is a slight difference in choice of non-uniform discretization, namely the linear slightly outperforming the exponential approach.
However, the difference is small and might very well be noise.

#### A brief look at a more complex system
After these quantitative tests, I want to have a look at steering a racecar around a racetrack using model predictive contouring control (MPCC).

The dynamics of the racecar are taken from here, and are approximated by the bycicle model.
The state is 8 dimensional, and the input has two dimensions.
As MPCC introduces additional states and inputs, the resulting system is 10 dimensional, with three input states.

The racetrack also has boundaries that we will introduce by enforcing a maximum distance between the middle line and the center of the car.
The constraints are then velocity constraints, acceleration constraints, and the track constraints.
A possible solution looks like this:
<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/racecar_sol.gif" style="width:75%; padding: 10px">
</div>
Here, the rectangle is the car, and the blue line is the predicted path at that time-instant.

The setting we consider now for designing a controller is one where we assume that we have a fixed compute budget allocated for a controller.
We then want to find the controller that stays in this compute budget, and minimizes some cost functional. 
In our case, the cost is the minimization of the laptimes while staying in the track limits.
Our two parameters to choose are then the discretization timestep and the prediction horizon.


Below, we plot{% include sidenote.html text="For the sake of plotting, we'll assume that the car will follow the track in any case reasonably well, but to be sure, we'll double check track violations."%} the lap times for a grid search over discretization timesteps and number of timesteps in the prediction horizon for the uniform controller, and the two non-uniform discretization strategies.

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/quadcopter_cost_comp.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/quadcopter_cost_comp.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/quadcopter_cost_comp.png" style="width:29%; padding: 10px">
</div>

# Conclusion & Outlook
Looking at the results it is quite clear that one should not discretize the continuous control problem uniformly if one cares about performance.
I think the specific way to discretize is up for discussion, but the experiments show quite convincingly that a compareable solution quality can be obtained with much less computational cost when using a non-uniform disretization.

Further, the experiments suggest that there is a bigger advantage to use such a non-uniform discretization if the systems is operating at the boundary of the constraints, and needs to e.g. not exceed a positional constraint.
Here, a larger lookahead is required, which can either be enabled by a larger discretization timestep (and sacrifice performance by doing so) or via nonuniform discretization (which seems to sacrifice less performance).

I think this can be partially explained by the fact that a longer discretization step can be seen as a lowpass filter on the control signal, thereby disallowing high frequency actions{% include sidenote.html text='This is an idea that I need to devote some more time to. Intuitively it feels right to say that a given discretization allows actions only below some frequency. There should be some connection between system performance and possible control frequency.'%}.
If we have a system that requres high frequency actions sometimes, this non-uniform discretization is helpful.

Of course this also means that since we only allow high frequency actions at the start of the prediction window, there must be some approach that outperforms ours if we need a high frequency action later in the prediction window.

#### Next steps
There are many things one could do here. First should probably be an implementation in C++ to see how the results and speedups hold up in a real implementation compared to the python versions I have here.
I have no reason to expect drastic differences, but you never know.

Then, there are a variety of other things one should have a look at and analyze further. Amongst other things

- Influence of the integrator that is used for discretization on the strategy. I found that with a simple euler integrator, large timesteps did not work well anymore (this means that sometimes the uniform controller works a bit better than in the plots above, and sometimes drastically worse. Roughly the same for the nonuniform discretization).
- Conditioning the stepsize on something, possibly a reference trajectory, or the solution of the previous timestep
  - I do feel like it should be possible to figure out some approach to figure out where fine timesteps are required, and where we do not need a fine discretizaztion online in an RTI scheme.
  - Similarly, incorporating stepsize control from numerical integration in MPC like approaches might lead to a good stepsize-choice-policy.
- There is an open question how one could handle e.g. contacts that need to happen at a specific time, as for example in locomotion.
