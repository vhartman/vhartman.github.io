---
layout: post
title:  "Shortcutting multi-robot multi-goal plans"
# subtitle: "or: How to best compute sums of euclidean distances."
date:   2026-09-10 12:00:00 +0200
permalink: /multi-robot-shortcutting/
categories: path-planning
---

<p class="preface">
In multi-robot path planning, it is often relatively easy to find a bad path, since we can just move robots out of the way if we control all of them.
It is usually much harder to find good paths. So what we do is find a bad path, and then postprocess it into a good path.
This is standard practice in path planning, and is called (partial) shortcutting.
It is unclear how to best apply this to multi-robot multi-goal path planning, as we want to shortcut over the fully constrained parts.
</p>

This is more or less a writeup of the work I did recently for the [multi-robot multi-goal multi-modal path planning](/mrmg-planning), respectively the [multi-robot assembly planning](/wrap) work.
I decided that it might be interesting to have a standalone post that focusses on the shortcutting part, and explain it a bit in more detail, and sets up a bit of a benchmark, where people could build upon{% include sidenote.html text='And I ended up doing better analysis than before, and tested a few small new ideas.'%}.
This would benefit me since the paths that I would be getting in several applications would be better faster.

In the following, I am not going to explain the background of shortcutting, and how it works, this can be seen e.g., [here](/partial-shortcutting).

# Shortcutting for multi-robot multi-goal paths
 
As mentioned above, I am interested in multi-robot multi-goal multi-modal path planning, and as part of it in post-processing of those paths.
The path planning side of it boils down to finding a feasible path in a high-dimensional space.
This space has a special structure: it is a tensor product of all the separate single robot configuration spaces, i.e.

$$
\mathcal{Q} = \mathcal{Q}_1 \times \mathcal{Q}_2 \times ... \times \mathcal{Q}_N
$$

This can and should be used to plan more effectively, but we are for now not really doing that, since if we ignore it, we can easily get optimality guarantees by using existing planners.

In the following, we are then going to treat the shortcutting problem as a setting where we shortcut a given initial path with equality constraints (i.e. the end points of each mode).
This means that we still need to keep satisfying these equality constraints, i.e., our path is required to go through certain parts of the cofiguration space. 

Below, we see these constraints illustrated{% include sidenote.html text='Taken from [the paper](/mrmg-planning).'%}:

<img src="{{ site.url }}/assets/multi-robot-shortcutting/constraint-illustration.png" style="display:block; width:70%; margin:0 auto;">

Here, the modes of the robots are shown with the grey boxes, and if a box ends, we require a robot (one of the disks here) to be in a very specific position (e.g., in order to pick something up, or for example to do a point-weld).
The red dashed lines show the points at which we have a mode switch of any robot (and thus the overall mode changes).

The key realization is that only parts of the tensor product that makes up the composite configuration space is constrained:

$$
\mathcal{Q}_\text{constrained} \subseteq \mathcal{Q}_1 \times q_2 \times ... \times \mathcal{Q}_N.
$$

With this insight, we can see that we can still freely shortcut large parts of our full composite space, just not the constrained robot coordinates.
This means that we can do:

- As a baseline, shortcutting in the full configurations space. This means that we can never shortcut over mode-boundaries/the equality constraints (again, since we have a hard equality constraint _where_ we need to be with the mode switching robot).
- As next step up, we can choose single robots at random, and shortcut its dimensions. In here, we also need to make sure that the indices we choose to linarly interpolate between are in the same mode.{% include sidenote.html text='This is what we originally did in the [multi-robot multi-goal multi-modal path planning](/mrmg-planning) work. This has since been replaced though, with something we will see below.'%} But that already means that we can shortcut longer paths compared to considering all robots at the same time.
- Instead of single robots, we can also choose groups of robots to shortcut. The rest is the same, but we now need to make sure that all robot modes do not change.

In the approaches above, the simple implementations of shortcutting are 'choosing a two random indices of the path, and hoping that the mode is the same'. Instead, we can also sample the mode that we shortcut directly, and then choose the indices only on that part of the path. 

