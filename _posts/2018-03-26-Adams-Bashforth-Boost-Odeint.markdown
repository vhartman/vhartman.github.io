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

$$ \mathbf{x}(T) = \int_{0}^{T} f(\mathbf{x}) dx $$

and approximate the integral on the right side as constant until we evaluate the function again. This means that we get 

$$ \mathbf{x}(T) = \int_{0}^{t_1} f(\mathbf{x}(t_0)) dx +  \int_{t_1}^{t_2} f(\mathbf{x}(t_1)) dx + ...$$

One problem is left, namely that we do not know the value of $$\mathbf{x}(t_1)$$ without first computing the first integral.

Thus, we solve one integral after another, and obtain

$$x[1] = hf(x[0]) + x[0]$$

$$x[2] = hf(x[1]) + x[1]$$

and so on.

Exchanging the constant approximation with a polynomial of order $$k$$, we obtain the ABM-solution:

$$ \mathbf{x} = \int_{0}^{T} L(\mathbf{x}) dx $$

with $$L$$ being the polynomial approximation of $$f$$. With this, we can transform the equation above to 

$$ \mathbf{x}(T) = \int_{0}^{t_1} L(\mathbf{x}(t_0)) dx +  \int_{t_1}^{t_2} L(\mathbf{x}(t_1)) dx + ...$$

Since it is possible to integrate a polynomial analytically, we can now solve the integrals easily to get from one step to the next one.

However, we skipped over the part of how to approximate the function $$f$$ with the polynomial $$l$$. Here is where the lagrange-polynomial comes into play. Since we know the values of the previous evaluations of the function $$f$$, we can use these to fit our polynomial $$L$$. The polynomial $$L$$ of order $$k$$ is fully determined by the previous $$k$$ points, resulting in the equation

$$L(x) := \sum_{j=0}^{k} f(x_j) \ell_j(x)$$

with the Lagrange basis polynomials $$\ell$$:

$$\ell_j(x) := \prod_{\begin{smallmatrix}0\le m\le k\\ m\neq j\end{smallmatrix}} \frac{x-x_m}{x_j-x_m} = \frac{(x-x_0)}{(x_j-x_0)} \cdots \frac{(x-x_{j-1})}{(x_j-x_{j-1})} \frac{(x-x_{j+1})}{(x_j-x_{j+1})} \cdots \frac{(x-x_k)}{(x_j-x_k)}$$

Thus, we can solve the integral 

$$\begin{align}
\int_{t_n}^{t_{n+1}} L(\mathbf{x}(t_n)) dx &= \int_{t_n}^{t_{n+1}} \sum_{j=0}^{k} f(x_j) \ell_j(x) dx \\ &= \sum_{j=0}^{k}f(x_j)\int_{t_n}^{t_{n+1}} \ell_j(x) dx \end{align}$$

which clearly has an analytical solution. To get to the ABM method, we make the method above into an implicit method. For the Euler method analogy from above, this means that the constant value is now equal to the function evaluated at the end-point, i.e.

$$\mathbf{x}[k + 1] = \mathbf{x}[k] + h f(\mathbf{x}[k+1]) $$

This implicit equation can be solved using various methods. A common one is the predictor-corrector approach, meaning that we first predict the value, and then correct it, using a different formula, for example an explicit one, like the euler formula introduced above. This results in the iteration: ...



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
