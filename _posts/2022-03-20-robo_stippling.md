---
layout: post
title:  "Making dots with a robot arm"
subtitle: "or: ..."
date:   2022-04-10 12:00:00 +0200
permalink: /robo-stippling/
categories: art 
---

<p style="font-style: italic">
    We are abusing a 20k robot arm because I a stuck with my research.
</p>

<!--<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: -50px;height: 300px;padding: 10px;font-size:10pt; width:200px">
<sup>1</sup>
The code is not yet available because I am still in the process of changing around a few things.
</p>
</div>-->

# Preparing the image
Stippling.

But for now, we just assume that we gat a list of dots as input, that we only need to make on the paper.

# Computing Paths

To compute the path that the robot needs to make, we need to know a few things: the order in which the dots should be drawn, and the pose that the robot needs to be in to actually make a dot onto the paper.

We solve these in inverse order: We first compute the pose in which the robot needs to be in, and then we take these poses and figure out how to go through them to efficiently draw all of them.

#### Sampling positions: Solving an inverse kinematics problem

Finding a pose of the robot that results in the tip of the pen being in a certain place in 3D-space is known as inverse kinematics problem.

For simplicity, we are going to assume that there is only one configuration per dot we are making.
It would technically be possible to allow multiple configurations that all result in the same dot.
That would make planning later on more optimal (because we can choose the best of the configurations) but also more complex.

#### Connecting the positions
Now that we have all configurations that we need to connect, we can compute the paths between them.


TSP!

# Simulated results

# Results
[images]

# Further work
