---
layout: post
title:  "Optimizing time in robotic trajectory planning"
date:   2025-10-06 12:00:00 +0200
permalink: /optimizing-time/
categories: performance planning
---

<p class="preface">
In traditional robotic path planning, we deal with (possibly multiple) robots going from a configuration A to configuration B.
We are mostly concerned with avoiding collisions with the environment, and with each other.
In addition, if we do trajectory planning, we might also be interested in fulfilling some dynamic constraints, or minimizing time or accelerations that appear while we move.
Importantly, we still only deal with going from one configuration to another one.
This does not allow for two robots going to the same place in space (for example for picking something up in the same place).    
</p>

Illustrating the problem above:
Classical path planning enables something like this{% include sidenote.html text='going from a collision free configuration A to a collision free configuration B'%}:

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/time-in-opt/no_intermediate_goal.png" style="width:45%; padding: 10px">
</div>

Compared to what I describe above, when we do multi robot, multi goal planning, we deal with a sequence or a set of goals that we need to reach.
Particularly, we usually do not force the robots to be at a specific location at a given time.
This means that, as part of our planning problem, we also plan when a robot can be somewhere in order to avoid colliding with other robots

Thus, multi-goal path planning enables something like this{% include sidenote.html text='Visiting some intermediate state, and going to a final collision free configuration B'%}:

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/time-in-opt/intermediate_goal.png" style="width:45%; padding: 10px">
</div>

So far, in most previous work I did, I always did multi robot-multi goal _path-planning_{% include sidenote.html text='Sometimes with post processing to minimize accelerations etc, but in general, the planning part was purely geometric.'%}, i.e. neglecting all kinds of dynamics constraints, and only minimizing a proxy to time.

A promising approach to take constraints into account is either doing kinodynamic sampling based planning (which is very likely to be _sloooow_), or doing the thing that is much more common for trajectory planning: some sort of optimization approach.
If we formulate the problem above as optimization problem, we have to deal with the question: 'when do we actually want to reach the intermediate state(s) and the goal?'
To figure out how we can deal with this, I briefly recap some trajectory optimization below.{% include sidenote.html text='[This tutorial](https://www.matthewpeterkelly.com/tutorials/trajectoryOptimization/index.html) is in my opinion by far the best resource to get an intro to the topic, anything I write here is a worse summary.'%}

# Trajectory optimization

Our goal is (very generically) something like this:

$$
\begin{align}
\min_{x, u} & \ c(x(t))\\
\text{s.t.} \ & \ \dot{x}(t) = f(x(t), u(t))\\
& \ x(0) = x_0\\
& \ x(T) \in X_G.
\end{align}
$$

We want to find a trajectory of states $$x(t)$$ and inputs $$u(t)$$, that minimizes a cost function $$c$$ and brings us from a start state to a goal state.

In practice there are some additional constraints, i.e. collision constraints, possibly restricting the magnitude of the input $$u$$, and bounding the state $$x$$.
This can be solved in a variety of ways, but in (hedging my statements: almost) all of them, we have to discretize the problem at some point, since we unfortunately can not optimize an infinite dimensional (continuous) problem.

The most generic way to solve this is to assume a fixed timestep in order to discretize the state and input trajectory, and approximating all the relevant continuous functions.
This means that instead of a function $$x(t)$$, we now have a sequence of states $$x_0 ... x_k ... x_N$$ and the same for the inputs (except that the input sequence only goes up until $$N-1$$). 
Depending on the cost function, and the dynamics that we have, this can then be solved by any generic NLP solver (or if you are lucky with a QP solver).
This is called direct collocation, and results in the optimization problem

$$
\begin{align}
\min_{x, u} & \ \sum_i^{N-1} c(x_i, u_i) + c_\text{goal}(x_N)\\
\text{s.t.} \ & \ x_{i+1} = f_d(x_i, u_i)\ \  \forall\ i=0..N-1\\
& \ x_0 = x_0\\
& \ x_N \in X_G.
\end{align}
$$

Instead of the fixed discretization, we could also approximate our $$x(t)$$ by a piecewise cubic spline (or any other parameterized curve), and take a similar approach as above, just with different optimization variables.
Depending on how we parameterize our curve, this decouples the time and the state somewhat.

# Adding intermediate goals

Going back to the continuous setting, if we want to introduce intermediate state constraints, we can do that via an additional constraint on the state at a time:

