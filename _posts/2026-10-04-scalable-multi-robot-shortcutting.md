---
layout: post
title: "Scaling shortcutting to many robots"
date: 2026-10-04 12:00:00 +0200
permalink: /scalable-multi-robot-shortcutting/
categories: path-planning
# published: false
---

<!-- Follow-up to /multi-robot-shortcutting/. -->


<p class="preface">
This is a follow up to the previous post on multi-robot multi-goal shortcutting.
We have the same problem again, but I want to focus a bit more on scalability to a high(er) number of robots here.
Previously, we went to four robots only, and so we didnt really explore any scaling behavior (except for some scaling with the number of tasks).

I'll revisit a couple of the approaches from the previous post, and we'll make up some new ones since (spoiler) the old thing does unfortunately not scale too well.
</p>

In a [previous post](/multi-robot-shortcutting/) we looked at making the shortcutters in my [multi-robot mult-goal problem](/mrmg-planning) better.
Better here means 'faster', and 'resulting in a lower cost in the end'.
Overall, the goal is obviously making the planners better, but the shortcutters are part of it, so we are focussing on this here.
As the number of robots and tasks grow in our multi-robot multi-goal problem, some of the approaches that previously worked very well break down due to combinatorial complexity that was not an issue at lower robot numbers.

So while accounting for all combinations of robots, or computing statistics over many different combinatons is very good for problems involving few robots, in practice the combinatorial nature of this makes it not scale to many robots (with many == any number > 4).
While in reality, you will very often not have more than four robots in the same workspace, and so many of the previous approaches are fine, I want to look at slightly more scaleable approaches.
What we want is a simple approach that scales to amny robots, and is as close as possible to the previous approaches on the simple problems.

