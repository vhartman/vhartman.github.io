---
layout: post
title:  "Sampling manifolds for robotics path planning"
date:   2024-10-01 12:00:00 +0200
permalink: /sampling-constraints/
categories: performance planning
---

<p class="preface">
    We are currently working on doing motion planning for multiple robots for multiple goals in sequence.
    In some contexts of (multi robot) path planning, we care about satisfying some constraints in addition to just finding collision free paths.
    Thus, we somehow need to be able to satisfy various constraints with the paths that we take. 
</p>

In [other work](/mrmg-planning/) we presented a couple of multi robot motion planners and loads of benchmarks (i.e. different problems) to find paths that go to a series of goals.
In that work however, we did only do unconstrained path planning.
In practical words, that means that we could e.g. not plan for a problem that requires 'grasping an object with two arms', since that would constrain the manipulators to have the same relative transformation at all times for the duration while the object is grasped.

Since we only implemented samping based path planners, to deal with constraints in our planners, we simply{% include sidenote.html text='Much easier said than done.'%} sample only the constraint-manifold{% include sidenote.html text='There are a couple more things we need to do, but once we have a method to project a sample to a manifold, we can reuse that for all the other things we need to do as well.'%}.

Obviously, there is a lot of work on projection of samples onto constraint manifolds:

# Constraints
In the most generic form, we can write our constaints as 

$$g(q) \leq 0,$$

where we have a vector valued $$q$$, and a vector-function $$g$$.
Since we can also represent equality with the inequality constraint above, this is the most generic form we can attain.

Now in general, we have more structure, and using that structure usually helps design faster algorithms.
Our motivation is the example of a multi-robot setting, and as such, we use the structure we have there:
Our configuration becomes a stack of robot configurations $$q = [q_1, ..., q_N]$$, and since we have a bunch of different constraints with different properties, we do not take the most generic form there either:

$$
\begin{align}
A_\text{eq}q &= b_\text{eq}\\
A_\text{ineq}q &\leq b_\text{ineq}\\
h(q) &= 0\\
g(q) &\leq 0
\end{align}
$$

We have linear equality, and inequality constraints, and non-linear equality and inequality constraints.
We could further split this up by also using the structure in $$q$$ here, but we'll leave that for now.

Our goal is then to find a uniform set of points that satisfies the constraints above.
Since we are going to need to sample from the manifold of constraint satisfying configurations thousands of times, we would like to make this as fast as possible.

# Finding constraint satisfying points

The most straightforward thing we can do to find a point that satisfies the consditions above is formulating this as an optimization problem:

$$
\begin{align}
\min_q\  & \ ||q_\text{rnd} - q||_2\\
\text{s.t.}\ & A_\text{eq}q = b_\text{eq}\\
& A_\text{ineq}q \leq b_\text{ineq}\\
& h(q) = 0\\
& g(q) \leq 0
\end{align}
$$