$$
\begin{align}
\min_{x, u} & \ c(x(t))\\
\text{s.t.} \ & \ \dot{x}(t) = f(x(t), u(t))\\
& \ x(0) = x_0\\
& \ \color{green}{x(t_\text{inter}) \in X_\text{inter}} \\
& \ x(T) \in X_G
\end{align}
$$

where we for now assumed that we do know _when_ (namely at time $$t_\text{inter}$$) we want to be at the intermediate state.
If we do know, this is a relatively straightforward optimization problem:
We can just as before discretize the state, and add a constraint on the state that corresponds to the time at which we want to fulfill our constraint, and pass the problem to our favourite NLP solver.

If we _do not_ know the time at which we want to reach the constraint, this becomes more annoying, since we need to optimize time in addition to the inputs and states.
Introducing time in addition to the states and inputs in our optimization problem gives us the problem below for the classic collocation

$$
\begin{align}
\min_{x, u, \Delta t} & \ \sum_i^{N-1} c(x_i, u_i) * \Delta t_i + c_\text{goal}(x_N)\\
\text{s.t.} \ & \ x_{i+1} = f_d'(x_i, u_i, \Delta t_i)\ \  \forall\ i=0..N-1\\
& \ x_0 = x_0\\
& \ x_{N/2} \in X_\text{inter}\\
& \ x_N \in X_G\\
& \ 0 < \Delta t_i\ \forall \ i
\end{align}
$$

where we effectively just enforce the constraint (very arbitrarily) at the middle of the trajectory, but enable scaling the trajectory in time by adding the size of the time-discretization $$\Delta t$$ to the optimization problem.
This means that we effectively split the problem in two phases.
This could be simplified a bit further by just dealing with two timestep-sizes (i.e. one per phase), thus reducing the size of the optimization problem a bit{% include sidenote.html text='Instead of this approach, we could also formulate the problem using a complimentarity constraint, but from experience, this is not so nice to optimize anymore, and thus we will skip that here.'%}.

If we now add more intermediate goal states that we want to visit, this scales quite naturally:
We just add more 'phases', one for each intermediate state that we need to visit.

Instead of this above, we could also introduce a phase variable $$s$$ that tells us at which timestep the constraint should be fulfilled, i.e.

$$
\begin{align}
\min_{x, u, \Delta t, s} & \ \sum_i^{N-1} c(x_i, u_i) * \Delta t_i + c_\text{goal}(x_N)\\
\text{s.t.} \ & \ x_{i+1} = f_d'(x_i, u_i, \Delta t_i)\ \  \forall\ i=0..N-1\\
& \ x_0 = x_0\\
& \ x_{\lfloor s * N\rfloor} \in X_\text{inter}\\
& \ x_N \in X_G\\
& \ 0 < \Delta t_i\ \forall \ i
\end{align}
$$

This boils down to a mixed integer program that we could relax in various variants, but this is likely not what we would like to do.
Might come back to this though.

# Introducing more robots

To now change this formulation a bit to deal with multiple robots, we first introduce our robots' states as $$x^r$$, and inputs as $$u^r$$, such that we can have multiple different state and input trajectories. 
For ease of notation, $$x$$ is then simpy the trajectories stacked, same for $$u$$.
The equivalent continuous trajectory optimization problem without intermediate goals then looks very similar as before:

$$
\begin{align}
\min_{x, u} & \ c(x^1(t), ..., x^N(t), u^1(t), ..., u^N(t))\\
\text{s.t.} \ \forall i=0..N \ & \ \dot{x}^i(t) = f(x^i(t), u^i(t))\\
& \ x^i(0) = x^i_0\\
& \ x^i(T) \in X^i_G\\
& \ g_\text{coll}(x(t)) \leq 0 \ \forall t.
\end{align}
$$

where we introduced collision constraints between the robots, since it would be nice if we do not destroy our expensive robots.
We can discretize this nicely in the same way as the single robot problem (which I am skipping here).
The important part is that the collision constraints need to be evaluated at the _same time_.

If we now take the same steps as before, and reintroduce the requirement of visiting an intermediate state for each of the robots, we get

$$
\begin{align}
\min_{x, u} & \ c(x^1(t), ..., x^N(t), u^1(t), ..., u^N(t))\\
\text{s.t.} \ \forall i=0..N \ & \ \dot{x}^i(t) = f(x^i(t), u^i(t))\\
& \ x^i(0) = x^i_0\\
& \ \color{green}{x^i(t^i_\text{inter}) \in X^i_\text{inter}} \\
& \ x^i(T) \in X^i_G\\
& \ g_\text{coll}(x(t)) \leq 0 \ \forall t.
\end{align}
$$

