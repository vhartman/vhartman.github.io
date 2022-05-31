---
layout: post
title:  "Robotic stippling: Expanding to two robots"
subtitle: "or: Abusing lab equipment v2"
date:   2022-05-28 12:00:00 +0200
permalink: /robo-stippling-p2/
categories: art 
---

<p class="preface">
    This is part 2 of the robotic stippling experiment.
    We are trying to make a bunch of dots on a piece of paper using robot arms.
    In this post, I am trying to get an initial version running that uses multiple (=two) robot arms to make dots instead of only a single one.
    Ideally, they do not collide.
</p>

See [part 1](/robo-stippling/) for a general overview on what I am trying to do here:
Briefly summarizing, I am taking a list of dots as input, and want to have a piece of paper with the dots on them as output.
You might think that a printer would be the right approach here, and you would be right.
But that would be boring.
Instead, I am using robots that I gave pens to make dots.

In part 1, I built a proof of concept with a single robot arm.
But what if I want dots in multiple different colors?

It is now a convenient time to remember that the table with the robots in our lab has _two_ robot arms there.
I want to use them both this time.

#### Problem setting

For now, I am tackling the problem under the assumption that we are given a set of points for each robot.
This could e.g. be the case if I want to draw something with two colors (as is the case in our lab's logo).
In a more practical setting, this is also the case when working with multiple robots that have different end-effectors, e.g., one robot is spot welding, while another is drilling something{% include sidenote.html text='The other case (having a single set), and having to assign the dots to the robots is interesting as well, and is called Task Assignment. This is part of what I do in my more academically minded work.'%}.

Having the dots/tasks allocated means that we again (as last time) only need to find a pose for each dot, the sequence in which the tasks should be done, and the paths in between - but this time for two robots.
The difference now is that the pose and the path needs to take the other arm into account.
This likely already needs to be taken into account in the sequence planning, as some assignments of dots at the same time to the two robots might really not be possible.

We are trying to minimize the time it takes until all dots are made.
This means that for two robots, we are simply trying to minimize the largest finishing time.

Mathematically, the problem can be formalized as multi-agent neighbourhood traveling salesman problem, with the additional constraint that some cities can not be visited at the same time{% include sidenote.html text='The [multi agent traveling salesman problem](https://neos-guide.org/content/multiple-traveling-salesman-problem-mtsp) can be solved with a MILP solver.
Adding the constraints of not being able to be at some poses at the same time is straightforward.
Bringing the neighbourhood-possibility into play makes the whole thing harder for the formulation, but could still be formulated as opt. problem, and thrown into a solver.'%}.

All of this assumes that we can find paths if the start and the destination are feasible poses, which is a reasonable assumption to make in this setting, as there is (still) no clutter, and we have control over the movement of both robot arms.
In this setting, the path length is now dependent on the path that the other robot takes (as we might need to take evasive action).

For now, I am simply concerned with producing a sequence and paths that are feasible, and are (hopefully) better than the trivial approach of simply doing all the tasks sequentially, and not parallelizing anything.

To simplify the problem, I make the assumption that the dotting of the two robots is completely synchronized for now.
This means that I do not care as much about path length at the moment, but only about maximizing the number of dots that are made at the same time.
While this is clearly not the best approach, it lets us get the problem to know a bit better.

<!---- #### Interlude

It makes sense to now take a brief step back, and think about what we want our algorithm to behave like in some special cases:

- What should happen if the dots are positioned such that the robots do not interact at all? <br>
  Ideally, the solution that we get should be the same as if we would solve the TSP for each robot separately. It would also be nice if there would be no (or very little) computational overhead resulting from dealing with two robot arms instead of two single robot arms separately.
- What should happen if one of the robots does not have any dots?<br>
  The solution should again be the same as if we only consodered one arm alone. The second robot should not add any complexity.

In general, the algorithm we use for two (or multiple) robot arms should degrade gracefully to simpler cases that we treated before.

Continuing this thought-experiment:

- What should happen if we have muliple dots for one agent, but only one for the second one? <br>
  This is a harder question, and we have to distinguish two cases: If all the configurations for the first agent are in conflict with the second one, this simply becomes a problem of first making the dots for one arm, and then for the second arm. For the resulting total time, the order does not matter. If there are configurations in which it is possible to make two dots at the same time [...]
----->

#### Baseline

For a simple baseline, our two robots are doing everything sequentially, i.e. the first robot is making its dots, and once it is done, the second robot makes its round.

This means that we can reuse lots of things from part 1.
This baseline algorithm serves mostly as setting up a bit of infrastructure, and changing the code from part 1 to deal with two robots.

The approach we are taking is the same as in part 1: first compute a robot configuration for each dot, and then connect them greedily.
After we planned everything for the first robot, we repeat the whole procedure for the second one.

All of the above results in the following order and animation, and 25 steps to complete the task of drawing all the dots:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/multi_circles_sequentially.gif" style="width:100%; padding: 10px">
</div>

It is fairly clear that this set of dots could have been brought onto the paper more efficiently by making some of them in parallel.

#### Attempt Nr. 1: Being Greedy

A simple algorithm (while still being better than the baseline above) could be the following:

1. Sample poses that fulfill the constraints for each point.
2. Find the pose for robot one that minimizes the distance to its previous pose.
3. Find a pose for robot two that is valid when taking the other arm into account and minimizes the distance to its previous pose.
4. If there is no valid pose, 'wait', i.e., go into a pose that does not collide with any other pose of the other arm.

This approach gives us this animation, and takes 21 timesteps:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/multi_circles_no_set.gif" style="width:100%; padding: 10px">
</div>

We can obviously do better for two reasons:
- We could sample sets of configurations (sometimes, the poses are just barely in collision)
- With the greedy approach above, we are not actually maximizing the number of dots that are drawn simulataneously. It could happen that one configuration of robot 2 is only feasible for one single configuration of robot 1. But it might happen (since we minimize distance) that we pick another configuration that might be feasible for many other configurations.

#### Attempt Nr. 2: Beeing greedy with sets
We tackle the first point first: Sample multiple poses for the robot that make dots in the same configuration.

Now, in practice, it might be more desirable to compute the positions of the two robot arms jointly.
This would have the clear benefit that the configurations are computed with the other robot in mind.
However, in that case, we would have a quadratically increasing number of combinations that we would have to attempt to generate poses for.

So, as a first attempt, we try to simply sample multiple poses for each robot, and hope for the best.
How do we actually sample multiple poses? By randomly perturbing the initial pose that we start our optimizer from.

As example, when generating n=50 poses for one dot, these are the poses we get:
<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/poses_v2.gif" style="width:100%; padding: 10px">
</div>

While that looks ok(ish), it does not seem like this set of solutions covers the space of possible solutions well{% include sidenote.html text='This is also an ongoing theme in my research - How can we produce _diverse_ poses that fulfuill a set of desired constraints?'%}.
But for now, I am fine with what we get from simply randomly initializing the starting pose of the robot, and we'll continue working with that simple approach.
We might revisit this later.

We also need to change the greedy algorithm from above to take multiple poses into account.
These two changes give us this animation:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/multi_circles_random_sets.gif" style="width:100%; padding: 10px">
</div>

This looks much more satisfying, and takes 18 timesteps, three more than the minimum.
But the second point from above still stands - we are still not really attempting to actively maximize the number of simultaneously made dots.
Further, the 'in and out' movement of the second robot is a bit weird.

#### Attempt Nr. 3: Maximum matching in a bipartite graph 
So, after getting to know the problem a little better with two (or three if you count the baseline) fairly naive solutions, we are taking this to a more complex level.

Since we 'discretized' the problem and currently assume synchronous dot-making, I currently want to maximize the dots that are made simultaneously.

We can see each index as a node in a (bipartite) graph, with each node containing multiple poses.
Now, we can connect all indices that have any position that is collision free with a pose in another node.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/graph.png" style="width:100%; padding: 10px">
</div>

Here, on the left side, I connected all the separate poses with all other feasible poses.
On the right side, the same graph is shown, but the edges are now simply indicating that the two dots could be made at the same time (and the specific pose does not matter anymore).

Now, the problem of 'finding a sequence of dots that draws as many dots as possible simultaneously' can be seen as 'finding a [maximum matching](https://en.wikipedia.org/wiki/Matching_(graph_theory))'.

Once we have a maximum matching{% include sidenote.html text='For example by formulating it as [maximum flow problem through a network](https://www.geeksforgeeks.org/maximum-bipartite-matching/), or with the [augmented path algorithm](https://github.com/flxf/maximum-bipartite-matching), which I used here.'%}, we know which indices should go together{% include sidenote.html text='Additionally, once we know which indices work with others, we also have a lower bound for the number of timesteps we need here: The number of indices that do not have any edges plus the number of the ones that do.<br> In the exmple above, we now know that the minimum number of timesteps we need would be 4. In case we would have a 4th dot for robot 1 that we can not connect to a dot of robot 2, the minimum time would be 5.'%}.
The indices that are not part of the matching are the dots that can not be drawn simultaneously with another dot.
This means that we can now construct a graph again, and figure out a way to order them.
We could do that in a greedy manner (as before) or actually run a (better) TSP algorithm on it.

For now, we do this again in a greedy manner, which results in this animation:
<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/multi_circles_bipartite.gif" style="width:100%; padding: 10px">
</div>

The problem with this approach is the following: If we have two sets of dots that are completely independent, only using one maximum matching results in putting poses together that might be suboptimal.

That is, this approach still minimizes the number of timesteps, but absolutely not the distance that the robots are moving.
In practice, we'd likely want to do a mix of both things - we need to maximize the things we can do at the same time, but we also need to minimize the distance that needs to be covered by the robots.

#### More demos
I ran the bipartite graph matching approach on a couple other sets of dots (concentric circles, random points, and our labs logo), giving these results:
<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/multi_bipartite_concentric.gif" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/stippling/multi_bipartite_random.gif" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/stippling/multi_bipartite_lis_2.gif" style="width:97%; padding: 10px">
</div>

#### Going out into the real world

We can reuse everything we had in part 1 for the execution of the paths on the real robots.
I did not get much time to test this, as our robots are currently in use for data-collection for actual research.

<iframe style="display:block; margin: 0 auto;" width="600px" height="340" src="https://www.youtube.com/embed/7oVc4VULhyg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
<br>

And the resulting images here, with a bunch of attempts on the right.
<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/stippling/multi_focus.jpg" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/stippling/multi_all.jpg" style="width:46%; padding: 10px">
</div>

My key takeaway is that the pen needs to be stiffer/more accurate to the model. 
The more diverse set of orientations from which we now make dots makes any misalignment of the pen with the axis on which it should be very obvious.
The best solution might be to fix the pen to the robot in a different way, and get a pen that has compliance in its axis direction.

However, that is a hardware issue, and while that is definitely something that can be taken into account in planning the path (try to stay at similar orientations, restrict the freedom of the dot-making-pose in general) it is not something that invalidates the approach for planning that I took here.

As such, I am fairly happy with the results that I got.

#### Things to do/Outlook
- At the moment the 'go out of the way' position is the home position of the robot.
This is unneccessarily far away from all the other configurations, and takes too much time.
- Is there a better way to get diverse samples that fulfill the goal of making a dot? I really hope there is - this question should read as 'Someone should really have a look at it'.
- So far, we assumed that all the actions of the robots are synchronized.
If we relax that, we can try to interleave the dots of the two robots by simply going to an intermediate position between dots that is not in collision with the dot-making-configuration of the other robot.
- Can we extend the approaches we attempted here to more than two robots?
- Can we make up some industrial scenarios where something like this would be useful?
- How much better is properly solving the 'ordering' problem vs, simply running a greedy algorithm on it?
