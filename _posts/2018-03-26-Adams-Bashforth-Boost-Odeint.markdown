---
layout: post
title:  "Semester thesis: Implementation of a numerical integrator for optimal control"
date:   2018-03-26 01:31:34 +0200
categories: control numerical integrator thesis
---

During my Semesterthesis (as a requirement for my degree), I worked on an implementation of a numerical integrator for [Boost Odeint][boost] at the agile and dextrous robotics lab ([ADRL][ADRL]) at ETH.

# Idea and motivation
When solving a kinematic planning problem with constraints, one approach is [Constrained SQL][CSLQ][^CSLQ], which is able to use variable-stepsize ODE solvers. However, it turns out that the equation that has to be integrated by the solver can be high-dimensional and thus very expensive to evaluate[^DRE].

Hence, we want to design an ODE solver that is able to use the benefits of variable stepsize (if nothing in our problem changes, we can use big steps for the integration), but minimizes the number of function evaluations as much as possible.

The class of [Linear Multistep Methods][LMM] tries to minimize the information gained in every function evaluation by combining previous evaluations in its computation. This is compared to one step methods, which discard the previously obtained information.

# Formulation of the Adams Bashforth Moulton (ABM) Integrator
When attempting to solve the equation 

$$ \mathbf{\dot{x}} = f(\mathbf{x}) $$

with $$ f  = (f_1, ... f_n)^T$$, and $$\mathbf{x} = (x_1, ..., x_n)^T$$, with a boundary value given, a numerical approach is generally needed.

The easiest approach is the discretization of the problem,

$$\mathbf{x}[k + 1] = \mathbf{x}[k] + h f(\mathbf{x}[k]) $$

is called Euler method, and is a special case of the ABM integrator. The Euler method can be thought of as follows: We take the initial equation again, and integrate both sides:

$$ \mathbf{x} = \int_{0}^{T} f(\mathbf{x}) dx $$

and approximate the integral on the right side as constant until we evaluate the function again. Thus, we get 

$$x[1] = hf(x[0]) + x[0]$$

$$x[2] = hf(x[1]) + x[1]$$

and so on.

If we now extrapolate the function with a polynomial of order $$k$$, we obtain the ABM-solution:

$$ \mathbf{x} = \int_{0}^{T} l(\mathbf{x}) dx $$

with $$l$$ being the polynomial approximation of $$f$$. Since it is possible to integrate a polynomial analytically, we can now solve the integral on the right side easily.

However, we skipped over the part of how to approximate the function $$f$$ with the polynomial $$l$$. Here is where the lagrange-polynomial comes into play. Since we know the values of the previous evaluations of the function $$f$$, we can use these to fit our polynomial $$l$$. The polynomial $$l$$ of order $$k$$ is fully determined by the previous $$k$$ points by the equation

$$abc$$

which is derived here.

The equation above simplyfies to ... if the space between evaluations is constant, which removes the complexity of having to recompute the coefficients, but also removes the freedom of being able to choose the stepsize as needed.

# Implementation
There are several ways of computing the coefficients of a lagrange polynomial, with various pros and cons.


# Results: Performance comparisons
- Pleiades etc.

[LMM]: https://en.wikipedia.org/wiki/Linear_multistep_method
[CSLQ]: https://arxiv.org/abs/1701.08051
[ADRL]: http://www.adrl.ethz.ch/
[boost]: http://www.boost.org/doc/libs/1_66_0/libs/numeric/odeint/doc/html/index.html

[^CSLQ]: More about constrained SQL in a future post.
[^DRE]: The discrete riccati equation, which results from the backward pass of the Constrained Algorithm is a matrix equation with $$n$$ dimensions, which in its naive expansion results in $$ n^2 $$ equations for the ODE.
