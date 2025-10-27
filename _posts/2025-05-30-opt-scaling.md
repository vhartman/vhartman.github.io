---
layout: post
title:  "You should manually scale your optimal control problem"
date:   2025-10-28 12:00:00 +0200
permalink: /scaling-your-opt-problem/
categories: numerics path-planning science
---

<p class="preface">
In any kind of optimization problem, the scaling of the optimization variables should not change the optimal solution. However, depending on the solver, it changes how fast we get there (or if we get there at all depening on your solver settings).<br>

The magnitude of the influence (a solve-speedup of factor ~1000!) this has was very surprising to me at some point in an internship, and it was extremely surprising to everyone I ever told about it as well.
</p>

In robotics, you'll often run into various types of optimization problems.
It could be in [optimal control](https://en.wikipedia.org/wiki/Optimal_control), in [trajectory planning](https://en.wikipedia.org/wiki/Motion_planning), or even just when solvong the linearized QP for whole body [quadruped locomotion](https://ethz.ch/content/dam/ethz/special-interest/mavt/robotics-n-intelligent-systems/rsl-dam/documents/RobotDynamics2017/robot-dynamics-exercise-3-solution.pdf) (or for a humanoid if that's what you like).
In all these problems, you typically start by formulating your cost function, set up your constraints, and then pass it on to the solver of your choice, which then magically{% include sidenote.html text='This "magically" is doing a lot of heavy lifting here.'%} gives you a solution.

Your solver typically does gradient descent in some shape or form.
Generally, the 'same' optimization problem can be written in a couple of ways (i.e. the problem has the same optimum), and the solvers like some formulations better and some worse.

In an internship a while ago I worked on (nonlinear) optimal control, and implemented a framework for formulating and solving the problem.
While I knew at the time that solvers are somewhat prone to working much better with some formulation than others, I did not know how big of a difference in solve time just **scaling** your problem can have{% include sidenote.html text='I am excusing this lack of knowledge partially by solvers having a preprocessing step, and thus assuming that such scaling would happen in the solver itself if it would be benefitial.'%}.
That being said, this seems to be somewhat niche knowledge, since many people were surprised by the magnitude of the speedup that I got in that specific problem.

I never really dove much deeper at the time (mostly for the lack of time), regarding why that is, if all solvers are affected, and on which type of problem(s) such speedups can be observed.
But the topic has occupied a bit of my brain since then, and I wanted to finally investigate a bit more.

The code for this post is available [here](here).

# Related literature

When I first saw how big of an influence this scaling can have, I expected that this is a known thing, and was just a blindspot for me.
I expected not to be the first person running into this, and other people having lots of pratical advice on how to best scale your problem.

And I was and am not the first person running into this!

- The place where I found an example that scaling matters, and that it can save a lot of time is [from casadi](https://web.casadi.org/blog/nlp-scaling/).
Unfortunately some of the links in there are dead{% include sidenote.html text='Particularly, they link to some lectures from from John Betts which I can not find. But it seems like similar content is discussed in the [book here](http://www.digitalsats.com/reprints/Betts-2011-PracticalMethodsFor%20OptimalControlAnd%20EstimationUsingNonlinearProgramming_epdf.pub.pdf)'%}. They show the difference in convergence speed/number of required iterations for an example of controlling a 1D rocket, i.e., a nonlinear optimal control problem, and get a speedup of ~15-20 by scaling the optimization problem.

But while it is definitely known that scaling can have an impact on convergence and solve speed, it is not so widely (at least smongst the people that I know and worked with) known how much influence it can have.
There are some papers:

- [some discussion on scaling in traj opt](https://arxiv.org/pdf/2106.09125) and some more from the [same author](https://arxiv.org/pdf/1906.04857)
- ["Scaling and Balancing for High-Performance Computation of Optimal Controls"](https://arxiv.org/abs/1810.11073) is a paper on how to scale stuff.
- ["EXPLOITING SCALING CONSTANTS TO FACILITATE THE CONVERGENCE OF INDIRECT TRAJECTORY OPTIMIZATION METHODS"](https://arxiv.org/abs/2208.11273): paper

There is also not that much advice on _how_ you should transform your problem to get the best performance out of your solver.
The general advice is usually 'make everything the same magnitude', but that is very generic, and often not very actionable unfortunately.
Additionally, some solvers are invariant to the magnitude of the optimization variables, many are not, and so in the end what you should do is somewhat dependent on the solver that you are actually using.

- The [book from John Betts](http://www.digitalsats.com/reprints/Betts-2011-PracticalMethodsFor%20OptimalControlAnd%20EstimationUsingNonlinearProgramming_epdf.pub.pdf) gives some very good advice. Most of the things I summarize below comes from this book.
- The help page from [Altair Motion Solve](https://help.altair.com/hwsolvers/ms/topics/solvers/ms/optimization_advanced_topics_scaling_optimization_problem_r.htm) has some insights in why we scale, and how to scale. They also have an automatic scaling procedure.
- Next to the book above, [Optimagic](https://optimagic.readthedocs.io/en/latest/how_to/how_to_scaling.html) seems to be the closest to the thing I wanted at the time: advice on how to do scaling. Howeverm again there is no discussion on how much faster things can be.
- [Andrew Fitzgibbon](https://www.fitzgibbon.ie/optimization-parameter-scaling) gives some advice on scaling. It tracks with what John Betts says.
- There is [an article on scaling](https://www.alglib.net/optimization/scaling.php) and [practical tips](https://www.alglib.net/optimization/tipsandtricks.php)

# Scaling
I am predominantly interested in MPC and trajectory optimization for the full scale problems, but in the following, we'll also have a look at simpler QPs{% include sidenote.html text='Generally, when solving the more complex problems, they will also at some point end up in the form of a QP and be solved by a QP solver.'%} to see if there is a difference as well, respectively how big the difference is.
We are not going to go into too much depth here on how to formalize trajectory optimization problems (see [here](https://www.matthewpeterkelly.com/tutorials/trajectoryOptimization/index.html) for that), or how to do Model predictive control (see [e.g. here](https://idsc.ethz.ch/education/lectures/model-predictive-control.html) for that).
What I am interested in is how scaling affects these problems, repsectively the solve times and convergence.

Our QPs for optimal control will in all cases have:
- inequality constraints (which in optimal control usually take the form of box constraints coming from e.g. joint limits, or velocity bounds)
- equality constraints (from the system dynamics)
- a quadratic cost function (since we often want to minimize the energy, and a quadratic cost arises naturally)
- possibly reference tracking, so possibly also linear terms in the cost.

I.e. we roughly get a QP of the form

$$ 
\begin{align}
\min_x & \ x^T R x\\
\text{s.t.} & \ l \leq x \leq u\\
& \ Gx - f = 0.
\end{align}
$$

In such a QP we can apply a transformation of variables without changing the result, as long as we are able to revert the transform to recover the original optimization variables.
In order to maintain the convexity properties of the QP above, we are going to deal with an affine transformation $$x = A\hat{x} + b$$ to our original optimization variables.
The new QP will then be

$$ 
\begin{align}
\min_x & \ (A\hat{x} + b)^T R (A\hat{x} + b)\\
\text{s.t.} & \ l \leq (A\hat{x} + b) \leq u\\
& \ G(A\hat{x} + b) - f = 0,
\end{align}
$$

respectively

$$ 
\begin{align}
\min_\hat{x} & \ \hat{x}^TA^TRA\hat{x} + 2\hat{x}^TA^TRb\\
\text{s.t.} & \ A^{-1}(l-b) \leq \hat{x} \leq A^{-1}(u - b)\\
& \ GA\hat{x} + Gb - f = 0,
\end{align}
$$

which is another QP (where we dropped some constant terms from the objective already). 
After solving the new problem, we need to transform our variables back to obtain the variables that we cared  about initially.
Generally, our life will be easier if we assume that we can invert $$A$$, and even a bit simpler if we assume that $$b$$ is zero.
To simplify things a bit, I am going to assume $$b$$ is zero from now in (without loss of generality).

One of the main things to notice in the last QP is that we scale our objective with $$A^TRA$$, and we transform our bounds to be within $$A^{-1}l$$ and $$A^{-1}u$$.

The general advice is usually to scale the variables such that they are all in the same order of magnitude, and make a unit step in the variables correspond to a unit step in cost.
Using the scaling that we introduced above, we can try to scale our variables and bounds such that this is the case.

Betts further gives the advice that we can also scale our cost function with a constant, and we can scale the constraints with a constant as well.
His tips are:

[...]

# Problems

Generally, as said above, I am interested in optimal control and trajectory planning problems, and thus, the problems that I want to look at here are not general optimization problems, but should even in the simplest case have some of the properties of the optimal control problems{% include sidenote.html text='Importantly, this also means that the conclusions from this blog post should not be taken verbatim for a generic optimization problem.'%} mentioned before.


#### Control of a 1D rocket
Before looking at a couple of my own problems, we will reproduce the example used in the casadi blog above: control of a 1D rocket.
This is a nice example showcasing the possible improvements that we get quite well.

This is however also an extreme example in that the variables exhibt vastly different sizes if we use the physical representations.

#### Quadratic program
Moving to simpler (not non-convex) examples:
We'll start with a simple QP which is still interpretable for us to see whats going on.
For this simple case, we can also visualize iterates and whats going on in general much better than in the higher dimensional cases later on.

$$
\begin{align}
  \min_x\ & \ x^T R x + q^T x\\
  \text{s.t.} \ & \ Ax = 0 \\
  & \ Bx \leq 0,
\end{align}
$$

where we assume that $$R = \text{diag}(r)$$.
We will get to the specific values that we use in the experiments below.
I suspect that we might have to play around a bit to find a case where we we actually observe the effect that scaling matters.

#### Constrained control
Next problem is QP thath corresponds to trying to minimize a single step error under constraints.
We assume that we have some linear robot dynamics 

$$x[t+1] = Ax[t] + Bu[t],$$

where $$x$$ is the state at discrete time $$t$$ and $$u$$ is the input at the same time.
Further, we have box constraints on the states and inputs that correspond to e.g. torque or acceleration limits (for the input) and joint limits for the states.

We will minimize a cost such as acceleration, or energy consumption which can both be written as quadratic problem.
Additionally, we are trying to move our robot to a given setpoint, thus we also get a linear term:

$$
||x[t+1] - x_\text{ref}||_R + ||u||_Q
$$

We will assume that our acceleration and torque limits are much higher than the velocity and joint limits.

$$
\begin{align}
  \min_x\ & \ x^T R x + q^T x\\
  \text{s.t.} \ & \ x[1] = Ax[0] + Bu \\
  & \ x[0] = x_0\\
  & \ Gx \leq x_\text{lim}\\
  & \ Gu \leq u_\text{lim}\\
\end{align}
$$

#### Robot arm reference tracking
We are going to extend the problem above to a path tracking problem in order to scale the problem up to a more realistic scenario.
Particularly, we need to define a time horizon (in number of steps), over which we will optimize.
This means that we will need to extend the cost function to deal with the whole horizon

$$
\sum_t||x[t] - x_\text{ref}[t]||_R + ||u[t]||_Q.
$$

The rest stays roughly the same, except that we are now going to have to deal with multiple states/inputs instead of only a single step.

# Experiments

In the following, we will have a look at two different interfaces, casadi, and cvxpy for setting up the problems.
Casadi makes live easy by supporting nonlinear things as well, and gives access to IPOPT.
Cvxpy has a couple of different solvers, OSQP, and Clarabel among them which we will use{% include sidenote.html text='Amongst these solvers, there are some that are supposed to be invariant to scaling, and others that are not.'%}.

Of course, if we change the scale of the variables, and scale the objective, this influences the stopping criterion of the optimizers, so we'll need to have a look this as well.

The metrics that we are interested in are primarily the cost that we achieve, and since we have constraints, we want to ensure that the constraints are satisfied.

Since we are interested in the types of problems introdoced above, and they all have bounds on all of the variables, we can use the bounds in order to scale the problems.

# Discussion
...

# Conclusion
Use all the knowledge you have to scale your problems.


# TODO

- [ ] look at differen cost functions?
