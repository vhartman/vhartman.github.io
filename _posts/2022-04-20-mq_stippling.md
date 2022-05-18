---
layout: post
title:  "Robotic stippling: Expanding to two robots"
subtitle: "or: Abusing lab equipment v2"
date:   2022-04-17 12:00:00 +0200
permalink: /robo-stippling-p2/
categories: art 
---

<p class="preface">
    This is part 2 of the robotic stippling experiment.
    Now, I am tackling doing the thing I did before with two robot arms.
    Ideally, they do not collide.
</p>

See [part 1](/robo-stippling/) for a general overview on what I am trying to do here.

Remember that the table with the robots on has _two_ robot arms there.
I want to use them both this time.

#### Problem setting

For now, I am tackling the problem under the assumption that we are given a set of points that we want to make with each robot.
This could e.g. be the case if I want to draw something with two colors (as is the case in our lab's logo).
In a more practical setting, this is also the case when working with multiple robots that have different end-effectors, say one robot is spot welding, while another is drilling something.

Having the dots/tasks allocated means that we again (as last time) only need to find a pose, for each task, the sequence, in which the tasks should be done, and the paths in between.
The difference now is that the pose and the path needs to take the other arm into account.
This should likely already be taken into account in the sequence planning.

We are trying to minimize the time it takes until all tasks are done/dots are made.
This means that for two robots, we are simply trying to minimize the largest finishing time.

Mathematically, the problem can be formalized as multi-agent neighbourhood traveling salesman problem, with the additional constraint that some cities can not be visited at the same time.

The [multi agent traveling salesman problem](https://neos-guide.org/content/multiple-traveling-salesman-problem-mtsp) can be solved with a MILP solver.
Adding the constraints of not being able to be at some poses at the same time is straightforward.
Bringing the neighbourhood-possibility into play makes the whole thing harder for the formulation, but could still be formulated as opt. problem, and thrown into a solver.

Note that all of this assumes that we can find paths if the start and the destination are feasible poses., which is a reasonable assumption to make.
However, in the multi agent problem, the path length would now actually be dependent on the path that the other robot takes.

#### Interlude

It makes sense to now take a brief step back, and think about what we want our algorithm to behave like in some special cases:

- What should happen if the dots are positioned such that the robots do not interact at all? <br>
  Ideally, the solution that we get should be the same as if we would solve the TSP for each robot separately. It would also be nice if there would be no (or very little) computational overhead resulting from dealing with two robot arms instead of two single robot arms separately.
- What should happen if one of the robots does not have any dots?<br>
  The solution should again be the same as if we only consodered one arm alone. The second robot should not add any complexity.

In general, the algorithm we use for two (or multiple) robot arms should [...] gracefully to simpler cases that we treated before.

Continuing this thought-experiment:

- What should happen if we have muliple dots for one agent, but only one for the second one? <br>
  This is a harder question, and we have to distinguish two cases: If all the configurations for the first agent are in conflict with the second one, this simply becomes a problem of first making the dots for one arm, and then for the second arm. For the resulting total time, the order does not matter. If there are configurations in which it is possible to make two dots at the same time [...]

#### Baseline

Doing everything sequentially.
This one serves mostly as setting up a bit of infrastructure, and changing the code from part 1 to deal with two robots.

The approach we are taking here is the same as in part 1: sample configurations, and connect them greedily.
But after we planned everything for the first robot, we repeat the whole procedure for the second one.

The things we need to change here are:
- representation of the path/sequence that takes both arms into account

All of the above results in the following order and animation, and a time of [...]:

[Image] [Animation]

#### Attempt Nr. 1: Being Greedy

For now, I am simply concerned with producing a sequence and paths that are feasible, and are (hopefully) better than the trivial approach of simply doing all the tasks sequentially, and not parallelizing anything.

We start with the assumption that the dots are synchronized for now.
This means that we do not care as much about path length.

The approach we take is the following:

1. Sample _sets_ of poses that fulfill the constraints for each point.
2. Annotate which poses collide.
3. Greedily choose the pose that minimizes the distance to the previous pose of the respective arm from all the poses that are collision free.
4. If there is no valid pose, 'wait', i.e., go into a pose that does not collide with any other pose of the other arm.

This approach results in the code below:

[code]

And this animation:

[animation]

#### Attempt Nr. 2: Simulated annealing?

#### Todos

- ...
- ...
