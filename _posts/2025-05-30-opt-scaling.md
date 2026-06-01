---
layout: post
title:  "You should manually scale your optimal control problem"
date:   2025-10-28 12:00:00 +0200
permalink: /scaling-your-opt-problem/
categories: numerics path-planning science
---

<p class="preface" markdown="1">
In any kind of optimization problem, the scaling of the optimization variables should not change the optimal solution. However, depending on the solver, it changes how fast we get there (or if we get there at all depening on your solver settings).<br>

The magnitude of the influence (a solve-speedup of factor ~1000!) this has was very surprising to me at some point in an internship, and it was extremely surprising to everyone I ever told about it as well.
</p>

In robotics, you'll often run into various types of optimization problems.
It could be in [optimal control](https://en.wikipedia.org/wiki/Optimal_control), in [trajectory planning](https://en.wikipedia.org/wiki/Motion_planning), or even just when solvong the linearized QP for whole body [quadruped locomotion](https://ethz.ch/content/dam/ethz/special-interest/mavt/robotics-n-intelligent-systems/rsl-dam/documents/RobotDynamics2017/robot-dynamics-exercise-3-solution.pdf) (or for a humanoid if that's what you like).
In all these problems, you typically start by formulating your cost function, set up your constraints, and then pass it on to the solver of your choice, which then magically{% include sidenote.html text='This "magically" is doing a lot of heavy lifting here.'%} gives you a solution.

Your solver typically does gradient descent in some shape or form {% include sidenote.html text='Technically, you could also do search/another global approach, but we focus on optimization here for now.'%}.
Generally, the 'same' optimization problem can be written in a couple of ways (i.e. the problem has the same optimum), and the solvers like some formulations better and some worse.

In an internship a while ago I worked on (nonlinear) optimal control, and implemented a framework for formulating and solving the problem.
While I knew at the time that solvers are somewhat prone to working much better with some formulations than others, I did not know how big of a difference in solve time just **scaling** your problem can have{% include sidenote.html text='I decided that I am absolving myself by excusing this lack of knowledge partially by solvers having a preprocessing step, and thus assuming that such scaling would happen in the solver itself if it would be benefitial.'%}.
That being said, this seems to be somewhat niche knowledge, since many people were surprised by the magnitude of the speedup that I got in that specific problem.

I never really dove much deeper at the time (mostly for the lack of time), regarding why that is, if all solvers are affected, and on which type of problem(s) such speedups can be observed.
But the topic has occupied a bit of my brain since then, and I wanted to finally investigate a bit more why and how this happens, and this would have the nice by-product that I coudl point people to this artifact when I tell them about this effect (and get it out of my brain).

The code for this post is available [here](here).

# Related literature

When I first saw how big of an influence this scaling can have, I expected that this is a known thing, and was just a blindspot for me.
I expected not to be the first person running into this, and other people having lots of pratical advice on how to best scale your problem.

And I was and am not the first person running into this!

The place where I found an example that scaling matters, and that it can save a lot of time is [from casadi](https://web.casadi.org/blog/nlp-scaling/).
They show the difference in convergence speed/number of required iterations for an example of controlling a 1D rocket, i.e., a nonlinear optimal control problem, and get a speedup of ~15-20 by scaling the optimization problem.
Unfortunately some of the links in there are dead{% include sidenote.html text='Particularly, they link to some lectures from from John Betts which I can not find. But it seems like similar content is discussed in the [book here](http://www.digitalsats.com/reprints/Betts-2011-PracticalMethodsFor%20OptimalControlAnd%20EstimationUsingNonlinearProgramming_epdf.pub.pdf).'%}. 

<div class="callout" markdown="1">

#### Example: Control of a 1D rocket
The problem that we have is getting a rocket to a certain height at a certain time with minimum fuel.
This leads to some equality constraints (fulfilling the rocket equation, and initial and goal conditions), and some cost (minimizing fuel){% include sidenote.html text='Have a look at the code for the exact equations.'%}.

The original example above uses matlab. I don't want to use matlab, so I translated the code to python here.
The plots that result are _exactly_ the same that are also in the casadi blog though.

The optimal solution is below, and we can see that in this example, there is a massive difference in the magnitudes of the different states.

<div class="post-image">
    <img src="{{ site.url }}/assets/opt-scaling/rocket_ipopt_states.png" style="width:90%; padding: 5px">
</div>

We run the problem in its unscaled and its scaled (The scaling is done by changing the units that we use to represent the states) version, and look at the convergence (how primal and dual feasibility changes with the number of iterations).
In addition, we also run a version that has the solver internal scaling enabled/disabled.

<div class="post-image">
    <img src="{{ site.url }}/assets/opt-scaling/rocket_ipopt_convergence.png" style="width:70%; padding: 5px">
</div>

We can then also run some experiments to figure out what the main driver is - when we change the mass of the rocket{% include sidenote.html text='And correspondingly adjust the maximum thrust in the model to keep a constant thrust to weight ratio.'%}, this effect diminishes a lot.
It does however not go away completely, as in this example, there are multiple states with big differences in magnitude.

<div class="post-image">
    <img src="{{ site.url }}/assets/opt-scaling/rocket_ipopt_mass_sweep.png" style="width:70%; padding: 5px">
</div>

As already stated in the original casadi post, even though casadi already does some auto-scaling (specifically, ipopt does gradient based scaling by default), it is in this case clearly worth it to scale the problem manually!
</div>

Coming back to other related work: It is definitely known that scaling can have an impact on convergence and solve speed, it is not so widely (at least amongst the people that I know and worked with) known just _how_ much influence it can have.
There are some papers on the topic as well, and thy do dicuss that it is best practice, and should be done. But again, they do not really show when you should do it and how you should do it, and the effec size is underdiscussed as well:

- Scaling in [Nocedal and Wright](https://convexoptimization.com/TOOLS/nocedal.pdf)
- [Some discussion on scaling in traj opt](https://arxiv.org/pdf/2106.09125) and some more from the [same author](https://arxiv.org/pdf/1906.04857)
- ["Scaling and Balancing for High-Performance Computation of Optimal Controls"](https://arxiv.org/abs/1810.11073) is a paper on how to scale stuff.
- ["Exploiting Scaling Constants to Facilitate the Convergence of Indirect Trajectory Optimization Methods"](https://arxiv.org/abs/2208.11273): paper
- [Effects on scaling in ipopt](https://arxiv.org/pdf/1301.7283)

There is also not that much advice on _how_ you should transform your problem to get the best performance out of your solver.
The general advice is usually 'make everything the same magnitude', but that is very generic, and often not very actionable unfortunately.
Additionally, some solvers are invariant to the magnitude of the optimization variables, many are not, and so in the end what you should do is somewhat dependent on the solver that you are actually using (but as seen in the example above, we already know that even if the solver is doing some scaling itself, it can still help to do the scaling ourselves as well).

- The [book from John Betts](http://www.digitalsats.com/reprints/Betts-2011-PracticalMethodsFor%20OptimalControlAnd%20EstimationUsingNonlinearProgramming_epdf.pub.pdf) gives some very good advice. Most of the things I summarize below comes from this book.
- The help page from [Altair Motion Solve](https://help.altair.com/hwsolvers/ms/topics/solvers/ms/optimization_advanced_topics_scaling_optimization_problem_r.htm) has some insights in why we scale, and how to scale. They also have an automatic scaling procedure.
- Next to the book above, [Optimagic](https://optimagic.readthedocs.io/en/latest/how_to/how_to_scaling.html) seems to be the closest to the thing I wanted at the time: advice on how to do scaling. Howeverm again there is no discussion on how much faster things can be.
- [Andrew Fitzgibbon](https://www.fitzgibbon.ie/optimization-parameter-scaling) gives some advice on scaling. It tracks with what John Betts says.
- There is [an article on scaling](https://www.alglib.net/optimization/scaling.php) and [practical tips](https://www.alglib.net/optimization/tipsandtricks.php)

# Scaling a quadratic program
I am predominantly interested in MPC and trajectory optimization (which end up as relatively big QPs).
In the following, we'll also have a look at simpler (smaller) QPs{% include sidenote.html text='Generally, when solving the more complex problems, they will also at some point end up in the form of a QP and be solved by a QP solver.'%} to see if there is a difference as well, respectively how big the difference is.

We are not going to go into too much depth here on how to formalize trajectory optimization problems (see [here](https://www.matthewpeterkelly.com/tutorials/trajectoryOptimization/index.html) for that), or how to do Model predictive control (see [e.g. here](https://idsc.ethz.ch/education/lectures/model-predictive-control.html) for that).
What I am interested in is how scaling affects these problems, repsectively the solve times and convergence.

Our QPs for optimal control problems will in all cases have:
- inequality constraints (which in optimal control usually take the form of box constraints coming from, e.g., joint limits, or velocity bounds)
- equality constraints (from the system dynamics and the initial and goal states)
- a quadratic cost function (since we often want to minimize the energy, and a quadratic cost arises naturally)
- possibly also linear terms in the cost (e.g., arising in reference tracking as we will see later on).

With these ingredients, we get a QP of the form

$$ 
\begin{align}
\min_x & \ x^T R x\\
\text{s.t.} & \ l \leq x \leq u\\
& \ Gx - f = 0.
\end{align}
$$

In such a QP we can apply a transformation of variables without changing the result, as long as we are able to revert the transform to recover the original optimization variables (if we can not revert the transformation, we could not recover the original variables).
In order to maintain the convexity properties of the QP above, we are going to deal with an affine transformation $$x = A\hat{x} + b$$ to our original optimization variables.
The new QP will then be

$$ 
\begin{align}
\min_x & \ (A\hat{x} + b)^T R (A\hat{x} + b)\\
\text{s.t.} & \ l \leq (A\hat{x} + b) \leq u\\
& \ G(A\hat{x} + b) - f = 0,
\end{align}
$$

or with a bit of rewriting

$$ 
\begin{align}
\min_\hat{x} & \ \hat{x}^TA^TRA\hat{x} + 2\hat{x}^TA^TRb\\
\text{s.t.} & \ l \leq A\hat{x} + b \leq u\\
& \ GA\hat{x} + Gb - f = 0,
\end{align}
$$

which is another QP (where we dropped some constant terms from the objective already). 

In addition, we can scale the constraints and the cost separately, i.e., just left-multiply the constraint matrices, and the cost function with another diagonal matrix (in this case $$W$$ for the cost function, $$P$$ for the inequality constraints, and $$F$$ for the equality constraints).

$$ 
\begin{align}
\min_\hat{x} & \ W (\hat{x}^TA^TRA\hat{x} + 2\hat{x}^TA^TRb)\\
\text{s.t.} & \ Pl \leq P(A\hat{x} + b) \leq Pu\\
& \ FGA\hat{x} + FGb - Ff = 0,
\end{align}
$$

After solving the new problem, we need to transform our variables back to obtain the variables that we cared  about initially (which we can do using the equation above).
Generally, our life will be easier if we assume that we can invert $$A$$ (we will usually assume that we use an $$A$$ that is diagonal), and even a bit simpler if we assume that $$b$$ is zero.
{% include sidenote.html text='To simplify things a bit, I am going to assume $$b$$ is zero from now on.'%}

One of the main things to notice in the last QP is that we scale our objective with $$\sqrt{W}A^TRA\sqrt{W}$$, we scale the equality constraints as $$FGA$$, and we transform our bounds to be within $$Pl$$ and $$Pu$$.

Generally, we consider the $$F$$ matrix to be a _row_ scaling of the constraint matrix, and the $$A$$ matrix to do _column_ scaling of the matrix.
This can be seen clearly in the special case of both matrices being diagonal (which is what we usually assume).

The general advice is usually to scale the variables such that they are all in the same order of magnitude, and make a unit step in the variables correspond to a unit step in cost.
Using the scaling that we introduced above, we can try to scale our variables and bounds such that this is the case.

Betts further gives the advice that we can also scale our cost function with a constant, and we can scale the constraints with a constant as well (again, from the book [here](http://www.digitalsats.com/reprints/Betts-2011-PracticalMethodsFor%20OptimalControlAnd%20EstimationUsingNonlinearProgramming_epdf.pub.pdf), which has a much more mathematically rigorous treatment of the whole topic).

#### Receipe
Thus, to scale a QP that we would like to solve, a simple receipe can be the following:

1. Choose $$P = A^{-1}$$, $$F = I$$.
2. Choose $$A = \text{diag}(l)$$ or $$A = \text{diag}(r)$$, respectively choose the scaling such that on the diagonal of $$A$$, you have the expected values for your solution.
3. Optionally, scale the cost function using a constant (such that the condition number of the KKT matrix is close to one).
4. Recompute the cost and constraint matrices using the scaling{% include sidenote.html text='If we are looking at an MPC or trajectory optimization problem, we normalize per timestep.'%}.
5. Solve the QP.
6. Compute the original solution via $$x = A\hat{x}$$.

This is a decent approach if we assume that we have these constraints, and we expect that the constraints are active at the optimal solution.
If we do not have the constraints $$l$$ or $$r$$, or they are not the same, it can be very helpful to use the linear term $$b$$ as well to ensure that we get constraints as we would like to have them.
If we do not expect that the constraints are actually active, they still usually give some indication on the magnitude of the various variables.
In this case, we choose the terms on the diagonal of $$A$$ such that the terms are (after scaling) roughly equal to 1 as mentioned above before.

# Problems and experiments

Generally, as said above, I am interested in optimal control and trajectory planning problems, and thus, the problems that I want to look at here are not general optimization problems, but should even in the simplest case have some of the properties of the optimal control problems{% include sidenote.html text='Importantly, this also means that the conclusions from this blog post should not be taken verbatim for a generic optimization problem. The advice might or might not apply, but I am not going to do these experiments here.'%} mentioned before.

Originally, I have noticed the scaling-effects using OSQP as a solver of an MPCC (model predictive contouring control) problem, but we are going to look at a few different options for sovers in addition to looking at a bunch of different problems.
Namely, we are going to have a look what influence the scaling has for osqp, clarabel, and ipopt.
I will use casadi for formulating the problem for ipopt.

To see the details of the problems that we are looking at, toggle the blocks below.

<details markdown="1">
<summary>Quadratic program</summary>

We'll start with a simple QP which is still interpretable for us to see whats going on.
For this simple case, we can also visualize iterates and whats going on in general much better than in the higher dimensional cases later on.

$$
\begin{align}
  \min_x\ & \ (x-q)^T R (x - q)\\
  \text{s.t.} \ & \ Bx \leq 0.
\end{align}
$$

In this case, we will leave out the equality constraint.

The problem we are setting up can then be seen as a problem where we are trying to find a value that is closest to a reference value, i.ee, in a robotics constext, this could be a setting where we try to find a joint pose which brings our end-effector close to some specified pose under some constraints.

Concretely, we consider the state $$x = [x_1, x_2]^T$$ with the first index corresponding to a position, and the second to a velocity.
The limits are in our case symmetrical, namely $$[1, 0.01]$$, and the weight we assign is much higher for the position, i.e. $$R=\text{diag}([100, 1])$$.
The reference pose is $$[1, 1]$$.

This gives us the QP matrices/vectors ...

[plot for ..]

</details>

<details markdown="1">
<summary>Constrained control</summary>

The next problem is a QP that corresponds to trying to minimize a single step error under constraints, i.e., we try to steer a state to a reference state, but we do not yet do general MPC over a finite horizon, but only optimize the input for the next timestep.

We will minimize a cost such as acceleration, or energy consumption which can both be written as quadratic problem.
Additionally, we are trying to move our robot to a given setpoint, thus we also get a linear term:

$$
||x[t+1] - x_\text{ref}||_R + ||u||_Q.
$$

We assume that we have linear robot dynamics, e.g., a triple integrator, where we have jerk as the input, and acceleration, velocity, and position as states: 

$$x[t+1] = Ax[t] + Bu[t],$$

where $$x$$ is the state at discrete time $$t$$ and $$u$$ is the input at the same time.
Finally, we have box constraints on the states and inputs that correspond to e.g. torque or acceleration limits (for the input) and joint limits for the states.

We will assume that our acceleration and torque limits are much higher than the velocity and joint limits.

$$
\begin{align}
  \min_{x, u}\ & \ ||x[t+1] - x_\text{ref}||_R + ||u||_Q\\
  \text{s.t.} \ & \ x[1] = Ax[0] + Bu \\
  & \ x[0] = x_0\\
  & \ G_\text{state}x \leq x_\text{lim}\\
  & \ G_\text{inp}u \leq u_\text{lim}\\
\end{align}
$$

</details>

<details markdown="1">
<summary>Robot arm reference tracking</summary>

We are going to extend the problem above to a path tracking problem in order to scale the problem up to a more realistic scenario.
Particularly, we need to define a time horizon (in number of steps), over which we will optimize.
This means that we will need to extend the cost function to deal with the whole horizon

$$
\sum_t^H||x[t] - x_\text{ref}[t]||_R + ||u[t]||_Q.
$$

The rest stays roughly the same, except that we are now going to have to deal with multiple states/inputs instead of only a single step, and a time dependent reference state.
We are again sticking to the same system dynamics and constraints, i.e., a triple integrator with relatively high jerk limts compared to the acceleration and velocities. 

[anim ]

</details>

<details markdown="1">
<summary>Robot arm trajectory planning with energy minimization</summary>

In addition to the problem above, we now want to minimize the energy that the manipulator uses.
While it is possible to write that purely in terms of the inputs/states, we are going to introduce energy as a state, since we want to ensure that we obey some energy usage limits{% include sidenote.html text='For a static manipulator, this formulation does not make a lot of sense, since we usually can not deplete the energy resource that we are plugging the robot into. However, you could imagine a mobile manipulator with a battery here.'%}.
This also makes it possible to write the energy minimization problem as linear cost term of start minus end state.

We then change our cost function to a mixture of the reference tracking, and a term for the energy-usage minimization.

[ also anim ]

</details>

<details markdown="1">
<summary>MPCC with a racecar</summary>

[In a previous post](/variable-dt-mpc), we looked at motion planning/control for a racecar using MPCC.
I wanted to apply the scaling to this as well.

Before we look at the nonlinear dynamics of the racecar, we do it with a masspoint though.
This is still a nonlinear problem due to the cost.

[also anim]

</details>

<details markdown="1">
<summary>Landing a rocket</summary>

Contrary to the original example above i the related work, we now also want to land a rocket.

</details>

# Results
After introducing all the problems, we first show the number of iterations that each solver takes to converge to the specified tolerance, across the different scaling strategies.

**OSQP**

| Problem | unscaled | scaled | col-scaled |
|---|---|---|---|
| Quadratic program | ? | ? | ? |
| Constrained control | ? | ? | ? |
| Robot arm reference tracking | ? | ? | ? |
| Robot arm trajectory planning (energy min.) | ? | ? | ? |
| MPCC with a racecar | ? | ? | ? |
| Landing a rocket | ? | ? | ? |
{: .results-table}

**Clarabel**

| Problem | unscaled | scaled | col-scaled |
|---|---|---|---|
| Quadratic program | ? | ? | ? |
| Constrained control | ? | ? | ? |
| Robot arm reference tracking | ? | ? | ? |
| Robot arm trajectory planning (energy min.) | ? | ? | ? |
| MPCC with a racecar | ? | ? | ? |
| Landing a rocket | ? | ? | ? |
{: .results-table}

**IPOPT**

| Problem | unscaled | scaled | col-scaled |
|---|---|---|---|
| Quadratic program | ? | ? | ? |
| Constrained control | ? | ? | ? |
| Robot arm reference tracking | ? | ? | ? |
| Robot arm trajectory planning (energy min.) | ? | ? | ? |
| MPCC with a racecar | ? | ? | ? |
| Landing a rocket | ? | ? | ? |
{: .results-table}

# Discussion
...

# Conclusion
Use all the knowledge you have to scale your problems.


# TODO

- [ ] look at differen cost functions?
