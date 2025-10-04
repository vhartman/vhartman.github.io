---
layout: post
title:  "Sampling manifolds for robotics path planning"
date:   2024-07-12 12:00:00 +0200
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
A_\text{eq}q = b_\text{eq}\\
A_\text{ineq}q \leq b_\text{ineq}\\
h(q) = 0\\
g(q) \leq 0
$$

We have linear equality, and inequality constraints, and non-linear equality and inequality constraints.
We could further split this up by also using the structure in $$q$$ here, but we'll leave that for now.

Our goal is then to find a uniform set of points that satisfies the constraints above.

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

and then use your favourite solver to deal with this.
Generally, this is not the most efficient way to deal with this{% include sidenote.html text='Since we are going to need to sample from the manifold of constraint satisfying configurations thousands of times, we would like to make this as fast as possible.'%}.

- [Robot planning, projection](https://arxiv.org/pdf/2006.02027)
- Ranomized gradient descent
- Newton raphson

- [constellation](https://personalrobotics.cs.washington.edu/publications/kaiser2012constellation.pdf)
- [Kaczmarz](https://en.wikipedia.org/wiki/Kaczmarz_method)
- [More Kaczmarz](https://www.sciencedirect.com/science/article/abs/pii/S0377042721003423?casa_token=bYklnHFN8B0AAAAA:KocLni9N-qipGrxo1-z4ONXQu3cUV2tknT9QSqtqGq0e0SQ6XEMIeQ0TQBwsmkgOf82C0Rr5ih4)
- [Constrained Nonlinear Kaczmarz](https://arxiv.org/pdf/2410.21630)