---
layout: post
title:  "You should manually scale your optimal control problem"
date:   2026-06-23 12:00:00 +0200
permalink: /scaling-your-opt-problem/
categories: numerics path-planning science
---

<p class="preface" markdown="1">
In any kind of optimization problem, the scaling of the optimization variables should not change the optimal solution. However, depending on the solver, it changes how fast we get there (or if we get there at all depending on your solver settings).<br>

The magnitude of the influence (a solve-speedup of factor ~1000!) this has was very surprising to me at some point in an internship, and it was extremely surprising to everyone I ever told about it as well.
</p>

In robotics, you'll often run into various types of optimization problems.
It could be in [optimal control](https://en.wikipedia.org/wiki/Optimal_control), in [trajectory planning](https://en.wikipedia.org/wiki/Motion_planning), or even just when solving the linearized QP for whole body [quadruped locomotion](https://ethz.ch/content/dam/ethz/special-interest/mavt/robotics-n-intelligent-systems/rsl-dam/documents/RobotDynamics2017/robot-dynamics-exercise-3-solution.pdf) (or for a humanoid if that's what you like).
In all these problems, you typically start by formulating your cost function, set up your constraints, and then pass it on to the solver of your choice, which then magically{% include sidenote.html text='This "magically" is doing a lot of heavy lifting here.'%} gives you a solution.

Your solver typically does gradient descent in some shape or form {% include sidenote.html text='Technically, you could also do search/another global approach, but we focus on optimization here for now.'%}.
Generally, the 'same' optimization problem can be written in a couple of ways (i.e. the problem has the same optimum), and the solvers like some formulations better and some worse.

In an internship a while ago I worked on (nonlinear) optimal control, and implemented a framework for formulating and solving the problem.
While I knew at the time that solvers are somewhat prone to working much better with some formulations than others, I did not know how big of a difference in solve time just **scaling** your problem can have{% include sidenote.html text='I decided that I am absolving myself by excusing this lack of knowledge partially by solvers having a preprocessing step, and thus assuming that such scaling would happen in the solver itself if it would be benefitial.'%}.
That being said, this seems to be somewhat niche knowledge, since many people were surprised by the magnitude of the speedup that I got in that specific problem.

I never really dove much deeper at the time (mostly for the lack of time), regarding why that is, if all solvers are affected, and on which type of problem(s) such speedups can be observed.
But the topic has occupied a bit of my brain since then, and I wanted to finally investigate a bit more why and how this happens, and this would have the nice by-product that I could point people to this artifact when I tell them about this effect (and get it out of my brain).

The code for this post is available [here](here){% include sidenote.html text='The initial problems and test were done completely by me a long time ago, and now with claude, I was able to speed up much of the experimentation. Thus, large parts of the code are written by claude, as I decided at some point that I could use this post to experiment a bit with how to best work with AI. Everything in this text is written by me with some proof reading by claude.'%}.

# Related literature

When I first saw how big of an influence this scaling can have, I expected that this is a known thing, and was just a blindspot for me.
I expected not to be the first person running into this, and other people having lots of pratical advice on how to best scale your problem.

And I was and am not the first person running into this!{% include sidenote.html text='
This whole scaling topic is called preconditioning in the optimization literature generally. I have however not looked a lot at that side of the literature, as I came more from the side of optimal control, and am limiting myself to this type of problems here.'%}. 

The place where I found an example that scaling matters, and that it can save a lot of time is [from casadi](https://web.casadi.org/blog/nlp-scaling/).
They show the difference in convergence speed/number of required iterations for an example of controlling a 1D rocket, i.e., a nonlinear optimal control problem, and get a speedup of ~15-20 by scaling the optimization problem.
Unfortunately some of the links in there are dead{% include sidenote.html text='Particularly, they link to some lectures from from John Betts which I can not find. But it seems like similar content is discussed in the [book here](http://www.digitalsats.com/reprints/Betts-2011-PracticalMethodsFor%20OptimalControlAnd%20EstimationUsingNonlinearProgramming_epdf.pub.pdf).'%}. 
The casadi blog post is more of an example where scaling matters, but does not really go into detail why this happens.

<div class="callout" markdown="1">

#### Example: Control of a 1D rocket
The problem that we have is getting a rocket to a certain height at a certain time with minimum fuel consumption.
This leads to some equality constraints (fulfilling the rocket equation, and initial and goal conditions), and some cost (minimizing fuel){% include sidenote.html text='Have a look at the code for the exact equations.'%}.
This problem is nonconvex.

The original example above uses matlab. I don't want to use matlab, so claude translated the code to python for me.
The plots that result from this are _exactly_ the same that are also in the casadi blog.

The optimal solution is below, and we can see that in this example, there is a massive difference in the magnitudes of the different states.
More concretely, we see that both the mass and the thrust start quite high, and become a lot lower later on, while the velocity is always relatively low. 
The states are on the order between 1e3 and 1e8.

<div class="post-image">
    <img src="{{ site.url }}/assets/opt-scaling/rocket_ipopt_states.png" style="width:90%; padding: 5px">
</div>

We run the problem in its unscaled and its scaled (The scaling is done by changing the units that we use to represent the states) version, and look at the convergence (how primal and dual feasibility changes with the number of iterations).
In addition, we also run a version that has the solver internal scaling enabled/disabled.

<div class="post-image">
    <img src="{{ site.url }}/assets/opt-scaling/rocket_ipopt_convergence.png" style="width:90%; padding: 5px">
</div>

We can very clearly see that the manually scaled formulation performs best in numbers of iterations, and it does not realy make a difference if we use or if we do not use the internal scaling.

We can then also run some experiments to figure out what the main driver is - when we change the mass of the rocket{% include sidenote.html text='And correspondingly adjust the maximum thrust in the model to keep a constant thrust to weight ratio.'%}, this effect diminishes a lot.
It does however not go away completely, as in this example, there are multiple states with big differences in magnitude.

<div class="post-image">
    <img src="{{ site.url }}/assets/opt-scaling/rocket_ipopt_mass_sweep.png" style="width:90%; padding: 5px">
</div>
This leads us to the main hypothesis that the large difference in state magnitude is to blame for the bad convergence behavior.

As already stated in the original casadi post, even though casadi already does some auto-scaling (specifically, ipopt does gradient based scaling by default), it is in this case clearly worth it to scale the problem manually!
</div>

Coming back to other related work: It is definitely known that scaling can have an impact on convergence and solve speed, it is not so widely (at least amongst the people that I know and worked with) known just _how_ much influence it can have.
There are some papers on the topic as well, and they do dicuss that it is best practice, and should be done. But again, they do not really show when you should do it and how you should do it, and the effect size is underdiscussed as well.

There is a bunch of practical advice on help pages of optimization software:

- The help page from [Altair Motion Solve](https://help.altair.com/hwsolvers/ms/topics/solvers/ms/optimization_advanced_topics_scaling_optimization_problem_r.htm) has some insights in why we scale, and how to scale. They also have an automatic scaling procedure.
- Next to the book above, [Optimagic](https://optimagic.readthedocs.io/en/latest/how_to/how_to_scaling.html) seems to be the closest to the thing I wanted at the time: advice on how to do scaling. However, again there is no discussion on how much faster things can be.
- [Andrew Fitzgibbon](https://www.fitzgibbon.ie/optimization-parameter-scaling) gives some advice on scaling. It tracks with what John Betts says.
- There is [an article on scaling](https://www.alglib.net/optimization/scaling.php) and [practical tips](https://www.alglib.net/optimization/tipsandtricks.php)

And then there is some mentions of scaling in the classic works:
- The [book from John Betts](http://www.digitalsats.com/reprints/Betts-2011-PracticalMethodsFor%20OptimalControlAnd%20EstimationUsingNonlinearProgramming_epdf.pub.pdf) gives some very good advice. Most of the things I summarize below comes from this book.
- Scaling problems is a chapter [Nocedal and Wright](https://convexoptimization.com/TOOLS/nocedal.pdf) (page 27)

And finally, some papers do mention scaling, or even completely focus on scaling and how to do it:
- [Some discussion and suggestions for how to scale in trajectory optimization](https://arxiv.org/pdf/2106.09125) and some more from the [same author](https://arxiv.org/pdf/1906.04857). Unfortunately, in neither of the papers, there is a comparison between the scaled and the unscaled opt. problems.
- ["Scaling and Balancing for High-Performance Computation of Optimal Controls"](https://arxiv.org/abs/1810.11073) is a paper on how to scale stuff.
- ["Exploiting Scaling Constants to Facilitate the Convergence of Indirect Trajectory Optimization Methods"](https://arxiv.org/abs/2208.11273): paper
- [Effects on scaling in ipopt](https://arxiv.org/pdf/1301.7283)

I might have looked at these papers a bit too superficially, but in my opinion there is not a lot of simple understandable advice (besides from Betts), and the effect sizes seem underdiscussed to me, and the analysis of when it actually matters is missing to me personally.

The general advice is usually 'make everything the same magnitude', but that is very generic, and often not very actionable unfortunately.
Additionally, some solvers are invariant to the magnitude of the optimization variables, many are not, and so in the end what you should do is somewhat dependent on the solver that you are actually using (but as seen in the example above, we already know that even if the solver is doing some scaling itself, it can still help to do the scaling ourselves as well).

# Scaling a quadratic program
I am predominantly interested in MPC and trajectory optimization (which end up as relatively big QPs).
In the following, we'll also have a look at simpler (smaller) QPs{% include sidenote.html text='Generally, when solving the more complex problems, they will also at some point end up in the form of a QP and be solved by a QP solver.'%} to see if there is a difference as well, respectively how big the difference is.

We are not going to go into too much depth here on how to formalize trajectory optimization problems (see [here](https://www.matthewpeterkelly.com/tutorials/trajectoryOptimization/index.html) for that), or how to do model predictive control (see [e.g. here](https://idsc.ethz.ch/education/lectures/model-predictive-control.html) for that).
What I am interested in is how scaling affects these problems, respectively the solve times and convergence.

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

Finally, before moving on, I want to mention that most of the things we now introduced also works for nonlinear problems. 
We have to be somewhat careful with warm starting if we do SQP, but a basic diagonal scaling/change of variables effectively always works also in NLPs.

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

We will call this bound-based scaling from now on (even though it is not always the most descriptive name, as it sometimes might be 'expected-solution-size'-scaling).

#### Illustration of the effect of scaling

On a simple problem in 2d, we can visualize what happens if we scale the problem along the axes (i.e., using a diagonal scaling matrix).
Concretely, we are going to look at a problem that has one dimension weighted higher in the quadratic cost than the other, and we will scale according to the cost matrix in this case.

We will also have a look at a second case (bottom row), where the state vectors are all rotated by 40 degrees (i.e. we do a change of basis), and correspondingly, the cost ellipsoids are rotated by 40 degrees.
Otherwise, the top and bottom row below are the same problem.

We then run normal gradient descent (i.e. a first order solver) on this and show the trace that the solution takes over the iterations.
First, we see this on the unscaled problem, then on the version with diagonal scaling, and finally the version where we use general affine whitening (by using a non-diagonal scaling).

Finally, (in the last column) we also run a second order solver (i.e. a newton step) too see how the problem is solved by such a solver.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/scaling_2d_illustration_notitle.png" style="width:100%; padding:5px">
</figure>

It is quite visible that diagonal scaling helps a lot if we have a problem that can be whitened by diagonal scaling.
We can also see that we should possibly consider more complex scaling mechanisms than scaling with a diagonal matrix, as the diagonal scaling does not help anything at all in the case where the basis is rotated by 40 degrees.
On the other hand, general affine scaling recovers the one-step solution.

Finally, the second order solver solves the problem in a single step, i.e. imbalance in the states does not affect the solver much.

# Problems and experiments

Generally, as said above, I am interested in optimal control and trajectory planning problems, and thus, the problems that I want to look at here are not general optimization problems, but should even in the simplest case have some of the properties of the optimal control problems{% include sidenote.html text='Importantly, this also means that the conclusions from this blog post should not be taken verbatim for a generic optimization problem. The advice might or might not apply, but I am not going to do these experiments here.'%} mentioned before.

Originally, I have noticed the scaling-effects using OSQP as a solver of an MPCC (model predictive contouring control) problem, but we are going to look at a few different options for sovers in addition to looking at a bunch of different problems.
Namely, we are going to have a look what influence the scaling has for osqp, clarabel, and ipopt.
I will use casadi for formulating the problem for ipopt.

OSQP is a splitting (first order) solver, whereas Clarabel, and ipopt are factorizing solvers.
We will have a look at some other solvers that belong to other categories below.

To see the details of the problems that we are looking at, toggle the blocks below.
There's animations in soem of them!

<details markdown="1">
<summary>Quadratic program (QP)</summary>

We'll start with a simple QP which is still interpretable for us to see whats going on.
For this simple case, we can also visualize iterates and whats going on in general much better than in the higher dimensional cases later on.

$$
\begin{align}
  \min_x\ & \ (x-q)^T R (x - q)\\
  \text{s.t.} \ & \ Bx \leq 0.
\end{align}
$$

In this case, we will leave out the equality constraint.

The problem we are setting up can then be seen as a problem where we are trying to find a value that is closest to a reference value, i.e, in a robotics context, this could be a setting where we try to find a joint pose which brings our end-effector close to some specified pose under some constraints.
</details>

<details markdown="1">
<summary>Constrained control (OCP)</summary>

The next problem is a QP that corresponds to trying to minimize a single step error under constraints, i.e., we try to steer a state to a reference state, but we do not yet do general MPC over a finite horizon, but only optimize the input for the next timestep.

We will minimize a cost such as acceleration, or energy consumption which can both be written as quadratic problem.
Additionally, we are trying to move our robot to a given setpoint, thus we also get a linear term:

$$
||x[t+1] - x_\text{ref}||_R + ||u||_Q.
$$

We assume that we have linear robot dynamics: 

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

Concretely, our system is a simple double integrator for a 6dim system, and the cost function is an identity matrix, i.e., equal weight on all states.
Additionally, we have a small regularization term for the input (the acceleration).

</details>

<details markdown="1">
<summary>Robot arm reference tracking (MPC)</summary>

We are going to extend the problem above to a path tracking problem in order to scale the problem up to a more realistic scenario.
Particularly, we need to define a time horizon (in number of steps), over which we will optimize.
This means that we will need to extend the cost function to deal with the whole horizon

$$
\sum_t^H||x[t] - x_\text{ref}[t]||_R + ||u[t]||_Q.
$$

The rest stays roughly the same, except that we are now going to have to deal with multiple states/inputs instead of only a single step, and a time dependent reference state.
We are again sticking to the same system dynamics and constraints, i.e., a double integrator with high velocity and acceleration limits compared to the positions.

In our case, the reference is stationary, and we have a cost on positions only for tracking, and the velocity parts are 0.
There is a light regularization on the acceleration input, and the horizon is $$H=100$$.

</details>

<details markdown="1">
<summary>Robot arm trajectory planning with energy minimization</summary>

In addition to the problem above, we now want to minimize the energy that the manipulator uses.
While it is possible to write that purely in terms of the inputs/states, we are going to introduce energy as a state, since we want to ensure that we obey some energy usage limits{% include sidenote.html text='For a static manipulator, this formulation does not make a lot of sense, since we usually can not deplete the energy resource that we are plugging the robot into. However, you could imagine a mobile manipulator with a battery here.'%}.
This also makes it possible to write the energy minimization problem as linear cost term of start minus end state.

We then change our cost function to a mixture of the reference tracking, and a term for the energy-usage minimization.
Additionally, we change the system dynamics to be closer to a true manipulator arm, i.e.,

$$M(q)\ddot q + b\dot q + g(q) = \tau,$$

In addition to this, we have the energy dynamics, which we encode as $$E_{k+1} = E_k − \Delta t p(\tau_k)$$, with $$p(\tau) = \text{2.5e5} \frac{\tau}{\tau_{\text{max}}}^2$$.

Similar to before, the task is moving from an initial state to a goal state, which is encoded as hard constraint.
As mentioned above, we have an additional state, namely the energy.
The cost function is then a linear term in the energy state, plus a small torque regularization.

The energy state is started at approximately $$10^6$$, while the other states are much smaller, and the problem is discretized with $$N=40$$ states.

An illustration of a solution to the problem is the following gif: 

<img src="{{ site.url }}/assets/opt-scaling/robotarm_energy_anim.gif" style="width:100%; padding:5px">


</details>

<details markdown="1">
<summary>MPCC</summary>

[In a previous post](/variable-dt-mpc), we looked at motion planning/control for a racecar using MPCC.
I wanted to apply the scaling to this as well.

Before we look at the nonlinear dynamics of the racecar, we do it with a simple (6d) masspoint where we assume jerk as input, i.e., a triple integrator.
This is one possible way of modelling path following with a robot, where each of the masspoints would correspond to a joint, and we want to track a joint space trajectory.

This is still a nonlinear problem due to the cost.
We formulate the track constraint as soft constraint, and the bounds are relatively low, except for acceleration at 30 rad/s^2 and jerk at 2000 rad/s^3.
The horizon is $$H = 30$$, and the contouring and lag cost can be found in the linked post.

We then also run this with the racecar dynamics, which makes both the system and the cost nonlinear.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/racecar_lap_anim.gif" style="width:60%; display:block; margin:0 auto; padding:5px">
</figure>

</details>

<details markdown="1">
<summary>Apollo lander</summary>

Contrary to the original example above in the related work, we now also want to land a rocket.
This is a 2D problem, i.e., we need to steer and regulate throttle.

The dynamics are otherwise very similar to the one introduced before for the rocket.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/lander_descent_anim.gif" style="width:100%; padding:5px">
</figure>
</details>


<details markdown="1">
<summary>Rocket</summary>
The rocket problem is exactly the same as the problem introduced above.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/rocket_ascent_anim.gif" style="width:100%; padding:5px">
</figure>

</details>

# Results
After introducing all the problems, we first show the reduction/increase in iteration count that the solver's own internal scaling gives when solving the introduced problems to a specified tolerance.
The speedup/reduction in iterations that are required is largely independent of the tolerance that we solve a problem to, so we solve the problems all to a tolerance of 1e-6 here.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/scaling_internal.png" style="width:100%; padding:5px">
<figcaption>Iteration-count speedup from the internal scaling of the respective solvers. ✗ = no convergence in the given iterations.</figcaption>
</figure>

In most cases, there's a no change to a moderate improvement for the solvers using the internal scaling.
However, we can also see that in some cases, this scaling actively hurts.
For OSQP in particular, some of the problems are not possible without doing some more work on them beforehand.
It is worth pointing out specifically again that even though the steps in the factorizing solvers are not affected by scaling (i.e., it cancels out if you write it out), the globalization strategies (line-search/termination tolerances) are.

Next, we do the same thing for the manual scaling.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/scaling_heatmap.png" style="width:100%; padding:5px">
<figcaption>Iteration-count speedup from the full scaling recipe. “req.” = the unscaled problem never converges; ✗ = no convergence even when scaled.</figcaption>
</figure>

Here, we can see that the manual scaling is significantly better than the solvers internal scaling.
We can also see that - contrary to the illustrative 2d example above - that the second order solvers can benefit from the scaling as well, particularly on the problems that are NLPs.

More details can be seen below, and we also have some data on how this iteration counts change solve time.

<details class="results-details" markdown="1">
<summary>Solve time — full numbers per solver &amp; scaling config (tol=1e-6)</summary>

<table class="results-table">
<thead>
<tr><th></th><th colspan="4">OSQP (ms)</th><th colspan="4" class="sol-sep">Clarabel (ms)</th><th colspan="4" class="sol-sep">IPOPT (ms)</th></tr>
<tr><th>Problem</th><th>unscaled</th><th>internal</th><th>col-scaled</th><th>full-scaled</th><th class="sol-sep">unscaled</th><th>internal</th><th>col-scaled</th><th>full-scaled</th><th class="sol-sep">unscaled</th><th>internal</th><th>col-scaled</th><th>full-scaled</th></tr>
</thead>
<tbody>
<tr><td>Quadratic program</td><td>0.7</td><td>0.6 (1.1×)</td><td>0.6 (1.1×)</td><td>—</td><td class="sol-sep">0.1</td><td><strong>0.0 (1.2×)</strong></td><td>0.1 (1.2×)</td><td>—</td><td class="sol-sep">16</td><td>15 (1.1×)</td><td>14 (1.1×)</td><td>—</td></tr>
<tr><td>Constrained control (single-step OCP)</td><td>0.7</td><td>0.8 (1.0×)</td><td><strong>0.7 (1.1×)</strong></td><td>0.7 (1.1×)</td><td class="sol-sep">1.8</td><td>1.8 (1.0×)</td><td>1.7 (1.0×)</td><td>1.7 (1.1×)</td><td class="sol-sep">19</td><td>18 (1.1×)</td><td>18 (1.1×)</td><td>18 (1.1×)</td></tr>
<tr><td>MPC (double integrator)</td><td>7961</td><td>8339 (1.0×)</td><td>153 (52.0×)</td><td><strong>133 (59.9×)</strong></td><td class="sol-sep">158</td><td>159 (1.0×)</td><td>149 (1.1×)</td><td>146 (1.1×)</td><td class="sol-sep">1126</td><td>1005 (1.1×)</td><td>734 (1.5×)</td><td>808 (1.4×)</td></tr>
<tr><td>Robot arm trajectory (energy min.)</td><td>—</td><td>—</td><td>2490</td><td>339</td><td class="sol-sep">554</td><td>289 (1.9×)</td><td><strong>244 (2.3×)</strong></td><td>342 (1.6×)</td><td class="sol-sep">3916</td><td>3920 (1.0×)</td><td>1426 (2.7×)</td><td>909 (4.3×)</td></tr>
<tr><td>MPCC with a masspoint</td><td>—</td><td>—</td><td>1654</td><td>4640</td><td class="sol-sep">419</td><td><strong>411 (1.0×)</strong></td><td>513 (0.8×)</td><td>609 (0.7×)</td><td class="sol-sep">4527</td><td>3674 (1.2×)</td><td>4482 (1.0×)</td><td>3935 (1.2×)</td></tr>
<tr><td>MPCC with a racecar</td><td>4135</td><td>4875 (0.8×)</td><td>1651 (2.5×)</td><td>1541 (2.7×)</td><td class="sol-sep">139</td><td>201 (0.7×)</td><td>162 (0.9×)</td><td><strong>138 (1.0×)</strong></td><td class="sol-sep">5753</td><td>10587 (0.5×)</td><td>6468 (0.9×)</td><td>5319 (1.1×)</td></tr>
<tr><td>Apollo lander</td><td>—</td><td>—</td><td>—</td><td>—</td><td class="sol-sep">344</td><td>368 (0.9×)</td><td><strong>291 (1.2×)</strong></td><td>298 (1.2×)</td><td class="sol-sep">730</td><td>971 (0.8×)</td><td>321 (2.3×)</td><td>514 (1.4×)</td></tr>
<tr><td>Landing a rocket</td><td>—</td><td>—</td><td>322</td><td>354</td><td class="sol-sep">235</td><td>248 (0.9×)</td><td>334 (0.7×)</td><td>551 (0.4×)</td><td class="sol-sep">264</td><td>286 (0.9×)</td><td>329 (0.8×)</td><td><strong>225 (1.2×)</strong></td></tr>
</tbody>
</table>

<p class="results-legend">Solve time per solver, and speedup value relative to the unscaled setting in parenthesis. Times are wall-clock (problem pre-built, warm, best of 3), measured identically for every solver. Bold = fastest solver on that problem.  — = reported wrongly as infeasible, or timed out.</p>
</details>

<details class="results-details" markdown="1">
<summary>Iteration counts — full numbers per solver &amp; scaling config (tol=1e-6)</summary>
<table class="results-table">
<thead>
<tr><th></th><th colspan="4">OSQP</th><th colspan="4" class="sol-sep">Clarabel</th><th colspan="4" class="sol-sep">IPOPT</th></tr>
<tr><th>Problem</th><th>unscaled</th><th>internal</th><th>col-scaled</th><th>full-scaled</th><th class="sol-sep">unscaled</th><th>internal</th><th>col-scaled</th><th>full-scaled</th><th class="sol-sep">unscaled</th><th>internal</th><th>col-scaled</th><th>full-scaled</th></tr>
</thead>
<tbody>
<tr><td>Quadratic program</td><td>81</td><td>30 (2.7×)</td><td>81 (1.0×)</td><td>—</td><td class="sol-sep">9</td><td>6 (1.5×)</td><td>8 (1.1×)</td><td>—</td><td class="sol-sep">7</td><td>7 (1.0×)</td><td>7 (1.0×)</td><td>—</td></tr>
<tr><td>Constrained control (single-step OCP)</td><td>58</td><td>58 (1.0×)</td><td>27 (2.1×)</td><td>25 (2.3×)</td><td class="sol-sep">6</td><td>6 (1.0×)</td><td>4 (1.5×)</td><td>4 (1.5×)</td><td class="sol-sep">6</td><td>6 (1.0×)</td><td>5 (1.2×)</td><td>5 (1.2×)</td></tr>
<tr><td>MPC (double integrator)</td><td>37849</td><td>37849 (1.0×)</td><td>981 (38.6×)</td><td>849 (44.6×)</td><td class="sol-sep">12</td><td>12 (1.0×)</td><td>10 (1.2×)</td><td>11 (1.1×)</td><td class="sol-sep">14</td><td>14 (1.0×)</td><td>13 (1.1×)</td><td>10 (1.4×)</td></tr>
<tr><td>Robot arm trajectory (energy min.)</td><td>—</td><td>—</td><td>14278</td><td>149</td><td class="sol-sep">273</td><td>103 (2.7×)</td><td>50 (5.5×)</td><td>30 (9.1×)</td><td class="sol-sep">102</td><td>102 (1.0×)</td><td>24 (4.2×)</td><td>8 (12.8×)</td></tr>
<tr><td>MPCC with a masspoint</td><td>—</td><td>—</td><td>13471</td><td>21051</td><td class="sol-sep">70</td><td>95 (0.7×)</td><td>73 (1.0×)</td><td>63 (1.1×)</td><td class="sol-sep">184</td><td>150 (1.2×)</td><td>182 (1.0×)</td><td>144 (1.3×)</td></tr>
<tr><td>MPCC with a racecar</td><td>40892</td><td>43805 (0.9×)</td><td>24034 (1.7×)</td><td>20480 (2.0×)</td><td class="sol-sep">53</td><td>78 (0.7×)</td><td>63 (0.8×)</td><td>56 (0.9×)</td><td class="sol-sep">107</td><td>203 (0.5×)</td><td>122 (0.9×)</td><td>95 (1.1×)</td></tr>
<tr><td>Apollo lander</td><td>—</td><td>—</td><td>—</td><td>—</td><td class="sol-sep">162</td><td>106 (1.5×)</td><td>45 (3.6×)</td><td>58 (2.8×)</td><td class="sol-sep">55</td><td>55 (1.0×)</td><td>10 (5.5×)</td><td>12 (4.6×)</td></tr>
<tr><td>Landing a rocket</td><td>—</td><td>—</td><td>662</td><td>4401</td><td class="sol-sep">151</td><td>126 (1.2×)</td><td>20 (7.5×)</td><td>53 (2.8×)</td><td class="sol-sep">45</td><td>45 (1.0×)</td><td>22 (2.0×)</td><td>8 (5.6×)</td></tr>
</tbody>
</table>


<p class="results-legend">Iteration count per solver, and speedup value relative to the unscaled setting in parenthesis.  — = reported wrongly as infeasible, or timed out;</p>
</details>

So the main takeway here should already be that you should in fact check if scaling might make sense for your optimization problem.
Scaling with the bounds, respectively the roughly expected size of the variables is a good default choice.
In the following, we will do some more digging on where scaling helps more and where it might help less, and we'll try to reason about where scaling helps.

#### Scaling in splitting solvers

To figure out why and how scaling makes a difference, we need to have a look at the two different groups of solvers that we considered:
OSQP, SCS (splitting based solvers), and Clarabel/IPOPT (factorization based solvers).

Our main hypothesis is that a large difference/ratio between the highest and the lowest state in the optimization problem is problematic.
When the states are all reasonably well behaved, the scaling does not make much of a difference.
The influence of how whitened the cost matrix is does seemingly also not have a huge influence.
Notably, in many cases, scaling drives the condition number of the KKT matrix up, but the solver stil gets faster.

After some experimentation, I have arrived at the hypothesis that for OSQP, the main driver seems to be the equality constraints in the problem and how they are treated.
To test this, we looked at a QP and an MPC problem (with equality constraints).
In the problems we varied the ratio of the bounds by scaling the system with $$x = A^\alpha \hat{x}$$ with $$\alpha\in[0,1]$$.

In this plot, the 'well scaled problem' is on the leftmost side, i.e. with a bounds-ratio of 1.
The systems on the rest of the x-axis are effectively 'worse-scaled' versions of the problem, until we arrive at the original problem formulation on the rightmost side.

We include Clarabel as solver to account for how 'hard' the problems are.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/scaling_decoupled_vs_coupled_oc_notitle.png" style="width:100%; padding:5px">
<figcaption>Left: QP with box constraints, no equality constraints. Right: Triple integrator MPC problem. x-axis is the ratio between the lowest and highest bound values, y-axis is the number of solver iterations.</figcaption>
</figure>

We can see that the number of iterations stay flat for OSQP on the problem without equality constraints (on the left side).
On the other hand, OSQP takes an increasing number of iterations the worse the problem is scaled if equality constraints are present in the problem.

We want to reiterate that this does not have anything to do with the 'hardness' of the problems, as the problems stay exactly the same over the whole range of the x-axis (stated differently: the problem stays the same, the formulation is just changed slightly through scaling).

Now, I am aware that this does not really answer the question _why_, but at least it gives us a point of attack:
We can dig a little deeper of whats going on with splitting methods when they are dealing with equality constraints.
OSQP treats the full constrained optimization problem as two steps: updating $$x$$ to minimize the cost (plus some other stuff), and trying to enforce the problem $$z = Ax$$, where $$z$$ must lie in the inequality constraints.
To satisfy the constraints, we can then simply project onto the box (and the equality constraints are parts of the box, where the lower and the upper bound coincide).
To reconcile these two problems, we deal with a dual variable $$y$$, which is updated as $$y += \rho (Ax - z)$$.
This means that a single $$\rho$$ should keep the primal and the dual residual balanced, which is hard if the states span multiple magnitudes (since we might have a large violation in one dimension, but a tiny one somewhere else).

#### Scaling in factorizing solvers

On the other hand, for factorization based solvers, they solve the KKT system at every iteration, so they should be completely invariant to affine scaling.
However, we have seen that there clearly are effects from scaling. 
How much we can notice them depends on the class of problems we solve: for the QPs, the effect is very moderate, and my hypothesis is that the only scaling influence comes from the termination tolerance (while the relative tolerance should not be influenced by scaling, the absolute tolerance usually is).
On the other hand, for the NLPs, the effect is in some cases much bigger (again, as seen above).

My assumption here is that the main effects are the globalization things that are happening in the solver: (1) line search is not immune to scaling, (2) the barrier is influenced by scaling (for IPOPT).
There might be other things, but these are the main effects I can think of at the moment.

Since the largest influence happens with the robot arm with energy regularization, we will use that as testbed. 

Luckily, we have access to a couple of the options that Ipopt exposes, and we can mess with a bunch of the things, to try to pinpoint what to do/whats the main driver behind the dependence on variable size and spread of bounds.
Before we start playing around with [options](https://coin-or.github.io/Ipopt/OPTIONS.html), we can check what Ipopt reports to us when solving the NLP.
We get some information on what operations were done during the iterations, and how many of them:

```
                         | unscaled | scaled
total iterations         |    407   |   17
damped steps (α<1)       |    377   |    0   
line-search backtracks   |   2525   |    0
restoration iters        |      2   |    0
Hessian regularizations  |     89   |    0
```

This shows that the whole globalization machinery is doing a lot of work on the unscaled problem: Ipopt is doing loads of linesearches, and needs many damped steps.
On the contrary, when the problem is scaled appropriately, we effectively only do newton steps in this problem.
This does not perfectly generalize to other problems though: In other problems, other components do more or less work.

Then, messing with the options one-by-one, and reporting the number of iterations the solver takes gives:

```
lever                          | unscaled | scaled | ratio
baseline (filter line search)  |   406    |   16   |  25.4
no line search (accept_every)  |    77    |   16   |   4.8  
penalty line search            |   100*   |   16   |  (*fails)
no 2nd-order corr (max_soc=0)  |   431    |   16   |  26.9   
adaptive mu                    |    21    |   17   |   1.2   
unscaled + IPOPT auto-scaling  |   406    |  (n/a) |        
```

And we can see that if we use adaptive mu scaling, the difference between scaling and not scaling is effectively gone.
The adaptive mu tends to be the largest lever for all the NLPs.

Now what does 'adaptive mu' mean?
Mu is the parameter used for scaling our barrier.
We need to choose (decrease) this parameter over time in order to make sure that the constraints of our problem are satisfied.
Ipopt chooses a monotone strategy ('Fiacco-McCormick approach') by default which gives relatively predictable convergence, but it can be very slow on badly scaled problems (as we have seen).
On the other hand, there is a an adaptive mode, which is more aggressive, and only switches to the monotone mode in case we do not get 'good' convergence.

#### Influence of problem size

Next, we have a look how the runtime of the solvers changes with problem sizes.
In this instance, we show a bunch more solvers, which we also tested above, but for ease of reading the stuff omitted.

The problem we are solving is an MPC problem, i.e., a robot arm trying to reach a goal, where we vary the horizon length.

<figure>
<img src="{{ site.url }}/assets/opt-scaling/size_speedup_notitle.png" style="width:100%; padding:5px">
<figcaption>Left: solver iterations vs. size — unscaled (solid) vs. scaled (dashed). Right: wall-clock vs. size.</figcaption>
</figure>

It is visible that the number of iterations stay roughly the same for all solvers, and that the only solvers that are actually changed significantly through scaling are the splitting (first order) solvers, as already seen above as well.
We can also notice that a higher number of solver iterations than another solver does not necessarily mean a higher runtime than another solver, since the iterations of the first order solvers are much cheaper.
Particularly, we notice that OSQP in its scaled variant is among the fastest solvers here, and is the fastest one by quite a margin in the largest problem instance.

This plot can also be seen as (post-hoc) justification of why we looked at the solvers we did above: OSQP, Clarabel and Ipopt are the fastest 3 solvers on the largest problem instance.

# Conclusion
I did not get the factor ~1000 speedup that we had originally, but I think the effect is there, and the rest is just a question of the exact parameters of the problem.

In this small adventure I learned a lot about sensitivity of various solvers to variable scaling.
As mentioned in the beginning, I used this as learning adventure for figuring out how to do research with AI (claude specifically).
I learned quite a few things there as well.
My main takeaway for this would be that very often you superficially get answers to your questions that are not always perfectly supported by the evidence. 
I had to do a lot of pushback against various argumentations for why scaling works/does not work, and often try to dig deeper with experiments that would give more evidence.
That being said, I think many of the experiments here would not have been possible for me in the time that I managed to do them with the help of claude.

I guess the main bottom line of this blog is that even if you think your solver is completely scale invariant, it likely is not.
Scaling the states to be reasonable close together clearly helps in most cases, but we have also seen that it can hurt in some cases.
So it is hard to give a general rule of thumb of where, when and how to scale. 

The best takeaway I could give here is that you should use all the knowledge you have to scale your problems, and just test it before deploying anything.

# Future Work

#### Scaling
While I very briefly tested cost function based scaling, it did not really help as much.
Similarly, we have the internal ruiz-equilibration that does effectively nothing in many cases.
We find that the scaling based on the expected solution size helps much more.
However, we have also seen that the whitening that is done in the 2D case required a generic affine transformation, and it would be nice to check if we can find a simple automatic scaling that takes stuff like this into account.

#### Benchmarking
[There are existing benchmarks for qp solvers](https://github.com/qpsolvers/mpc_qpbenchmark/tree/main), and it would be nice to add some of these problems that I considered here to the benchmarks.