and then use your favourite solver to deal with this. Solvers differ quite a bit in how this constrained problem is dealt with.
A simple approach is movig the constraints in to the objective, and then solving the problem how an unconstrained problem would be solved (using Newton's method):
typically with simple gradient descent, i.e., taking the derivative to figure out the direction in which we would like to take a step, doing a line search to figure out the step length, and then iterating this.

Generally, this is not the most efficient way to deal with this, especially for high dimensional settings, with possibly complex constraint manifolds.
Again, since the constraints that we are dealing with are not simply a black box to us{% include sidenote.html text='I.e., we are not really trying to solve the general case of solving a constrained optimization problem'%}, we can use the structure of the constraints and the configurations.
Adding to this, [recent work](https://arxiv.org/pdf/2410.21630) in constrained robot motion planning in high dimensional spaces suggests that vanilla gradient descent can not nicely fulfill the constraints (that are all in different units!) to a desired tolerance easily. 

#### Related work

Of course there are loads of previous methods to solve this problem.
I am trying to get rid of my open tabs, so I am listing mostly the ones I have seen so far/found in brief research.
These might not be the most efficient, and experiments need to be done to figure out what works best (for us).

The thing that is different for u sthan most constraint optimization problems is that we would ideally want a uniform covering of the manifold.
If we are projecting to the manifold, we tend to only get boundary points.
While that is fine to _solve_ the planning problem, we usually do not want to only move along the boundary for a variety of reasons:
the path might be more optimal on the inside of the manifold, and there might be safety issues _at_ the boundary.

**Dealing with constraints in optimization problems**

I want to reiterate here again that this is by no means a comprehensive overview for how to deal with constraints in optimization problems.

- Newton's method: Projects iteratively to the contraint manifold roughly as desried above.
- [Randomized gradient descent](https://www.sciencedirect.com/science/article/pii/S0893965920303712): Does roughly what the name says - we do gradient descent, but at each iteration, we randomly choose a subset of the whole system to solve. This minimizes some computational issues that would occur with large Jacobians (etc. etc).
- There are a bunch of variants using Pseudoinverses of the Jacobina in order to deal with underdetermined/overdetermined systems. This is what we need to do as well, since typically not all of our degrees of freedom are constrained.
- Cimminos algorithm similarly solves a system of linear equations. it does so by projecting the current iterate $$x$$ onto for each row of constraints, and then taing a step that is a weighted sum of all row-steps.
- [Nonlinear cimmino](https://link.springer.com/article/10.1007/BF01389537) takes the same idea, but projects onto the tangent hyperplane per row. 

Compared to the methods above, there are methods that do not try to solve the whole system of constraints in one go, but cycle through constraints one at a time.
Randomized gradient descent also counts to those.
- [Kaczmarz Method (Wikipedia)](https://en.wikipedia.org/wiki/Kaczmarz_method), and the [nonlinear version of Kaczmarz](https://www.sciencedirect.com/science/article/abs/pii/S0377042721003423?casa_token=bYklnHFN8B0AAAAA:KocLni9N-qipGrxo1-z4ONXQu3cUV2tknT9QSqtqGq0e0SQ6XEMIeQ0TQBwsmkgOf82C0Rr5ih4). Kaczmarz' method originally solves $$Ax = b$$ for large overdetermined systems. Effectively the thing that the algorithm does is simply goign through the rows of the constraints one by one and projecting the current iterate onto the (partial) solution manifold given by the row we are currently looking at. <br>
  The nonlinear extension effectively just takes rows of the nonlinear constraint, and (nonlinearly) projects onto the solution manifold as well. This projection can happen either via linearization and (linear) projection, or just nonlinear projection. 

**Sampling constrained manifolds in robotics**

As alluded to above, sampling a constraint manifold is a common thing for many robotics algorithms.
I'll list some approaches and sources here mostly for motion planning.

- Englert at al. have some work on planning on [constraint manifolds](https://arxiv.org/pdf/2006.02027), but do not mention what type of projection they do. Just that they project each sample to the relavant manifold.
- [Constellation](https://personalrobotics.cs.washington.edu/publications/kaiser2012constellation.pdf) is an algorithm for IK that uses a smart exploration strategy taking previous attempts into account. Projection itself is cyclic.
- The paper [Constrained Nonlinear Kaczmarz Projection on Intersections of Manifolds for Coordinated Multi-Robot Mobile Manipulation](https://arxiv.org/abs/2410.21630) is to a certain extent the reason for this writeup, as this paper made me realize that there is a relatively wide range of literature that is concerned with how to sample fast. They apply nonlinear Kaczmarz to the problem of projecting samples to a complex set of constraint manifolds.
- [Task Constrained Motion Planning in Robot Joint Space](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4399305)
- [Learning Efficient Constraint Graph Sampling for Robotic Sequential Manipulation](https://arxiv.org/pdf/2011.04828)

# Some concrete (simple) examples

We are going to look at two very simple settings:

- a dual arm end-effector that has a shared degree of freedom: 
- A single arm motion planner that should follow an end-effector path.

...