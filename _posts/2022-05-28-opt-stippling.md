---
layout: post
title:  "Robotic stippling: Finding optimal sequences"
subtitle: "or: Abusing lab equipment v3"
date:   2022-05-28 12:00:00 +0200
permalink: /optimal-stippling/
categories: art 
---

<p class="preface">
    In part 1, and part 2 of this series, I looked at overengineering making dots on a piece of paper: Using multiple robots.
    So far, I was not too concerned with finding an optimal solution, but rather with finding a solution that works well for one (in part 1) or two (in part 2) robots.
    
    Now, I want to look at how big the difference between an optimized solution, and the greedy solutions I produced so far is.
</p>

For a general overview on what I am trying to do here:
In previous posts, I looked at finding poses to make dots, sorting the poses, and then finding paths for one robot in [part 1](/robo-stippling/), and for two robots in [part 2](/robo-stippling-p2/).
Even though this is part 3, I am now not going to look at extending our approach to three robots.

Instead, I am going back to using a single robot for now, and comparing my previous approach of generating one pose and ordering the poses greedily compares to generating multiple poses, and finding a more (optimal) path.
{% include sidenote.html text='I do not yet want to claim _the_ optimal path, since I am still making a few approximations that impact the optimality along the way.' %}

#### Problem setting
I am still assuming that I am getting a set of dots (2d coordinates) wand want to output a path in jointspace for the robot that makes those dots onto the paper.
I am planning geometrically, i.e. not taking any robot dynamics into account.
This is a valid approximation, since we have a good low lever controller, that (if we are not operating at very high speeds or with high loads) can track the path that a geometric planner produces well.

Compared to part 1, I am now trying to actually find an optimal path for the robot.
That is, I want to find the time-optimal path that makes all the dots.

Since every dot can be made from various poses, we have multiple groups of poses which need to be visited exactly once.
This is called the "Traveling Salesman Problem in Neighbourhoods".

In this setting, we use the infinity norm as distance metric between poses, that is the distance between two poses is the maximum absolute difference between all its elements.
This represents the time it takes to get from pose 1 to pose 2 fairly well, since a typical controller would steer each joint of the robot arm seprarately, i.e. the time it takes to get from pose 1 to pose 2 is the maximum time one of the joints takes.

Prior research for this problem are e.g. 
\[[1](https://cse.cs.ovgu.de/cse/traveling-salesman-problem-with-neighborhoods-tspn)\],
\[[2](https://www.tandfonline.com/doi/abs/10.1080/10556788.2011.648932)\],
\[[3](https://www.ac.tuwien.ac.at/files/pub/hu-08.pdf)\],
or the two following here, that are concerned with problems where the path planning is a bottleneck as well 
\[[4](http://timroughgarden.org/papers/ijrr.pdf)\]
\[[5](http://old.sztaki.hu/~akovacs/publications/ijpr2016.pdf)\].

The problem we are tackling here is the 'easy' version, since we do not have any obstacles in the environment which may make our path planning harder.
As such, the goal we have is really finding an optimal sequence of poses, i.e. finding the sequence, and finding the right pose.

#### Solving the TSP for a single pose

I first implement a 'proper' TSP algorithm for the single-pose case.
Even though we likely have little enough poses to being able to find the exact solution, I am not going down that path.

We are implementing two approximation algorithms:

- Greedy with longer lookahead
- Simulated annealing

In both cases, I run the resulting path through an algorithm that tries to improve the result that we got.
Here, I do that by locally reversing subtours and checking if that leads to a better result.

#### Solving the TSP for a neighbourhood
Finding a solution to the TSP with neighbourhoods can be done in various ways.
However, as for the standard TSP, we are not getting the optimal solution here, but rather an approximation, since solving it is computationally not tractable.

We are going to look at a baseline of simply being greedy and simulated annealing for the neighbourhoods.
I originally also planned to implement a greedy version with lookahead, but already did the experiments for a single pose, and noticed that the simulated annealing approach was much better, or said differently: The lookahead sometimes made the solution worse.

**Simulated annealing for TSP with neighbourhoods**
...

#### Comparison & Results

To compare the planners we produced above, we need a few testcases.
We largely reuse things we have used before: a grid, a set of random points, a spiral, and part of our labs logo.

<div style="width: 85%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/grid.png" style="width:20%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:20%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:20%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:20%; padding: 5px">
</div>


The methods we have are summarized in the table below, along with the pathlength of the method for each test.
I marked the best result for both single-pose, and neighbourhoods italic, and the best overall in bold.

| | Method | Grid | Random | Spiral | Logo |
|----|-------|--------|---------|
|Single pose| Greedy | 5.83 | 2.392 | 3.72 | 0.85 |
|| Greedy with lookahead l=2 | 5.794 | 2.465 | 3.78 | 0.845 |
| | Simulated annealing | *5.681* | *2.389* | *3.589* | *0.838* |
|Neighbourhood | Greedy | **4.915** | **1.474** | 4.347 | 0.841 |
| | Simulated annealing | ... | ... | .. | .. |

<br>
And here is how the ordering of the methods for our labs logo.

<div style="width: 85%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/grid.png" style="width:20%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:20%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:20%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:20%; padding: 5px">
</div>

Finally, here is a side-by-side comparison of the greedy with sets and the TSP with a set of poses.
<div style="width: 85%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/grid.png" style="width:20%; padding: 5px">
    <img src="{{ site.url }}/assets/stippling/logo.png" style="width:20%; padding: 5px">
</div>

#### Takeway
I once more want to point out that the order of the dots does not necessarily seem to make sense as the 'best' path.
However, this might very well correspond to the shortest/best path in joint space of the robot.

It came as a surprise to me that the methods with a longer lookahead do not necessarily outperform the simple methods.
This has two reasons: We always perform a polishing step after we found the initial path, and some of the solutions that we obtain with a shorter lookahead might turn out better.
The other reason is that the greedy methods are suboptimal, and it might simply be the case that a method with a longer lookahead is locally better, but turns out worse overall.

Further, it is fairly clear that 'global' methods such as simulated annealing outperform the greedy methods.

#### Outlook/Leftover problems
- We ignored dynamics in this post. If we are truly looking for a time optimal path, this has to be taken into account.
- Additionally, we have neglected the actual path length, respectively the time it takes to traverse a path to the next pose. From experience, the use of the infinity-norm as proxy for this is reasonalble, but should be properly tested.
- Lastly, it is not completely obvious how this not translates back to multiple robots, since in addition to an ordering problem, we also need to answer the question how to assign points.
