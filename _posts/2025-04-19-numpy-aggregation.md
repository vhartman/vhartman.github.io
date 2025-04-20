---
layout: post
title:  "So you think numpy is always the fastest?"
subtitle: "or: How to best compute sums of euclidean distances."
date:   2025-04-20 12:00:00 +0200
permalink: /fast-numpy-aggregation/
categories: numerics path-planning science
---

<p class="preface">
In multi robot planning, you'll need to compute some cost or distance at some point. Depending on how you represent a configuration, this might require different sequences of operations. <br>
In my case, I have an n-dimensional array, and I want to compute the euclidean distance over a set of (non-overlapping) slices, and then take the sum or the max of the separate values.

You'd think that just doing this with generic numpy operations is always the fastest approach. <br><br>
Spoiler: You would be wrong.
</p>

This post is motivated by my recent work on multi-robot multi-goal motion planning, where to decide what is a good path, we want to compute a cost or a distance that depends on multiple robots, and their respective poses.

Concretely, I want to compute

$$
c(q_1, q_2) =  w\sum_{i\in R} ||q_1^i - q_2^i||_2 + (1-w)\max_{i\in R} ||q_1^i - q_2^i||_2
$$

where $$q_1 = [q_1^1 ... q_1^R]$$, and the same for $$q_2$$.
It is important to note here that I do want to compute this number for many different configurations $$q$$, so clearly I want to batch this.

In the general case, we also don't always use the euclidean norm as single-robot metric, but sometimes want to use a more general L-p norm.

{% include sidenote.html text="In the general case, we also don't always use the euclidean norm as single-robot metric, but sometimes want to use a more general L-p norm."%}.

Code for everything can be found [here](https://github.com/vhartman/nu-nmpc/tree/blog_version).

# Baseline

Translating the formula above into code is relatively straightforward:

```python
if...:
  pass

```

We'll run this for different numbers of points, and different dimensionalities of slices, we get the following curves:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_5.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_10.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_20.png" style="width:29%; padding: 10px">
  <figcaption><span style="color: #1f77b4;">Blue</span> is position, <span style="color: #ff7f0e;">orange</span> is velocity, and <span style="color: #2ca02c;">green</span> is acceleration. The constraints for each variable are shown in the corresponding color.</figcaption>
</div>

Even though this i snot extremely slow on an absolute scale, in the motion planning pipeline, this now makes up for a majority of the runtime, since this is called very often in some of the subroutines.

# Enter: numba
Running cProfile on this whole thing shows that computing the euclidean distance over the slices is most problematic, and we'll first focus on this part.

#### Speeding up the euclidean distance over slices

As first attempt to speed this up, we'll just take the thing as a whole and jit it using numba.
There are a few small things we need to do, since numba does not like some of the things we did so far:

```python
```

This results in the following curve, already giving a massive speedup.
This speedup is (was) already enough to not make this part of the code the bottleneck anymore at the time.
However, we are now in the rabbithole of trying to optimize this as much as possible, so we go on.

We can try to parallelize this:

[...]

Sadly, this did not work. 
I do not have a great explanation, but I am assuming that the overhead is simply not worth it given that the separate operations are fast.

We can still do better for the sliced distance by ...

```python
```

And the corresponding curves:

#### Speeding up the sum and max reductions
Since we were succesful with numba before, why change the receipe? Here we go:

```python
```

Curves:

#### But a simple multiplication is still best in numpy right?

For all of the code, we always kept the squared difference in numpy so far- Is that a good idea?

# Conclusion & Outlook