This now is where problems start to happen.
If we want to discretize in the same way as before, i.e., globally discretize all robot trajectories together, and enforce the intermediate constraint(s) at some point(s), we need to enforce a sequence in which we visit the intermediate states *a priori*{% include sidenote.html text='In other words: we need to choose an index at which we enforce each intermediate constraint. This is necessarily also an ordering.'%}, which makes any other sequence impossible{% include sidenote.html text='This might be fine actually, since allowing complete freedom of when to visit an intermediate state makes the problem combinatorial, and thus unlikely to find the global optimum anyways.'%}.

We could instead discretize all robot trajectories separately, and give each robot their own $$\Delta t$$ as well, which would allow for moving the intermediate times around as we wish{% include sidenote.html text='Or as suggested above as well, just a scaling factor per phase.'%}.
This would make collision checking somewhat more difficult, as we need to enforce the collisions at a global time.
However, this would get rid of the requirement of ordering the robot intermediate times, and would enable us to find the optimal solution, if we had an globally optimal solver.
This form of formulating the problem does not structurally enforce an order (but it could if we would want to!).
Thus, the optimization problem that we have is:

$$
\begin{align}
\min_{\{x, u, \Delta t\}_i^R} & \ \sum_r^R\sum_i^{N-1} c(x_i^r, u_i^r) * \Delta t_i^r + c_\text{goal}(x^r_N)\\
\text{s.t.} \ \forall r=1..R \ & \ x^r_{i+1} = f_d'(x^r_i, u^r_i, \Delta t^r_i)\ \  \forall\ i=0..N-1\\
& \ x^r_0 = x^r_0\\
& \ x^r_{N/2} \in X^r_\text{inter}\\
& \ x^r_N \in X^r_G\\
& \ 0 < \Delta t^r_i\ \forall \ i \\
& \ g_\text{coll}(x^r(t_\text{coll})) \leq 0 \ \forall t_\text{coll}
\end{align}
$$

where we abused the notation a bit to denote the interpolation between states $$x^r(t_\text{coll})$$.
Notably, we have a grid of times where we check the collisions that is not the same at which we evaluate the rest.
This means that when solving this, we need to take some special care, since we need to interpolate between two states in order to obtain the state at the time at which we check the collision.

Similarly as before, we can use this to extend this to any number of 'phases'.

# Literature

I am collecting a few related things to the problem of introducing time in our optimization problem.
Of course, I am not the first persion thinking about introducing time in the optimization problems, altough most previous work had different reasons for doing it.
Thus, the problem of having to deal with collision constraints at times different than the optimization variables/discretization timesteps seems novel to me.

- [Space-Time Functional Gradient Optimization for Motion Planning](https://homes.cs.washington.edu/~bboots/files/T-CHOMP-icra-2014.pdf)
- [A 6-DOF robot-time optimal trajectory planning based on an improved genetic algorithm](https://jrobio.springeropen.com/articles/10.1186/s40638-018-0085-7)
- [Time-Optimal Trajectory Planning for Industrial Robots Based on Improved Fire Hawk Optimizer](https://www.mdpi.com/2075-1702/13/9/764)

A common theme is bilevel optimization where we first do path planning, and then time parameterize the plan

- [Quadcopter Trajectory Time Minimization and Robust Collision Avoidance via Optimal Time Allocation](https://arxiv.org/pdf/2309.08544)
- [Collision-free time-optimal path parameterization for multi-robot teams](https://arxiv.org/pdf/2409.17079)

For completeness, there is also sampling based stuff that deals with time as part of the planning problem:

- [T-PRM: Temporal Probabilistic Roadmap for Path Planning in Dynamic Environments](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9981739)
- [ST-RRT*: Asymptotically-Optimal Bidirectional Motion Planning through Space-Time](/strrt)
- [Prioritized Motion Planning for Multiple Robots](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=1545306)

Aside from these works, I also briefly looked at introducing [time in MPC as design parameter](/variable-dt-mpc) which feels similar, but is not really, as we do not optimize over the time.

# Future work

I would like to implement something like this in the near future.
Hit me up if 
- this sounds fun, or 
- if you have a solution to the problem of messy gradients for the collision constraint at the global times,
- or if I missed listing your paper that is relevant.