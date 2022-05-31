---
layout: post
title:  "Robotic stippling: Finding optimal sequences"
subtitle: "or: Abusing lab equipment v3"
date:   2022-05-28 12:00:00 +0200
permalink: /optimal-stippling/
categories: art 
---

<p class="preface">
    In part 1, and part 2 of this series, I alook ed at producing dots on a piece of paper in a really complicated way: By using multiple robots.
    So far, I was not too concerned with finding an optimal solution, but rather with finding a solution that works well for one (in part 1) or two (in part two) robots.
    
    Now, I want to look at how big the difference between an optimized solution, and the greedy solutions I produced so far is.
</p>

Previously  for a general overview on what I am trying to do here:
In previous posts, I looked at finding poses to make dots, sorting the poses, and then finding paths for one robot in [part 1](/robo-stippling/), and for two robots in [part 2](/robo-stippling-p2/).
Even though this is part 3, I am now not going to look at extending our approach to three robots.

Instead, I am going back to using a single robot for now, and comparing my previous approach of generating one pose and ordering the poses greedily compares to generating multiple poses, and finding the (optimal) path.

#### Problem setting
I am still assuming that I am getting a set of dots (2d coordinates) wand want to output a path for the robot that makes those dots onto the paper.

Compared to part 1, I am now trying to actually find an optimal path for the robot though.
That is, I want to find the time-optimal path that makes all the dots.

Mathematically, our problem is this:


which is the Traveling Salesman Problem in Neighbourhoods.

Prior research for this problem are e.g. 
\[[1](https://cse.cs.ovgu.de/cse/traveling-salesman-problem-with-neighborhoods-tspn)\],
\[[2](https://www.tandfonline.com/doi/abs/10.1080/10556788.2011.648932)\],
\[[3](https://www.ac.tuwien.ac.at/files/pub/hu-08.pdf)\],
or the two following here, that are concerned with problems where the path planning is a bottle neck as well 
\[[4](http://timroughgarden.org/papers/ijrr.pdf)\]
\[[5](http://old.sztaki.hu/~akovacs/publications/ijpr2016.pdf)\].

The problem we are tackling here is the 'easy' version, since we do not have any obstacles in the environment which may make our path planning harder.
As such, the goal we have is really finding an optimal sequence of poses, i.e. finding the sequence, and finding the right pose.

#### Solving the TSP for a single pose

I first implement a proper TSP algorithm for the single-pose case.
Even though we likely have little enough poses to being able to find the exact solution, I am not going down that path.

We are implementing a few approximation algorithms:

- Greedy with longer lookahead
- Simulated annealing
- Ant colony optimization

In all cases, I run the resulting path through an algorithm that tries to improve the result that we got.
Here, I do that by locally reversing subtours.

#### Solving the TSP for a neighbourhood

...

#### Comparison

To compare the planners we produced above, we need a few testcases.
We largely reuse things we have used before: a grid, a set of random points, a circle, a spiral, the projection of randomly distributed dots on a sphere in 2d, and part of our labs logo.

<div style="width: 80%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/grid.png" style="width:25%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:25%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:25%; padding: 5px">
<br>
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:25%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:25%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:25%; padding: 5px">
</div>

Baseline from before: greedy

Greedy with sets

TSP with a single pose

TSP with a set of poses

#### Takeway
