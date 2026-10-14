---
layout: post
title: "Scaling shortcutting to many robots"
date: 2026-10-13 12:00:00 +0200
permalink: /scalable-multi-robot-shortcutting/
categories: path-planning
# published: false
---

<!-- Follow-up to /multi-robot-shortcutting/. -->


<p class="preface">
This is a follow-up to the previous post on multi-robot multi-goal shortcutting.
We have the same problem again, but I want to focus a bit more on scalability to a high(er) number of robots here.
Previously, we went to four robots only, and so we didn't really explore any scaling behavior (except for some scaling with the number of tasks).

I'll revisit a couple of the approaches from the previous post, and we'll make up some new ones since (spoiler) the old thing unfortunately does not scale too well.
</p>

In a [previous post](/multi-robot-shortcutting/), we looked at making the shortcutters in my [multi-robot multi-goal problem](/mrmg-planning) better.
Better here means 'faster', and 'resulting in a lower cost in the end'.
Overall, the goal is obviously making the complete planners better -- the shortcutters are a small isolated part of the planner, so we are focusing on this here.
They are also generally usable outside of the planners, so they make for a nice benchmark that we can isolate and optimize.

As the number of robots and tasks grows in our multi-robot multi-goal problem, some of the approaches that previously worked very well break down due to combinatorial complexity that was not an issue at lower robot numbers.

So while accounting for all combinations of robots or computing statistics over many different combinations is very good for problems involving few robots, in practice the combinatorial nature of this makes it not scale to many robots (with many == any number > 4).
While in reality, you will very often not have more than four robots in the same workspace, and so many of the previous approaches are fine, I want to look at slightly more scalable approaches.
What we want is a simple approach that scales to many robots and is as close as possible to the previous approaches on the simple problems.

