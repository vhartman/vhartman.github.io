---
layout: post
title:  "A quick overview over rapidly exploring random trees"
date:   2018-03-26 01:31:34 +0200
categories: RRT pathplanning survey
published: false
---

I recently saw [a lecture][frazzoli-lecture] by Prof. Frazzoli, which renewed my interest in random trees. This led to me experimenting around with some variants of RRTs, and writig this post. This post is mostly for personal reasons ('if you can't explain something in simple terms, you don't understand it', etc.), and to start practicing my writing, and peresentation skills.

# Problem and basic idea
The problem setup for the application of RRTs are similar to any general path-planning problem:
 > Given some environment $$X$$, a starting point $$x_{int}$$, and an area $$X_{Goal}$$, find a path from the beginning to the end without intersecting with the obstacles $$X_{obs}\subset X$$.

As a simple example, look at the special example of $$X$$ being a square in the 2 dimensional space. The image below illustrates the statement above:


However, in comparison to other planning algorithms, no discretization of the environment $$X$$ is needed. RRTs operate directly on $$X$$ instead of some graph representation (which requires some form of discretization).

The basic idea behind rapidly exploring random trees was described in [Steven LaValles paper (pdf)][LaValle]:

Since the original paper, many improvements, along with a lot of analysis and convergence bounds have been suggested. This post will go over some of the interesting ones, and show some comparisons between the variants on a few different problems.

# RRT*

# Bidirectional RRT

# Informed RRT 

[frazzoli-lecture]: https://www.youtube.com/watch?v=dWSbItd0HEA
[LaValle]: http://msl.cs.illinois.edu/~lavalle/papers/Lav98c.pdf