I am going to give details on the experiments that we do below in the experiments section, but for now, here's some plots, showing how each approach does on a variety of problems, for shortcutting only (i.e., not feeding the paths back into the planner again).
These plots for selected scenarios{% include sidenote.html text='More scenarios [TODO](here).'%} show time on the x-axis, and the cost of the path on the y-axis:

<img src="{{ site.url }}/assets/multi-robot-shortcutting/baseline-four-environments.png" style="width:100%;">

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-shortcutting/baseline-four-environments-logx.png" alt="Baseline offline shortcutting comparison with a logarithmic time axis" style="width:100%;">
</details>

The main thing to take away here is that it is clearly very useful to just sample the mode to shortcut directly.
Compared to what we did in the WAFR paper, this surprised me a bit, as I was assuming that the rejections of invalid index-pairs (i.e. crossing mode boundaries) was more or less free{% include sidenote.html text='Honestly, seeing these plots here, it is almost embarassing to have used the naive version in the paper originally.'%}. 
But this is explainable: If we just sample endpoints randomly, we have a relatively low probability of actually sampling both points in a constant mode part, and this probability decreases with the number of robots, and with the number of different tasks that we do{% include sidenote.html text='So effectively, we just have very bad chances of finding a shortcut that we can even attempt.
And because of how I implemented things in the planner, there is a budget of attempts that can be made - thus if we waste them with too many invalid attempts, we end up with a worse method.'%}.

<details class="results-details">
<summary>Shortcut lengths and acceptance rates</summary>
<table class="diagnostics-table">
<thead>
<tr>
<th scope="col">Environment</th>
<th scope="col">Sampling</th>
<th scope="col">Accepted span<br><small>median / 90th percentile</small></th>
<th scope="col">Compatible proposals</th>
<th scope="col">Accepted proposals</th>
</tr>
</thead>
<tbody>
<tr><th scope="row">Box rearrangement</th><td>full configuration</td><td>2.0% / 3.3%</td><td>2.6%</td><td>0.01%</td></tr>
<tr><th scope="row"></th><td>robot + endpoints</td><td>8.6% / 20.4%</td><td>15.6%</td><td>1.23%</td></tr>
<tr><th scope="row"></th><td>robot + compatible run</td><td>6.6% / 19.7%</td><td>55.3%</td><td>1.26%</td></tr>
<tr><th scope="row">Car assembly</th><td>full configuration</td><td>1.9% / 2.9%</td><td>1.9%</td><td>0.02%</td></tr>
<tr><th scope="row"></th><td>robot + endpoints</td><td>12.1% / 29.1%</td><td>38.3%</td><td>7.23%</td></tr>
<tr><th scope="row"></th><td>robot + compatible run</td><td>3.9% / 16.5%</td><td>54.5%</td><td>2.66%</td></tr>
</tbody>
</table>
<p class="results-legend">Medians over three 30-second runs. Shortcut spans are percentages of the initial path; proposal percentages are relative to all sampled proposals.</p>
</details>

To me the other surprising thing here is how good full configuration shortcutting is, and especially how quickly it leads to improvements, especially given how little of the attempts are actually feasible due to crossing modes.

One last thing to point out is that even though full configuration shortcutting is decreasing very fast, it also does not converge to the same best cost as the others, since we will always keep the waypoints that coincide with the mode-switches.

However! As said above already, these plots show pure 'offline' shortcutting.
In the context of the multi-robot planners, this is not the most realistic setting, as we insert the shortcuts back into the tree/roadmap, and continue working with the new plans.
This changes the plots:

<img src="{{ site.url }}/assets/multi-robot-shortcutting/baseline-four-environments-online.png" style="width:100%;">

Here, I added the planner without shortcutting as baseline comparison.
In the experiments, we make sure that all seeds and rng-sources are the same for all runs, i.e., the only thing changing is the seed given to the shortcutters.

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-shortcutting/baseline-four-environments-online-logx.png" alt="Baseline online shortcutting comparison with a logarithmic time axis" style="width:100%;">
</details>


And this shows that the difference is not actually that big!
We see that the algorithm that is best in the offline setting is also best in the online setting, but it is all much closer than before.
Now, this is partially due to a relatively small shortcutting budget, and partially due to the fact that the reinsertion of the plans into the planner dampens some of the bigger differences from the pure offline setting.

We could optimize our shortcutting approach for either of these settings, but I do believe that in the end we want one algorithm for both postprocessing, and 'online' use.

# Prior work
There is not much work on multi-robot multi-goal plan-postprocessing, so I am just going over a couple of things that I used for ideas and inspiration.

- Partial shortcutting: I wrote about this [in the post here](/partial-shortcutting) a bit. The core idea is that instead of just sampling indices on the path, and linearly interpolating them, we sample indices on the path and (a subset of) dimensions which we linearly interpolate. The other dimensions are kept as they were before (i.e., the path is not replaced for those dimensions). This carries over very naturally to the multi-robot case, as we can just sample a subset of robots, or a single robot and only shortcut that one. This is what we arleady do. 
- There was [some work presented at WAFR this year on shortcutting](https://algorithmic-robotics.org/papers/WAFR_2026_Final_66.pdf): It was slightly more on the theoretical side, but also suggested some approach that we'll see below is surprisongly similar to something I converged to below. The core idea is that we fix the length of the shortcut we do, and move this window over our path, and then repeat this with a smaller window. After, we fall back to shortcutting with indices coming from a halton sequence. The paper is cool, and worth looking at just for the plots alone already. They do unfortunately not look at partial shortcutting at all, which is what I usually do.
- At IROS '25, there was [a paper on multi-robot shortcutting](https://philip-huang.com/mr-shortcut/) from Huang et al. They propose three approaches, and suggest that a round-robin style application of those, repsectively estimating online which method has the highest probability of giving you a better path, works best.

I implemented a couple of those algorithms, and compared them against our baseline.
Since none of the approaches are presented such that they apply to the multi-robot multi-goal setting, we make some adjustments{% include sidenote.html text='In the plots above we can already see that there is effectively no point on running the shortcutters over the full path at once -- the planners that explicitly take into account where we can actually shortcut are always better than their sibling versions that don\'t.'%}:

- The WAFR shortcutter shortcuts full configuration modes directly, and is the same otherwise. 
- The meta algorithms from Huang, round-robin and thompson sampling do:
  - Sample full configurations and compatible modes, and within the modes, we sample endpoints uniformly.
  - Sample single robots, and compatible modes, and within the modes, we sample endpoints uniformly.

Compared to the original version from Huang, we do not do the prioritized shortcut in the following experiments, as this would imply re-checking the whole following trajectory.
We did test this, and the shortcuts were rarely accepted due to collisions of the following path.

We compare these against our baselines on the selected scenarios, both offline:

<img src="{{ site.url }}/assets/multi-robot-shortcutting/all-methods-offline.png" alt="Offline shortcutting comparison across four environments" style="width:100%;">

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-shortcutting/all-methods-offline-logx.png" alt="Offline shortcutting comparison with a logarithmic time axis" style="width:100%;">
</details>

and online:

<img src="{{ site.url }}/assets/multi-robot-shortcutting/all-methods-online.png" alt="Online planning and shortcutting comparison across four environments, including a planner-only control" style="width:100%;">

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-shortcutting/all-methods-online-logx.png" alt="Online planning and shortcutting comparison with a logarithmic time axis" style="width:100%;">
</details>

We see again that the full configuration shortcutting from the WAFR paper has the same issues as the simpler full configuration shortcutting.
The only other thing we can see here is gaain that in the online setting, the differnces are not very big between the different algorithms.
In the offline setting, the round-robin style approaches tend to perform best, but the full configuration shortcutting still hast the fastest initial decrease of the cost.

# Improving upon the baseline
We have seen that the version that randomly chooses a mode for a robot is doing best out of the non-meta-algortithms we have briefly described above.
Now, we can try to improve upon the things we are already doing.

We can not improve what we can not measure.
So we start by measuring and generating some statistics from the random-robot subset + compatible run{% include sidenote.html text='These numbers are obiously going to be different for all methods, but we are just going to assume that this is good enough information for now.'%}:

- How much time do we spend checking invalid edges, and how much time do we spent verifying edges that are actually collision free
- Which of the shortuts that we do actually ends up in the final path.
- How much do the shortcuts improve the path: could it be that we get the main improvement from only a few initially very suboptimal segments.

<!-- The table below reports medians over three 30-second runs of the random-robot + compatible-run shortcutter. "Surviving" means that at least one interior robot/path-index slot written by an accepted shortcut is still present in the final path. The valid/invalid split only measures time spent checking candidate edges. -->

<div class="diagnostics-table-wrap" role="region" aria-label="Shortcut diagnostics" tabindex="0">
<table class="diagnostics-table">
<thead>
<tr>
<th scope="col">Environment</th>
<th scope="col"><span>Candidates</span><small>checked / accepted</small></th>
<th scope="col"><span>Check time</span><small>valid / invalid</small></th>
<th scope="col"><span>Partially retained<br>shortcuts</span></th>
<th scope="col"><span>Improvement from<br>top 10 shortcuts</span></th>
</tr>
</thead>
<tbody>
<tr><th scope="row">Random 2D</th><td>13,637 / 2,742</td><td>85.3% / 14.7%</td><td>5.4%</td><td>34.7%</td></tr>
<tr><th scope="row">Box stacking</th><td>6,068 / 1,826</td><td>86.0% / 14.0%</td><td>9.5%</td><td>43.6%</td></tr>
<tr><th scope="row">Car assembly</th><td>3,495 / 1,151</td><td>82.9% / 17.1%</td><td>14.5%</td><td>61.3%</td></tr>
</tbody>
</table>
</div>

From this data, we see that 

- Not that many shortcuts end up in the final path: We spend a lot of time 'overwriting' previously checked edges.
- We spend much more time verifying valid edges, than rejecting invalid proposals. Rejecting invalid proposals is fast! I want to emphasize this again: Taking this and the previous point together means that we spend a lot of time validating shortcuts that do not do anything in the end!
- the best couple shortcuts are responsible for a big part of the path improvement.

So effectively, what we should try to do is 
- find the 'final' optimal long shortcuts directly, to avoid shortcutting the same indices many times{% include sidenote.html text='That being said, I realized at some point that shortcutting single robots at a time also leads to collision checking indices multiple times, as we always check the whole scene, even if we only change a single robot. I have some experiments lying around that does smarter collision checking if we only do partial shortcuts, but I am going to omit this for this post.'%}. However, this is very close to just stating 'Well, we should just find the best path directly'.
- allocate our effort to the right modes, and not the ones that we did already shortcut to optimality before.

# Shortcutting as resource allocation

We can see shortcutting as resource allocation problem: we need to allocate the time we have for edge checking smartly in order to get as much improvement out of the time as possible.
If we just spend the time carelessly, we might not improve at all, or not as much as we could.

In the multimodal setting, this could happen due to various reasons:
- we might not be able to improve the mode that we are in for a robot much further, or
- we might actually improve the path, and spend a lot of time verifying that the edge is collision free, and then later replace this edge completely with a better shortcut.

Both are not what we want!
So with this in mind, we can try to design an algortihm that

- constructs shortcuts that are successful, and do not spend time being rejected
- does shortcuts that are long, since those are more likely to end up in the final path
- shortcuts in modes that still have potential to be improved.

But we also want to make sure that we do not try the same shortcut time and time again.
In the following, we will try to do two things:
- Trying to predict shortcuttable modes
- do long shortcuts

#### Trying to predict shortcuttable modes

The things we describe above mean that we basically try to predict shortcuts that maximally improve the cost, and have a high likelihood of actually being collison free.
If we write this up in the most general sense, this is very close to just predicting a path, which is not something we want to do{% include sidenote.html text='Stating it more plainly: This is just the motion planning problem itself.'%}.

So what we settle for is updating our belief online based on attempted shortcuts to try to decide which robot-mode pair might be good.

We do this by taking two signals into account:
- How often we previously successfully shortcutted this robot/mode combination, and
- an estimation of how much further we could reduce the cost, by assuming that we could fully straithen the path.

Using this, we compute a score 

$$
s_a = \frac{g_a\,\frac{1 + A_a}{2 + P_a} + g_\mathrm{floor}}{1 + U_a}.
$$

Here, an arm $$a$$ is a robot (or robot group) and a compatible mode interval, $$g_a$$ is the estimated remaining cost reduction, $$A_a$$ and $$P_a$$ count accepted and proposed shortcuts, and $$U_a$$ counts how often the arm was selected. The gain floor is a small fraction of the mean gain and prevents arms with no estimated gain from being ignored completely.

We rank all possible arms using this score and sample shortcut endpoints uniformly within the highest-ranked interval.

#### A principled approach to long shortcuts

The other thing we want to do is a sensible approach to long shortcuts: An idea that we can have here is similar to a binary search: 

- We attempt a full shortcut of a mode for a robot
  - If we are successful, we are done with this mode for this robot
  - If not, we split the mode where the first shortcut was found, and add these two possible shortcuts to a queue of shortcuts that we attempt.

We do this for a certain number of splits, and then do a fallback strategy in this approach.
A fallback could e.g., be the method described above, or could also be just random sampling of endpoints within a mode.

The important thing to note here for the two methods is that they are stateful.
This will have some implications when running this in the planner, where we restart shortcutting repeatedly.

# Experiments

In the following, we will always show normalized cost improvement, and show a (more or less) representative sample of 4 environments.
The rest of the plots will be available as well though.

We are going to do two types of experiments, which we have already shown above: 
- we will be running shortcutting on a dataset of paths that we generate 'offline', and measure how much we improve the initial cost of the path.
- We are also going to be running the shortcutters as part of the planning loop, in order to see how they change the planning performance.

The setup for both these things is vailable in the repository [here](TODO).
We heavily build upon the github repository from the [multi-robot planning work](mrmg-planning), and generate initial paths for multiple environments from there.

#### Offline shortcutting
For offlien shortcutting, we run a planner, and take the initial path that it produces, and feed this path to all shortcutting algorithms.

<img src="{{ site.url }}/assets/multi-robot-shortcutting/experiments-eight-methods-offline.png" alt="Offline comparison of the selected shortcutting methods" style="width:100%;">

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-shortcutting/experiments-eight-methods-offline-logx.png" alt="Offline comparison of the selected shortcutting methods with a logarithmic time axis" style="width:100%;">
</details>

In the plots above we see that there is no large difference between the methods anymore. 
Only doing 'gain' seems to be somewhat bad, but the rest is largely similar.
Tree + group gain, and our own round robin version seems to be more or less the best though.

#### Online shortcutting
For online shortcutting, we simply run the planner in its optimizing mode, which calls the shortcutter whenever a new plan that improves upon the previous cost is found.

The new shortcutted path is then fad back into the plannner again, to refine the tree.

<img src="{{ site.url }}/assets/multi-robot-shortcutting/experiments-eight-methods-online.png" alt="Online comparison of the selected shortcutting methods" style="width:100%;">

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-shortcutting/experiments-eight-methods-online-logx.png" alt="Online comparison of the selected shortcutting methods with a logarithmic time axis" style="width:100%;">
</details>

**How much time should the shortcutters get in the planner?**
In all the oneline plots above, we used the default version of how many shortcutting invocations we do.
However, in many settings, this results in only ~5% of the time spent shortcutting.
To a certain extent, this explains why the online results were relatively similar for all shortcutters: They simply ould not actually spend enough time to show where they were better, if the difference was not already quite big.

I was wondering if we should allocate more time then.

<img src="{{ site.url }}/assets/multi-robot-shortcutting/check-budget-ablation.png" alt="Online shortcut collision-check budget ablation" style="width:100%;">

<details>
<summary>Plots with a logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-shortcutting/check-budget-ablation-logx.png" alt="Online shortcut collision-check budget ablation with a logarithmic time axis" style="width:100%;">
</details>

# Take away?

- When running the shortuctters as part of the planning loop, it does not matter too much what you do as long as you sample the modes directly.
- When running the planners offline as pure post processing roudn robin seems to be a decent idea.

If you found this work helpful, please cite ...