We are using [the same repo as before](https://github.com/vhartman/multi-robot-shortcutting) for the experiments.

# The problem with many robots

Before we begin, we briefly look at the problem we get with more than a handful of robots, and its root cause on a problem where we simply add more robots.
So below, we have a problem where we have disk robots that move in 2D space, and need to reach a sequence of goals in a globally predetermined order{% include sidenote.html text='This is basically a continuous version of MAPD, if that helps.'%}.

After some postprocessing, a solution for this problem looks like this, on the right, compared to the original plan on the left:

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/disk-r12-before-after.gif" alt="Twelve-disk path before and after shortcutting" style="width:100%;">

And the convergence curves that plot solution cost against computation time can be seen just below.

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/intro-disk-scaling.png" alt="Offline shortcutting convergence for four, eight, and twelve disk robots" style="width:100%;">

Hard to miss, we see the very flat line of tree + group gain here, which just abruptly stops after the initial improvement, once we come to a high number of robots.
This initial improvement is from the 'tree' part, which takes single-robot segments and shortcuts them.
The improvement then stops just after the 'tree'-part is finished, and the group-gain part begins.

We remember from part 1 that 'group gain' computes gain proposals over many combinations of robots and modes.
The stop then happens because the gain proposal suddenly takes too long due to looking at _all_ proposals (which scales combinatorially with the number of robots and robot-modes) to evaluate which one is best.
This then means that we actually never get to attempt another shortcut.

This behavior is not restricted to the disk setting -- we can observe similar behavior in a fixed manipulator setting.

<video autoplay loop muted playsinline controls style="width:100%;">
  <source src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/coupled-box-stacking-r6.mp4" type="video/mp4">
</video>

The scaling curves look quite similar -- it is not as bad here, but we already see tree + group gain slowing down somewhat.
It is not as extreme as in the 12-disk-robot setting above, but the number of shortcut attempts is much lower than for fewer robots due to the overhead of computing the proposals.

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/intro-coupled-scaling.png" alt="Offline shortcutting convergence for coupled box stacking with four and six robots" style="display:block; width:70%; margin:0 auto;">


Below, you can see where time is actually spent in the tree + group gain setting.

<details class="results-details">
<summary>Tree + group gain runtime breakdown</summary>
<table class="diagnostics-table">
<thead>
<tr>
<th scope="col">Environment</th>
<th scope="col">Robots</th>
<th scope="col">Wall time</th>
<th scope="col">Collision checking</th>
<th scope="col">Everything else</th>
<th scope="col">Gain arms</th>
<th scope="col">Proposals</th>
</tr>
</thead>
<tbody>
<tr><th scope="row">2D disks</th><td>12</td><td>63.40 s</td><td>1.45 s (2.3%)</td><td>61.95 s (97.7%)</td><td>102,399</td><td>1</td></tr>
<tr><th scope="row">Coupled box stacking</th><td>6</td><td>30.00 s</td><td>10.91 s (36.4%)</td><td>19.09 s (63.6%)</td><td>575</td><td>4,056</td></tr>
</tbody>
</table>
<p class="results-legend">Medians over nine runs. The requested budgets were 15 seconds for the disk scenario and 30 seconds for coupled box stacking.</p>
</details>

#### Slow starts

The other issue we can observe in the plots above again is that the improvement in the beginning is very slow, compared to the full configuration shortcutting when using the makespan-cost.
This is the case since we shortcut only single robots at a time, but the cost takes all the robots into account.
This then means that we might have to first improve all robots' paths to a certain quality before we can actually see the cost improvement when using this cost function{% include sidenote.html text='This cost function is a decent approximation for the makespan of the solution, i.e., the time at which the latest robot will finish.'%}:

$$
C(\pi) = \sum_i \left(\max_r ||q_{i+1}^r - q_i^r||_2 + 0.01 \sum_r ||q_{i+1}^r - q_i^r||_2\right)
$$

Plotting each robot's path length, we can see that some robots' path lengths decrease relatively quickly, while others do improve more slowly.
Thus the overall cost does not decrease as fast as we would want it to.
Below, we have an example for the 12 robots in a 2D environment, and we compare the full configuration shortcutting (on the left) with the tree + gain approach (on the right).

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/cost-knee-high-robot-count.png" alt="Complete cost and individual robot path lengths for high-robot-count scaling scenarios" style="width:100%;">

While I believe that this single-robot shortcutting is a good overall investment and makes the path much nicer already early on, it is not good anytime behavior for the complete cost{% include sidenote.html text='Stated slightly differently: It improves the behavior of single robots, but does not improve the makespan significantly.'%}.

# A scalable shortcutting policy

We now know the issue(s) with the previous policy, and we can start to try approaches that do ideally not have these issues.
As said before: our goal is to get something that generally works (i.e., does not only outperform the approaches from before on the high-robot-count problems), improves the cost as quickly as possible in the beginning, and is as simple as possible{% include sidenote.html text='I generally hold the opinion that algorithms are only going to be used if they are simple enough to implement, and do not have many moving pieces or complex ideas. RRT is such an example: Basically all motion planners worth looking at are some variation of RRT.'%}.

So from the discussion above (and some experiments that I am not showing here) I know that the problem is really the 'gain' part.
We did however like this in part 1 -- it worked very well in many cases -- so it is kind of sad that this is the issue apparently, and we need to get rid of it.

But the obvious first thing to try from this takeaway is then that one way to tackle the scaling issue is just replacing the gain part, which does not scale, with something that scales better.
One of the things that scales better (as can be observed above) is compatible subset (called 'random robot subset + compatible run' in the previous post): sampling a random robot subset and a run that is compatible with the robot subset (i.e., where there is no mode change from any of the robots), and shortcutting by randomly sampling an index pair from this run.

Because we want to run these shortcutters in the loop of the planner, the other thing that I do not like is this fixed order of 'first doing one approach, then doing another one'.
This is somewhat problematic in the online version of the current planners, since the shortcutters throw away their state when a new plan arrives{% include sidenote.html text='It is not trivial to carry over the computed statistics or figure out what we have already done if the path changes.'%}, and thus the first part of the shortcutting is repeated very often, while the second part receives too little time.

The obvious way to deal with this issue is interleaving the two approaches, instead of sequencing them.
So we will test two things in the experiments: (1) tree + compatible (sequenced), which first runs 'tree' and then compatible subset, and (2) tree + compatible (interleaved), which alternates calls to tree and compatible subset until the tree does not have any suggestions left.

# Experimental setup

We run scaling experiments on 4 scenarios, two of which we have seen before in the introduction:

- **Disk**: We have multiple 2D robots that need to reach a prescribed sequence of poses, and at the end return to their home positions.
- **Isolated box stacking**: We have a box stacking scenario with 4 boxes per table and with one robot per table, $$N$$ times -- the robots are not interacting with each other at all in this setting.
- **Coupled box stacking**: We have the box stacking scenario again, but with $$N$$ robots on one table. This means that the robots are clearly interacting with each other, and could collide.
- **Mobile wall**: Between 1 and 7 mobile robots build a fixed 5×5 wall of 25 bricks; we vary only the number of robots, not the wall size or number of bricks. The robots are in the same environment, thus also interacting, and requiring a high level of collision avoidance.

The scenarios are shown below as videos:

<details>
<summary>2D disks</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/disk-r12-before-after.gif" alt="Twelve-disk path before and after shortcutting" style="width:100%;">
</details>

<details>
<summary>Isolated box stacking</summary>
<video autoplay loop muted playsinline controls preload="auto" poster="{{ site.url }}/assets/scalable-multi-robot-shortcutting/isolated-box-stacking-r9-poster.jpg" style="width:100%;">
  <source src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/isolated-box-stacking-r9.mp4" type="video/mp4">
</video>
</details>

<details>
<summary>Coupled box stacking</summary>
<video autoplay loop muted playsinline controls style="width:100%;">
  <source src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/coupled-box-stacking-r6.mp4" type="video/mp4">
</video>
</details>

<details>
<summary>Mobile wall</summary>
<video autoplay loop muted playsinline controls style="width:100%;">
  <source src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/mobile-wall-r7.mp4" type="video/mp4">
</video>
</details>

We compare some of the old methods: (1) tree + gain, (2) tree + group gain, (3) compatible subset, and the 'new' methods we described above: (4) tree + compatible (interleaved) and (5) tree + compatible (sequenced).
As a baseline we also add (6) full configuration shortcutting.

As in the previous post, to make everything reasonably comparable, we start with the same initial path for all the methods. For the offline scaling and path-length-cost experiments, we use 3 different initial paths and 2 shortcutting seeds per path{% include sidenote.html text='Three method/scenario combinations have five successful runs instead of six; we aggregate the available runs.'%}, taking the median over the available seeds for each path and then the median across paths.
The broad scenario comparison uses 3 initial paths and 3 shortcutting seeds per path, while the online comparison uses 1 initial path and 2 shortcutting seeds.
We do this in the hope of avoiding a shortcutter just being a particularly good fit for a certain initial path.

And finally, while it is useful if the shortcutter is good for a pure offline setting, we test the planners offline and online, as we typically do not only run the shortcutter for post-processing, but as part of a loop, where we reinsert the new paths into the planner, and continue planning using the (hopefully) better plan.
In the online setting, the shortcutters get considerably less time than in the offline setting, as we have to balance the planning and the shortcutting{% include sidenote.html text='I.e., we have the typical exploration vs exploitation problem.'%}.

#### Scaling with the number of robots

The first thing we care about here now is how performance changes when increasing the number of robots that are involved in the problem that we are attempting to solve.

So below, we have the summary of a lot of experiments for our four scaling scenarios introduced before for the offline setting.
The plots show the median normalized cost at the end of shortcutting for a given time over all the experiments.

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-scaling-summary.png" alt="Final normalized offline shortcutting cost as the number of robots increases" style="width:100%;">

The approaches all perform similarly enough for up to 4 robots.
Depending on the scenario, we start seeing differences from 6 robots on, where compatible subset and the two tree + compatible variants perform significantly better than the other planners.

The tree + compatible (interleaved) and tree + compatible (sequenced) methods perform almost the same except for the mobile-wall setting for the highest number of robots, where we see that the interleaved approach works slightly better.
When looking at the full convergence plot however, I do feel like the approaches would converge to the same final cost.

The full convergence plots are below:

<details>
<summary>2D disks</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-disk-scaling-curves.png" alt="Offline cost curves for the disk scaling scenarios" style="width:100%;">
</details>

<details>
<summary>Isolated box stacking</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-isolated-box-stacking-curves.png" alt="Offline cost curves for the isolated box-stacking scaling scenarios" style="width:100%;">
</details>

<details>
<summary>Coupled box stacking</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-coupled-box-stacking-curves.png" alt="Offline cost curves for the coupled box-stacking scaling scenarios" style="width:100%;">
</details>

<details>
<summary>Mobile wall</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-mobile-wall-scaling-curves.png" alt="Offline cost curves for the mobile-wall scaling scenarios" style="width:100%;">
</details>

In these plots, we can also see that in some of the scenarios, tree + compatible (interleaved) also has slightly better anytime behavior (i.e., it decreases ever so slightly more quickly in the beginning) than tree + compatible (sequenced).

Finally, unfortunately the full configuration shortcutting remains significantly better for initial convergence.
For pure performance reasons, I think a case can be made for first running some full configuration shortcutting, and then switching to another method -- but this is again problematic for online performance, so I am not doing this here for now.

#### General performance

In addition to the scaling, we also said that we wanted the new approach to play nice with the whole set of problems.
So here we test it on the same broad scenario set as before.

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-broad-highlights.png" alt="Offline shortcutting comparison for Random 2D, box rearrangement, spiral tower, and car assembly" style="display:block; width:70%; margin:0 auto;">

There is not much to say here: The planners perform very similarly to the good planners from the previous post.
The biggest difference can be seen on car assembly, where our new methods from this post converge slightly slower than the gain methods.

<details>
<summary>Full broad comparison — all 27 environments</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-broad-comparison.png" alt="Offline shortcutting comparison across all 27 broad scenarios" style="width:100%;">
<details>
<summary>Logarithmic time axis</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-broad-comparison-logx.png" alt="Offline shortcutting comparison across the broad scenario set with a logarithmic time axis" style="width:100%;">
</details>
</details>

#### Online planning

We have seen in the previous post that there is usually not much performance difference to be seen for the online versions of the shortcutters.
Here, we run them on scenarios involving moderate and higher numbers of robots.

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/online-largest.png" alt="Online shortcutting convergence for moderate and largest settings in each scaling family" style="width:100%;">

And again, we can see that there is no huge difference for most scenarios.
On the other hand, we can see that the planners seem to perform much worse when running planning + shortcutting compared to only running shortcutting on the initial plan offline.

This points to an issue that the planner + shortcutting integration has that becomes only this visible at high robot numbers, not really to an issue the shortcutters have{% include sidenote.html text='To be analyzed in detail in a future post.'%}.

#### Performance for the path length cost

As a last experiment, we look at the performance of the shortcutters when using the sum of all single-robot path lengths instead of the makespan cost to ensure that we did not overfit our methods to the specific setting we had there.

<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-sum-cost-largest.png" alt="Offline shortcutting convergence with the sum-of-path-lengths cost for the largest setting in each scaling family" style="display:block; width:70%; margin:0 auto;">

And we can see that the performance and the ordering of the methods are close to unchanged, even though the curves look slightly different.
The new methods decrease the cost more quickly than before in the sum-cost setting.
However, the full configuration shortcutting is also significantly faster than before, and as such, the gold standard for initial speedup is still the full configuration shortcutting.

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/scalable-multi-robot-shortcutting/offline-sum-cost-largest-logx.png" alt="Offline shortcutting convergence with the sum-of-path-lengths cost and a logarithmic time axis" style="width:100%;">
</details>

# Conclusion

#### What seems to matter

An important (the most important?) ingredient is apparently the shortcutting of groups: this both shortcuts (and thus improves the paths of) multiple robots at once and saves some time in collision checking, compared to shortcutting the same group one by one.

Additionally, while the cost function that we use has a large influence on how much influence shortcutting one robot vs multiple robots at a time has, it does not change the ordering, and full configuration shortcutting is in all cases the fastest improving approach in the beginning.
Thinking about this for long enough, this is understandable, but annoying.

Generally, it can also be seen that the tree has a big influence on the end result even though we only shortcut single robots at a time, and thus make the initial progress slower.
However, it seems to help, and improve over compatible subset alone (likely because it gives a slight bias to shortcut longer single-robot segments).

The part of the algorithm that we added here which seems to help a lot is the random sampling of groups in combination with the single-robot tree, which helps avoid the combinatorial complexity of the other more complex approaches at little cost.

I also briefly want to restate previous results that were reinforced once again: mode-compatible shortcuts seem to matter a lot, and if I had to choose one thing to do, it is this.

#### Future work

All of these approaches are relatively similar to general preexisting shortcut ideas.
During the course of writing these two posts, I did also try more exotic things, but none really worked; the classical things were always simpler and still worked better{% include sidenote.html text='And simpler is already better in itself anyways.'%}.
So I do feel like there is a general opportunity to have a strong look at the shortcutting literature in general and try to do something fundamentally different to improve{% include sidenote.html text='Which is what I am trying to encourage with this benchmark!'%}.

For example, a big issue with the shortcutting is that it relies on straight-line interpolation -- this only really works for geometric path planning (with exceptions) without constraints.
It is also only improving paths where the straight-line contraction is actually leading to better paths.
If I, e.g., want to maximize clearance, this straight-line shortcutting is not going to be very helpful.

Then, more focused on what we did here: As next steps, we should look at how the shortcutting is actually used and implemented in the planners online.
We have seen here that this seems to be the limiting factor now -- the time the shortcutters get is too low, and in addition, in the current implementation we are throwing away the state that the shortcutters accumulate.

As a result, the differences between the online runs of the shortcutters are negligible, even though the offline differences are large.
Even more extreme, the pure offline shortcutters find better paths than combining the shortcutting + planning, which should _never_ be the case.

Finally, with the visualizations of the paths here, we can see that the paths are clearly still far from optimal.
In the 12-disk setting, it is clear that they essentially act one-by-one -- and this also seemingly happens for the robots.
They do not really use the fact that they can already move a lot even when it is not 'their turn', i.e., when another robot has the immediately next goal to reach first.
This is also something that I need to look into, and see if the cost is to blame here, or if it is simply not yet optimal.
