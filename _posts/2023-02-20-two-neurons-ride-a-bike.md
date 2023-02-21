---
layout: post
title:  "Replicating research: It takes two neurons to ride a bicycle"
subtitle: "or: .."
date:   2023-02-20 12:00:00 +0200
permalink: /two-neurons-bike/
categories: replication science
---

<p class="preface">
</p>

I wanted to recreate this paper from 2004 at NeurIPS: "...".

# Content

# Code
The complete code is available here[].

First, it turns out that it is actually hard to find the equations of motion that describe a bike.
There is a plethora of papers [] [] [] [], but in the end, it was much easier to just set this problem up in pybullet, and make a bike run in a full fledged simulator, compared to setting up some system of equations, and integrating that forward.

The bike I used was this one:

[image]

The paper then goes on to set up a fairly simple controller (one that has an oracle and can choose the best action by looking into the future one step andn choosing the best action) - we'll skip that part.

I implemented a reinforcement learining based approach:

[]

And I implemented the two-neuron-controller described by the paper.

# Results
#### Path of an unsteered bicycle
My initial core motivation for reimplementing this paper was Figure 2. from the paper:
[]

I was not able to get exactly the same result, but got pretty close.
Here's a few figures with different initial conditions:

[]

#### Sketchy RL solutions

#### The two neuron controller and tracing a path
