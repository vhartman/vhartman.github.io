---
layout: post
title:  "Semester thesis: Implementation of a numerical integrator for optimal control"
date:   2019-11-01 01:31:34 +0200
categories: control numerical integrator thesis
---

During my Semesterthesis (as a requirement for my degree), I worked on an implementation of a numerical integrator for [Boost Odeint][boost] at the agile and dextrous robotics lab ([ADRL][ADRL]) at ETH.

# Idea and motivation
When solving a kinematic planning problem with constraints, one approach is [Constrained SQL][CSLQ][^CSLQ], which is able to use variable-stepsize ODE solvers. However, it turns out that the equation that has to be integrated by the solver can be high-dimensional and thus very expensive to evaluate[^DRE].

Hence, we want to design an ODE solver that is able to use the benefits of variable stepsize (if nothing in our problem changes, we can use big steps for the integration), but minimizes the number of function evaluations as much as possible.

The class of [Linear Multistep Methods][LMM] tries to minimize the information gained in every function evaluation by combining previous evaluations in its computation. This is compared to one step methods, which discard the previously obtained information.

# Formulation of the Adams Bashforth Moulton (ABM) Integrator
Refer to [xyz] for an introduction to numerical integration.
Exchanging the constant approximation with a polynomial of order $$k$$, we obtain the ABM-solution:

$$ \mathbf{x} = \int_{0}^{T} L(\mathbf{x}) dx $$

with $$L$$ being the polynomial approximation of $$f$$. With this, we can transform the equation above to 

$$ \mathbf{x}(T) = \int_{0}^{t_1} L(\mathbf{x}) dx +  \int_{t_1}^{t_2} L(\mathbf{x}) dx + ...$$

Since it is possible to integrate a polynomial analytically, we can now solve the integrals easily to get from one step to the next one.

However, we skipped over the part of how to approximate the function $$f$$ with the polynomial $$l$$. Here is where the lagrange-polynomial comes into play. Since we know the values of the previous evaluations of the function $$f$$, we can use these to fit our polynomial $$L$$. The polynomial $$L$$ of order $$k$$ is fully determined by the previous $$k$$ points, resulting in the equation

$$L(x) := \sum_{j=0}^{k} f(x_j) \ell_j(x)$$

with the Lagrange basis polynomials $$\ell$$:

$$\ell_j(x) := \prod_{\begin{smallmatrix}0\le m\le k\\ m\neq j\end{smallmatrix}} \frac{x-x_m}{x_j-x_m} = \frac{(x-x_0)}{(x_j-x_0)} \cdots \frac{(x-x_{j-1})}{(x_j-x_{j-1})} \frac{(x-x_{j+1})}{(x_j-x_{j+1})} \cdots \frac{(x-x_k)}{(x_j-x_k)}$$

which is a polynomial of degree $$k$$. Thus, we can solve the integral 

$$\begin{align}
\int_{t_n}^{t_{n+1}} L(\mathbf{x}(t_n)) dx &= \int_{t_n}^{t_{n+1}} \sum_{j=0}^{k} f(x_j) \ell_j(x) dx \\ &= \sum_{j=0}^{k}f(x_j)\int_{t_n}^{t_{n+1}} \ell_j(x) dx \end{align}$$

which has an analytical solution (due to being a polynomial).

To arrive at the implicit Adams Bashforth Moulton method, we make the method above into an implicit method, i.e. the next value depends on the value of the function evaluation at the next point:

$$\mathbf{x}[k + 1] = \mathbf{x}[k] + h f(\mathbf{x}[k+1]) $$

which becomes the following in the context of the Adams Moulton method:

This implicit equation can be solved using various methods. A common one is the predictor-corrector approach, meaning that we first predict the value, and then correct it with the implicit formula. 

Naturally, this leads us to the combination of the Adams Bashforth (explicit) and the Adams Moulton (implicit) methods for our predictor and corrector.


# Implementation
The main part of our implementation is the computation of the coefficients for the lagrange polynomial. There are some additional difficulties if we implement the integrator to allow for a variable stepsize (how do we choose the stepsize?), but we will leave that out for now.

As such, the general algorithm is

{% highlight python %}
def ABM(x_0, T, order, dt):
    t = 0
    
    x_prev = [x_0]
    f_prev = [f(x_0)]

    while t < T:
        # predict
        x_pred = x_prev[-1] + AB(x_prev, f_prev)
        f_pred = f(x_pred)

        # correct
        x_corr = x_prev[-1] + AM(x_prev + [x_pred], f_prev + [f_pred])
        f_corr = f(x_corr)

        # update bookkeeping
        ind = min([len(x_prev), order]) - 1

        x_prev = x_prev[:ind] + x_corr
        f_prev = f_prev[:ind] + f_corr
        t += dt

    return x_prev[-1]
{% endhighlight %}

{% highlight python %}
def AB(x, f):
    
    coefficients = compute_lagrange_coefficients(x)
    
{% endhighlight %}

{% highlight python %}
def AM(x):
    pass
{% endhighlight %}

{% highlight python %}
def integrate_polynomial(x):
    pass
{% endhighlight %}

{% highlight python %}
def compute_lagrange_coefficients(x):
    pass
{% endhighlight %}
<!-- # Results: Performance comparisons
There are some standard ODEs for the evaluation of the performance and accuracy of numerical integrators. Commonly used are:

- A simple system (for debugging purposes):

$$\dot{x} = -x$$

- A simple harmonic oscillator:

$$\left[ \begin{array}{c}\dot{x}_1\\ \dot{x}_2\end{array}\right] = \left[ \begin{array}{cc}0 & -1\\ 1 & 0\end{array} \right]\left[ \begin{array}{c}x_1\\ x_2\end{array}\right]$$

- The Arenstorf orbit, a three body system, where one body is fixed:

$$\begin{align}
        \dot{x}_1 &= x_2\\
        \dot{x}_2 &= x_1 + 2x_4 - (1-\mu)\frac{x_1+\mu}{d_1}\\
        \dot{x}_3 &= x_4\\
        \dot{x}_4 &= x_3 - 2x_2 - (1-\mu)\frac{x_3}{d_1} - \mu \frac{x_3}{d_2}
    \end{align}$$

with

$$\begin{align}
        d_1 &= ((x_1+\mu)^2+x_3^2)^{3/2}\\
        d_2 &= ((x_1-(1-\mu))^2+x_3^2)^{3/2}
    \end{align}$$

- Pleiades, a seven body orbital mechanics problem:

$$\ddot{x}_i = \sum_{j\neq i} m_j \frac{x_j - x_i}{r_{ij}}\qquad \ddot{y}_i = \sum_{j\neq i} m_j \frac{y_j - y_i}{r_{ij}}$$

with 

$$
        r_{ij} = \left((x_i-x_j)^2 + (y_i-y_j)^2\right)^{3/2}
$$ -->

[LMM]: https://en.wikipedia.org/wiki/Linear_multistep_method
[CSLQ]: https://arxiv.org/abs/1701.08051
[ADRL]: http://www.adrl.ethz.ch/
[boost]: http://www.boost.org/doc/libs/1_66_0/libs/numeric/odeint/doc/html/index.html

[^CSLQ]: More about constrained SQL in a future post.
[^DRE]: The discrete riccati equation, which results from the backward pass of the Constrained Algorithm is a matrix equation with $$n$$ dimensions, which in its naive expansion results in $$ n^2 $$ equations for the ODE.