We are using [the same repo as before](https://github.com/vhartman/multi-robot-shortcutting) for the experiments.

# The problem with many robots

Before we begin, we briefly look at the problem we get with more than a handful robots, and its root cause on a problem where we simply add more robots.
So bewlo, we have a problem where we have disk robots that move in 2D space, and need to reach a sequence of goals in a globally predetermined order{% include sidenote.html text='This is basically a continuous version of MAPF, if that helps.'%}.

After some postprocessing, a solution for this problem looks like this, on the right, compared to the original plan on the left:

[gif]

And the convergence curves that plot solution cost against computation time can be seen just below.

[disk robot scaling, full conf shortcutting, tree + gain, tree + group gain, random subset + compat run for 4, 8, 12 robots]

Hard to miss, we see the very flat line of the group gain here, which just abruptly stops after the intial improvement, once we come to a high number of robots.
This initial improvement is from the 'tree' part, which tkes single robot segments, and shortcuts them.
The stop then happens just after the tree is finished, and the group-gain part begins.

We remember from part 1, that 'group gain' computes gain proposals over many combinations of robots and modes.
The stop then happens because the gain proposal suddenly takes too long due to looking at _all_ proposals to evaluate which one is best.
This then means that we actually never get to attempt another shortcut.

This behaviour is not restricted to the disk setting -- we can observe similar behavior in a fixed manipulator setting:

[gif]

with the scaling curves looking quite similar:

[same shortcutters as above, for coupled stacking]

The other issue we can observe here again is that the improvement in the beginning is very slow when using this cost, compared to the full configuration shortcutting.
This is the case since we shortcut only single robots at a time, but the cost takes all the robots ino account.
This then means that we might have to first improve all robots' paths to a certain quality before we can actually see the cost improvement when using this cost function:

$$
C(\pi) = \sum_i \left(\max_r ||q_{i+1}^r - q_i^r||_2 + 0.01 \sum_r ||q_{i+1}^r - q_i^r||_2\right)
$$

This cost function is a decent approximation for the makespan of the solution, i.e., the time at which the latest robot will finish.

Plotting each robots' path lenght, we can see that some robots' path lenght decrease relatively quickly, while others do improve more slowly.
Thus the overall cost does not decrease as fast as we would want it to.

[plot with the knee for disk - comparison for 12 disks, full config left, subset right]
[if knee plot not available, choose any of the other high robot number scenarios (either disk or coupled stacking)]

While I believe that this single robot shortcutting is a good overall investment, and makes the path much nicer already early on, it is not good anytime behavior.

# A scalable shortcutting policy

We now know the issue with the previous policy, and we can start making stuff up that does not have this issue.
As said before: our goal is to get something that generally works, improves the cost as quickly as possible in the beginning, and is as simple as possible{% include sidenote.html text='I generally hold the opinion that algorithms are only going to be used if they are simple enough to implement, and do not have many moving pieces or copmlex ideas. RRT is such an example: Basically all motion planners worth looking at are some variation of RRT.'%}.

So from the discussion above (and some experiments that I am not showing here) I know that the problem is really the 'gain' part.
We did however like this in part 1 -- it worked very well in many cases -- so it is kind of sad that this is the issue apparently, and we need to get rid of it.

But the obvious approach from this takeaway is then that one way to tackle the scaling issue is just replacing the gain part, which does not scale, with something that scales better.
One of the things that scales better is just sampling a robot subset and a run that is compatible with the robot subset (i.e., where there is no mode change from any of the robots), and shortcutting by randomly sampling an index pair from this run.

Because we want to run these shortcutters in the loop of the planner, the other thing that I do not like is this fixed order of 'first doing one approach, then doing another one'.
This is soemwhat problematic in the online version of the planners, since the shortcutters throw away their state when a new plan arrives, and thus the first part of the shortutting is repeated very often, while the second part receives too little time.

The obvious way to deal with this issue is interleaving the two approaches, instead of sequencing them.
So we will test two things: (1) sequentially running first tree, and then subset group, and (2) interleaving tree and group.

In additon to that we weill also have a look at only group as an additional baseline.

# Experimental setup

We run scaling experiments on 4 scenarios, two of which we have seen before in the introduction:

- **Disk**: We have multiple 2D robots that need to reach a prescribed sequence of poses
- **Isolated box stacking**: We have a box stacking scenario with one robot on a table, $$N$$ times. So the robots are not interacting with each other at all.
- **Coupled box stacking**: We have the box stacking scenario again, but with $$N$$ robots on one table. This means that the robots are clearly interacting with each other, and could collide.
- **Mobile wall**: The $$N$$ mobile robots build a wall with a certain number of bricks, which we also vary. The robots are in the same environment, thus also interacting, and requiring a high level of collision avoidance.

The scenarios are shown below as videos:

[gifs]

We compare some of the old methods (tree + gain, tree + group gain, robot subset + compatible run), and the 'new' methods we described above (tree + robot subset + compatible run (interleaved and sequenced)).
As a baseline we also add full configuration shortcutting.

As in the previous post, to make everything compareable, we start with the same initial path for all the methods, and report the median for 3 different initial paths and 3 different shortcutting seeds.
This hopes to avoid a shortcutter just being a particularly good fit for a certain initial path.

And finally, while it is useful if the shortcutter is good for a pure offline setting, we test the planners offline and online, as we typically do not only run the shortcutter for post-processing, but as part of a loop, where we reinsert the new paths into the planner, and continue planning using the (hopefully) better plan.
In the online setting, the shortcutters get considerably less time than in the offline setting, as we have to balance the planning and the shortcutting{% include sidenote.html text='I.e., we have the typical exploration vs exploitation problem.'%}.

#### Scaling with the number of robots

The first thing we care about here now is how performance changes when increasing the number of robots that are involved in the problem that we are attempting to solve.

So below, we have the plots for our four scaling scenarios introduced before for the offline setting.

[image]

Her we do see again how the method that is very good for a lowr number of robots does not as well aymore for a higher number of robots.
In the thing below, you can see where time is actually spent.

[detail table of where time is spent for the higher number]

And this is how it looks online only for the higher number of robots.

[image]

[log image]

#### General performance

In addition to the scaling, we also said that we wanted the new approach to play nice with the whole set of problems.
So here we test int on the sam ebroad scenario as before, and in addition to before, I am also running this on the pure path length cost to see how the algorithms behave there.

[image]

[log image]

# Conclusion

#### What seems to matter

We can see that the cost function that we use has a large influence on how much influence single vs multi-robot at a time shortcutting has. 
This is intuitive, but annoying.
So generally, it is clear that the tree has a big influence on the end result, and overall seems to help, even though it makes the intitial progress seemingly slower.

So an important ingredient is appraently the shortcutting of groups: this both shortcuts (and thus improves the paths of) multiple robots at once, and second saves some time in collision checking, compared to shortcutting the same group one-by-one.

Repeatign from the previous post: mode-compatible shortcuts seem to matter a lot.

And the new thigs: random groups help avoid the combintorial complexity at little cost.

#### Future work

All of these approaches are relatively similar to general preexisting shortuct ideas. 
During the course of the writing of these two posts I did also try more exotic things, but none really worked, respectively the classical things were always simpler and worked still better.
So I do feel like there is a general opportunity to have a strong look at the shortcutting literature in general and try to do something fundamentally different to improve.

For example, a big issue with the shortcutting is that it relies on the straight line interpolation -- this only really works for geometric path planning (with exceptions) without constraints.
It is also only improving paths where the straight-line contraction is actually eading to better paths.
If I e.g. want to maximize clearance, this straight-line shortcutting is not going to be very helpful.

Then, again more focused on what we did here: As next steps, we should look at how the shortcutting is actually used and implemented in the planners online.
We have seen here that this seems to be the limiting factor now -- the time the shortcutters get is too low, and in addition, in the current implementation we are throwing away the state that the shortcutters accumulate.

As a result, the differences between the online runs of the shortcutters is negligible, even though the offline differences are large.