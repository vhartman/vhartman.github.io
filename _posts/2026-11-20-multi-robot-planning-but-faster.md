---
layout: post
title: "Speeding up sampling based multi-robot multi-goal planning"
date: 2026-11-23 12:00:00 +0200
permalink: /faster-multi-robot-planning/
categories: path-planning
# published: false
---

<p class="preface">
My benchmark on multi-robot multi-goal motion planning contains a couple of planners.
The main one I use usually is BiRRT*, and I improved that one quite a bit since the original publication of the benchmark.<br><br>

That means the original numbers in the paper are outdated by now.
This post is a writeup of the improvements made since the original benchmark-publication, and a bit of an update of the baselines for people that want to cite numbers, but do not (want to) run the benchmark.

There's also a couple new problems that people presented in other places that I am also comparing against here, and adding to the benchmark.
</p>

This post is mainly motivated by [cuArms](https://cuarms.github.io/), which cited some of the numbers published in the [paper introducing the multi-robot multi-goal path planning problem](/mrmg-planning).
I was a bit surprised by how much faster their planner is, but mainly I was a bit surprised by the numbers they cited since my planners felt faster in my day-to-day usage of them.

The benchmark is mostly written in Python{% include sidenote.html text='Except for the backends doing forward kinematics, and collision checking, which leverage whatever library you are willing to integrate.'%} because it was much easier to get started and experiment in Python.
By now I do regret that decision to base this whole thing in Python, since we lose out on some free performance-gains.
Luckily, the main optimizations that we can do are still algorithmic/implementation choices (for example how we sample configurations for many robots at a time), and we are not yet at the limits of Python: The majority of the time is currently still spent in collision checking, and as long as this is the case, Python overhead is not really holding us back.{% include sidenote.html text='Foreshadowing.'%}

But coming back to the comparison that cuArms made: It turns out my surprise makes sense, since running the current planner code on the same scenarios is quite a bit faster.
More specifically: I made a bunch of improvements (mainly while working on [WRAP](/wrap.html)) that the cited numbers from the paper did not reflect (since they are fairly old by now).

So in this post here I am doing three things: (1) writing up the things I did since the original paper that led to the main improvements, and (2) showing off some backends that were also integrated, and (3) comparing against some of their experiments.{% include sidenote.html text='For these things I had some help by various LLMs to integrate some backends, for visualizations, and for implementation help. All the text you are reading is 100% artisanal hand written though.'%}

# The multi-robot multi-goal planning benchmark
In my benchmark, I care about two things: time to initial solution, and how fast the cost converges to something sensible. 
In order to track what improvements we make, we are going to look at a subset of the environments from the benchmark.{% include sidenote.html text='Because running the whole benchmark for multiple seeds until convergence would take much too long.'%}
We will try to cover the different task horizons, the different difficulties in environments, and the different number of robots the scenarios contain.
For the initial solution times, we will look at a larger subset, since that is much faster to run.

For convergence, we will only look at:

- A two dimensional hallway-problem, where the robots need to swap positions, and go back to their start position.
- A two dimensional problem containing three robots that need to navigate to multiple goals each.
- A problem with four UR10e robots, that need to stack 8 boxes by picking them up and stacking them on the previously placed ones.
- A problem with four UR10e robots that assemble some struts to a structure made of two cubes.

These scenarios are shown in the gallery below:

<link rel="stylesheet" href="{{ '/assets/multi-robot-planning-but-faster/scenario-gallery.css' | relative_url }}">
<script src="{{ '/assets/multi-robot-planning-but-faster/scenario-gallery.js' | relative_url }}" defer></script>
{% include scenario-gallery.html clips=site.data.performance_scenarios.rai id="rai-scenario-video" label="RAI scenarios" %}

Because I am not at the same job anymore as I was when the paper was published, I will run this stuff on my laptop this time, compared to the previous experiments that were run on a desktop PC. 
Before we start, we'll look at the timings we get on this laptop, compared to the numbers we reported in the paper. 
{% include sidenote.html text='
For the paper, we ran 10 environments in parallel to cut down on the time needed.
I thought I had made sure that this does not noticeably slow the experiments down.
However, it seems like I was wrong, and there was indeed some slowdown compared to sequential runs.
So here, we run everything sequentially.'%}

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/paper-first-solutions.svg" alt="Initial solution times: published medians over 25 runs and submission-tag RAI laptop medians over 10 seeds. Speedups are below the plot. Overall is the geometric mean of medians across 15 environments; crosses flag out-of-bounds paths." style="display:block;width:100%;">
</figure>

In this comparison, we can already see a **~2.1x** difference to the numbers that we published in the paper.
I am mostly putting that on the fact that I ran things in parallel for the paper experiments, and things are running sequentially here.
{% include sidenote.html text='
I did a proper experiment here for what slowdown the parallel execution gives on my laptop, and the result is that 2 in parallel are fine (1.01x slower), 4 are already noticeable (at 1.57x slower), and 8 are definitely not comparable anymore (at 2.88x slower).
This of course depends on the CPU and the number of cores and various other things.
As stated before, even though 2 planners in parallel seems fine, I am going to stick with sequential runs here.'%}

# Speeding up bidirectional composite-space RRTs
Before we get to more interesting things, I made a variety of code improvements that aren't smart optimizations, but rather stopping to do dumb things:
- Originally we sampled 1000 random configurations before starting the planner to get an estimate for the volume of the free space in order to compute the rewiring radius. I got rid of that, and am estimating the free space online now.
- I added batched uniform sampling, with sequential collision checking. Generating random configurations one at a time is wasteful, and adds a lot of Python overhead.
- Whenever two trees meet in the bidirectional RRT, we merged them, and did a bunch of rewiring. I made that more efficient. If I remember correctly, this was the single biggest gain from these here.
- I changed the initial transition seeds of the BiRRT to use 10 seeds instead of 50. I think this was also a big gain.

Unfortunately I can not remember what each of the things brought, and I do not want to ablate just for this post, but the cumulative improvement is very visible in the initial solution plot:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/revision-first-solutions.svg" alt="Initial solution times for the published paper, submission-tag laptop runs and current-code baseline. Laptop medians use 10 seeds. Speedups compare the newest version to the paper and preceding version; Overall is the geometric mean across 15 environment medians. Crosses flag out-of-bounds paths." style="display:block;width:100%;">
</figure>

This gives another 1.7x improvement over the initial run on this laptop.
That means we are at a **3.8x** improvement over the numbers in the paper for the subset that we are testing here for the initial solution.

And the same thing in the convergence plots for the four chosen environments (note that these are log-log plots):

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/revision-convergence-log-log.svg" alt="Ten-seed convergence on four scenarios for the submission tag and current-code control. Logarithmic time and cost axes; historical reference costs remain separate." style="display:block;width:100%;">
</figure>

In the convergence plots, we can see that we do find the initial solution earlier, but (1) the improvements are not super impactful for 2D environments, and (2) cost-wise, it does not make a huge difference, since the convergence is still relatively slow.

#### Steering improvements

Thanks to the reviewers of the WAFR paper, we added a scaling study (and a bunch of other analyses) in the appendix of the paper:
This scaling study convinced me that the biggest reason for slow initial solution times were _very_ suboptimal plans.
More specifically, I thought (and it is very visible{% include sidenote.html text='Always visualize your plans!'%} in some cases when looking at the animation of the inital path!) that the robots were taking long detours from the optimal plan.
These detours imply longer paths which need to be collision checked, and thus longer path planning times to even get to the initial path.
The dumb solution to the problem of taking long to find an initial path is 'find a better initial path' or 'avoid the detours'.

The detours come from two sources: 

1. The steps that the RRT planner takes are long because of choices that I made originally: Our original default steering step-size limit was $$\eta = \sqrt{d}$$, where $$d$$ is the total dimension of the composite workspace, giving the step sizes just below.
   
   <figure style="max-width:400px;margin:0.75rem auto;">
   <img src="{{ site.url }}/assets/multi-robot-planning-but-faster/steering-dimension.svg" alt="The default steering step limit, square root of dimension, for dimensions 1–50" style="display:block;width:100%;">
   </figure>

   For determining the step length when extending our tree in RRT, we then used the largest per-robot joint-space displacement

   $$
   D(q,q') = \max_{r\in\mathcal R}\left\|q_r-q'_r\right\|_2.
   $$

    My motivation for this was that the robots should all be able to take large steps, since they all need to move somewhere! 
    But the problem then became exactly this: all robots took large steps at the same time.
2. The other source is the multi-goal part of the problem, and how we deal with them in the RRT planner:
The goals only apply to a subset of robots at a time, but the RRT needs to build a tree from a concrete root containing a full configuration (not only a subset).

   To get this full configuration, we fix the goal configuration for the robot(s) that the goal applies to, and we randomly sample the rest of the robots. These roots can then be very suboptimal, since it is quite unlikely that the random configuration is on the optimal path.

We are going to ignore the second source, and focus on the first issue: A natural way to avoid long detours is decreasing the step size of the BiRRT.{% include sidenote.html text='I say here that this is a natural way because in hindsight, it is. However, it took me years to realize this as well, as evident by the fact that we did not already do this in the paper.'%}
I looked at a few different metrics to use to determine the step size, and I looked at how to compute the step size in a sensible way as a function of the problem that we are trying to solve.
In the end, I ended up using a fixed step size of 3 for a per-robot L1 metric.

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/steering-first-solutions.svg" alt="Initial solution times adding L1 steering to the published paper, submission-tag laptop runs and current-code baseline. Speedups are below the plot; Overall is the geometric mean across the same 15 environment medians. Crosses flag out-of-bounds paths." style="display:block;width:100%;">
</figure>

Using the L1 metric for the step-size limit in the steering function we get a speedup of 1.2x over the previous numbers, adding up to a **4.7x** speedup overall for the initial solution times.

Similar to before, the impact is specifically in the higher dimensional robot environments, and slightly decreases performance on the 2D environments.
I think this can be explained mostly by the fact that most 2D environments have a total dimension below 10, giving a step-size increase in those environments, whereas most robot environments have a smaller maximum step size with this change.

Similar as before again in the convergence plots:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/steering-convergence-log-log.svg" alt="Ten-seed median convergence on four scenarios, with logarithmic time and cost axes: submission tag, current-code control and L1 steering. Published first solutions and 500–1000-second final costs are separate references; crosses mark out-of-bounds paths." style="display:block;width:100%;">
</figure>

Where we can see that as a side-effect to the faster solution, we also tend to get better initial solutions for the robot environments, supporting the hypothesis that the long (costly) detours were also costly in compute time.

#### General performance optimizations

After getting these first low hanging fruits, we need to figure out where time is spent at all to sensibly continue optimizing.
While we should do this for a couple of environments, since the environments behave differently for different numbers of robots, and different numbers of goals, we are going to do it for four: the 2D hallway, four-robot box stacking, six-robot isolated stacking, and spiral tower.

In our case more importantly, we want to see where time is spent at a certain time:
Our planner changes behaviour over time, so just reporting one single number per function is misleading.
The planner might spend lots of time collision checking in the beginning, but then get stuck in a completely different place later on.

So what we will do is plot a profile over time:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/profile-before-optimizations.svg" alt="Before the general optimizations: actual historical commit bd1160a with L1 steering, profiling hallway, box stacking, six-arm isolated stacking and spiral tower using RAI. One 60-second instrumented run per scene; dashed lines mark the first solution." style="display:block;width:100%;">
</figure>
Here, we see that as expected a large part of the time is spent doing collision checking, both in single query checks, and in complete edge checks - additionally, there is seemingly a large overhead in edge-checks that is not collision checking.
We do also see that a large part of the time is spent in informed sampling after an initial solution was found.

We also look at the average of the time spent on specific parts of the code before and after the solution was found.

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/profile-before-optimizations-phases.svg" alt="Historical code with L1 steering: exclusive wall-time breakdown before and after the first solution for the same four RAI scenes, one instrumented run each." style="display:block;width:100%;">
</figure>

The biggest difference in all environments between pre first solution and post first solution is that sampling takes much more time after the first solution was found.

**Optimizing informed sampling:**
There's two things that can be improved in informed sampling from how it was implemented at the time:
- We can sample batches, saving a bunch of setup and precomputations that were done many times when running the sampling sequentially, since many samples were infeasible.
- We can sample the mode and the configuration at once, instead of sampling a configuration and then later rejecting it if it can not improve the path in a specific mode.
- Instead of sampling the hyperellipsoid per robot, and then projecting on the bounds of the robots, and rejecting if the combination of all robot configurations can not improve the path, we can do direct sampling of the space that can improve a solution via hit and run sampling.

Of course, none of this improves the initial solution time, since informed sampling only happens after a solution was found.
We thus look only at the convergence curves:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/informed-convergence-log-log.svg" alt="Ten-seed median convergence on four scenarios: submission tag, current-code control, L1 steering and improved informed sampling. Logarithmic time and cost axes; crosses mark out-of-bounds paths." style="display:block;width:100%;">
</figure>

The improvement does not show super well in the plot here, but the converged cost is practically always better, and there is less time spent on informed sampling overall.

**Various optimizations**:
Similar to before the steering-change, there were also various optimizations that added up over time, but are not huge changes overall:

- When doing shortcutting, we feed the shortcut path back into the tree of the RRT. There's two things that can be avoided: (1) We do not need to collision check this path a second time when adding it to the tree, and (2) we can avoid adding nodes that already exist (i.e. in parts of the path that was already the direct connection, and therefore did not change).
- We added cached edge checks, which helped a bit.
- Some more minor things that all together add up, but are nothing super noteworthy.

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/all-convergence-log-log.svg" alt="Ten-seed median convergence on four scenarios, adding node reuse and cached edge checks to steering and informed sampling. Historical reference and current-code control remain visible. Logarithmic axes; crosses mark out-of-bounds paths." style="display:block;width:100%;">
</figure>

Overall, these things gave a ~5-10% improvement in final cost on longer runs, but the gain is mostly visible in the profiles below, where big parts of the time spent went away, and is spent on collision checking now.

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/profile-after-optimizations.svg" alt="After the general optimizations: commit efe2e6d with L1 steering, hit-and-run informed sampling, batching, sampler caching, node reuse and cached edge checks. The same four frozen RAI scenes and planner seed; one 60-second instrumented run per scene." style="display:block;width:100%;">
</figure>

<details>
<summary>Before and after the first solution</summary>

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/profile-after-optimizations-phases.svg" alt="Improved code: exclusive wall-time breakdown before and after the first solution for hallway, box stacking, isolated stacking and spiral tower, one instrumented run each." style="display:block;width:100%;">
</figure>

</details>

# Some more experiments

cuArms compared against some of the construction scenes from the benchmark: the spiral tower scene with two and four robots, the truss scene and the cube scene (shown in the gallery below).
Since no code is available at the time of this writing, and the paper talks of UR5 robots, while the benchmark uses UR10 robots, I am not sure how comparable the experiments will be.
That being said, despite this, I'll optimistically assume that they used the exact setting with the same collision check resolution and the same IK solutions.

Comparing the new updated runs of my planners with the reported curves from cuArms (extracted from the paper by your favourite LLM), we get those results:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/rai-mujoco-assembly-convergence-log-log.svg" alt="Current RAI convergence on the two spiral towers, Truss and Cube, using frozen archived goals and historical strut geometry. Median and interquartile range over five seeds, with published final-cost references and figure-extracted cuArms curves. Logarithmic time and cost axes." style="display:block;width:100%;">
</figure>

Here, we can see that the updated BiRRT* planner is more competitive with the cuArms planner in initial solution time than the cited numbers suggested.
When comparing convergence rate, the cuArms planner is clearly better.
There also seems to be a tendency, that the cuArms planner is relatively better on scenes with more robots.

I also added some of the experiments from cuArms and from [RoboBallet](https://arxiv.org/abs/2509.05397).
Unfortunately, at the time of writing, cuArms does not have code available, and so we have to build our environments by visual inspection.
We add:

- the welding experiments from RoboBallet.
- the packing and the unpacking from cuArms.

Videos of the scenarios, and of the strut-assembly scenarios from above are in the gallery below:

{% include scenario-gallery.html clips=site.data.performance_scenarios.additional id="additional-scenario-video" label="Additional experiments" %}

We compare the scenarios with MuJoCo, and with [RAI](https://marctoussaint.github.io/robotics-course/rai.html) as backends.
I am not putting the numbers from cuArms in here, since the scenarios are unlikely to be fair comparisons due to different assignments, and different IK solutions.

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/rai-mujoco-welding-packing-convergence-log-log.svg" alt="Current RAI and MuJoCo 4 convergence on sphereized four- and eight-arm welding, packing and unpacking. Five seeds per backend, with medians and interquartile ranges; unsolved runs retain infinite cost. Logarithmic time and cost axes." style="display:block;width:100%;">
</figure>

We can see that in the settings where Mujoco is the 'ground truth' for the scenarios, Mujoco is faster than RAI. 
I did not fully analyze this yet, but it seems like this has to do with how I am converting from Mujoco to RAI, and that there is a bunch of overhead in the collision checking due to that.

#### Integrating CoMotion: SIMD parallelism
Finally, with cuArms, and some other recent motion planning papers, the advantages of parallelizing become more and more obvious for planning, and collision checking many configurations in parallel offers huge advantages for speeding up the whole pipeline, as shown e.g. by cuArms, cuRobo, VAMP and MR-VAMP.

I currently don't have a GPU but luckily there is a good contender for getting parallelization and faster collision checking with CPUs as well: [CoMotion](https://github.com/parasollab/comotion) and [VAMP](https://github.com/kavrakilab/vamp).
So, I added CoMotion as backend for my benchmark.

For CoMotion, I had to add attachments (this exists in VAMP, on which CoMotion builds), enabling attaching boxes, and add cylinders in order to get feature parity with the RAI backend.
These additions were more or less completely vibe-coded, and I did not really check too much what's going on besides that the binary collision results that I get between RAI and CoMotion are exactly the same.
Further, while the backend has roughly feature parity with RAI, the implementation is much slower than the original CoMotion enviroments, where we easily get a >50x speedup over RAI, so there is still a way to go, and it might make sense to implement this properly.

I did not change much else in my planner except of making a bit better use of the parallel checking by (1) batching some collision checks in sampling, and (2) sending complete edges for checking in one call, avoiding a bunch of round-trips through the bindings.
This means that there must still be some room for smarter parallel planners.

This gives the following results for initial solution times:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/backend-first-solutions.svg" alt="Initial solution times for published references, original RAI rerun on the laptop, optimized RAI, CoMotion and MuJoCo 4. Rows below show optimized RAI versus original RAI, CoMotion versus optimized RAI, and CoMotion versus original RAI. Each speedup is reference time divided by new time; 2× means half the time. Overall uses geometric means across the same 13 scenes available for all five series, excluding cuArms. Historical and optimized runs differ in geometry, keyframes and planner settings, so ratios describe separate campaigns rather than a controlled ablation. Open triangles and greater-than-or-equal signs mark timeout lower bounds; crosses flag out-of-bounds paths." style="display:block;width:100%;">
</figure>

So, for initial solution times, using the SIMD collision checking of CoMotion is roughly 4x faster than the final RAI numbers we had, and roughly **12x** faster than the initial rerun of the code on this machine.
Compared to the original numbers, this is a **~26.7x** speedup.

And as usual, we also look at the curves for convergence.
First we look at the scenes that we used before as well to see how the SIMD backend behaves while improving the cost in the planner.

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/backend-convergence-log-log.svg" alt="Current RAI and CoMotion convergence on the four main scenarios, using frozen archived goals. Median and interquartile range over five seeds. Published final-cost references and the figure-extracted cuArms Cube curve are retained. Logarithmic time and cost axes." style="display:block;width:100%;">
</figure>

The speedup clearly carries over, and the curves from the faster collision checking backend are always under the curves of the RAI backend, meaning that the cost at any time during the solution is always better than the cost we get with using the RAI backend.

Finally, we compare BiRRT* with the CoMotion backend to the cuArms-planner on the scenes that cuArms used in their comparison.
However as said before, we have to be careful with interpreting these results for the reasons stated above.

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/backend-assembly-convergence-log-log.svg" alt="Current RAI and CoMotion convergence on the two spiral towers, Truss and Cube, using frozen archived goals and historical strut geometry. Median and interquartile range over five seeds, with published final-cost references and figure-extracted cuArms curves. Logarithmic time and cost axes." style="display:block;width:100%;">
</figure>

We see that the BiRRT* planner with the CoMotion backend is faster than their planner in all cases, but as before, this advantage shrinks the more robots there are.

Finally, we also look at the RoboBallet welding scenarios, and the packing/unpacking scenarios that I made up that are somewhat similar ot the ones in the cuArms paper:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/backend-welding-packing-convergence-log-log.svg" alt="Current RAI, CoMotion and MuJoCo 4 convergence on sphereized welding, packing and unpacking where supported. Five seeds per backend, with medians and interquartile ranges; unsolved runs retain infinite cost. Logarithmic time and cost axes." style="display:block;width:100%;">
</figure>

And to finish off, and close the loop on the foreshadowing from the beginning, we now look at the profiles from CoMotion:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/profile-comotion-after.svg" alt="After the planner optimizations with CoMotion: exclusive wall-time profiles for box stacking, eight-robot isolated stacking, spiral tower and eight-arm sphereized welding. One 60-second instrumented run per scene, planner seed 2, reusing the frozen backend-comparison scenes and settings. Native collision-query time includes FK and native edge interpolation. Dashed lines mark the first solution." style="display:block;width:100%;">
</figure>


In these profiles, we can now see that collision checking is not the dominant part anymore, and we need to figure out better sampling strategies, and consider porting the planners to C++ to avoid some Python overhead.
This is particularly visible in the split between before/after the initial solution:

<figure style="margin:1.5rem 0;">
<img src="{{ site.url }}/assets/multi-robot-planning-but-faster/profile-comotion-after-phases.svg" alt="CoMotion wall-time breakdown before and after the first solution for the same four instrumented runs. Collision queries include native state, batch and complete-edge checks; remaining categories exclude nested collision calls." style="display:block;width:100%;">
</figure>

# Conclusion
Unsurprisingly, the original code we wrote for the benchmarking of multi-robot multi-goal planning approaches was not the greatest of all time.{% include sidenote.html text='You can extrapolate what this says about the current implementation then.'%}
By improving a few things, we almost get a **5x** speedup over the numbers we have originally published with effectively the same planner, just a better implementation, and some better hyperparameter choices.

The **12x** speedup (over RAI, or a **26.7x** speedup over the published numbers) is then given by the switch of the collision backend, which leads to faster initial results compared to a purely GPU based planner that is highly parallelized on the comparisons that we can control.{% include sidenote.html text='There is still the caveat that there is some uncertainty on the specific setups.'%}
That being said, cuArms has the clear advantage that it is better suited to higher numbers of robots due to the decentralized/factorized approach.

The experiments were run with [this commit](https://github.com/vhartman/multirobot-pathplanning-benchmark/commit/01dd3efa9fb651c263de5e8708ee7f3660b57c3d) in the benchmarking repo.
The CoMotion fork is [here](https://github.com/vhartman/comotion), but I would not vouch for any implementation here, except that it matches what RAI is doing.

#### Next steps
- I would at some point like to implement most of this in a different language. Might be a good exercise to write some C++ by hand again.{% include sidenote.html text='And then run some LLM over it to get it more optimized again.'%} The main problem with this is that it is quite convenient to be able to set up environments in Python.
- Better sampling strategies seem to be the next thing for larger scenes, and for faster convergence. There's a reason why the factorized approach works well.
- I think I need to work on the benchmark to make stuff more reproducible, and make it easier to use for comparisons. This is mostly freezing assignments and IK solutions.
- It would be nice to add a GPU backend for collision checking and forward kinematics to see how SIMD approaches compare here.
- The vibed SIMD backend is worse than the results the CoMotion-authors achieved. This means there is still some headroom even there to work with properly compiled kernels here. 
- I should likely also give the same treatment that I gave to BiRRT* to the other planners at some point.
- Some of the visualizations shown here make it quite obvious that the main cost-driver is suboptimal IK solutions. I would need to look at this.

# Appendix
I reran the subset of the experiments that has sequential goal assignments.
I only did it for BiRRT* with the RAI backend, and with the CoMotion backend.
Compared to before, I ran everythign here sequentially and for shorter times than in the paper (however that does not matter since we usually achieve better final costs), and it is only 5 seeds.
Below, we report the medians of the 5 runs.

There are some settings, where th CoMotion backend does not yet have feature-parity, specifically the ones with the mobile robots.
This is caused by rounded boxes in RAI, which I did not yet port to CoMotion.
Just making them 0-radius makes some of the IK solutions infeasible, and thus the run would not be comparable.

In the plots we can already see that the curves are all better than the originally published ones.
Also, it is confirmed on a wide variety of experiments that the CoMotion backend is much faster than the RAI backend. 

<link rel="stylesheet" href="{{ '/assets/multi-robot-planning-but-faster/appendix.css' | relative_url }}">

<div class="performance-appendix-curves">
<img loading="lazy" src="{{ site.url }}/assets/multi-robot-planning-but-faster/appendix-convergence-loglog.png" alt="Current RAI and CoMotion cost convergence for twenty fixed-sequence environments. Medians and interquartile ranges over completed runs, with up to five seeds per backend. Mobile scenes use RAI only. Dotted lines show published final costs; dash-dot curves show figure-extracted cuArms results for the two spiral towers, Truss and Cube. Logarithmic time and cost axes.">
</div>

In addition to the plots, I also summarized the data the same way as before in the paper, namely presenting the initial solution time, and the final cost that we got.
Keep in mind here that the planners ran for much shorter than in the original paper, so the environments where we did not fully converge to the same cost as in the original paper are likely due to that.

Bold numbers always mark the best value per row.

<div class="performance-appendix">
<div class="table-scroll" role="region" aria-label="Published and current planning results" tabindex="0">
<table class="decimal-aligned" aria-describedby="appendix-table-note">
<thead>
<tr><th rowspan="2" scope="col" class="scene-heading">Environment</th><th colspan="2" scope="colgroup" class="group-start">Published<small>longer runs for final cost</small></th><th colspan="2" scope="colgroup" class="group-start rai-heading">RAI</th><th colspan="2" scope="colgroup" class="group-start comotion-heading">CoMotion</th></tr>
<tr><th scope="col" class="group-start">First [s]</th><th scope="col">Final cost</th><th scope="col" class="group-start">First [s]</th><th scope="col">Final cost</th><th scope="col" class="group-start">First [s]</th><th scope="col">Final cost</th></tr>
</thead><tbody>
<tr><th scope="row">Simple</th><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>17</span></span></td><td><strong><span class="decimal-number"><span>2</span><span>.</span><span>27</span></span></strong></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>0338</span></span></td><td><strong><span class="decimal-number"><span>2</span><span>.</span><span>27</span></span></strong></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0134</span></span></strong></td><td><strong><span class="decimal-number"><span>2</span><span>.</span><span>27</span></span></strong></td></tr>
<tr><th scope="row">2D handover</th><td class="group-start"><span class="decimal-number"><span>4</span><span>.</span><span>13</span></span></td><td><strong><span class="decimal-number"><span>17</span><span>.</span><span>90</span></span></strong></td><td class="group-start"><span class="decimal-number"><span>1</span><span>.</span><span>54</span></span></td><td><span class="decimal-number"><span>18</span><span>.</span><span>45</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>41</span></span></strong></td><td><span class="decimal-number"><span>18</span><span>.</span><span>03</span></span></td></tr>
<tr><th scope="row">2D random</th><td class="group-start"><span class="decimal-number"><span>7</span><span>.</span><span>95</span></span></td><td><span class="decimal-number"><span>26</span><span>.</span><span>09</span></span></td><td class="group-start"><span class="decimal-number"><span>1</span><span>.</span><span>87</span></span></td><td><span class="decimal-number"><span>26</span><span>.</span><span>28</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>1</span><span>.</span><span>57</span></span></strong></td><td><strong><span class="decimal-number"><span>25</span><span>.</span><span>69</span></span></strong></td></tr>
<tr><th scope="row">2D hallway</th><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>37</span></span></td><td><span class="decimal-number"><span>9</span><span>.</span><span>76</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>112</span></span></td><td><span class="decimal-number"><span>9</span><span>.</span><span>67</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0531</span></span></strong></td><td><strong><span class="decimal-number"><span>9</span><span>.</span><span>30</span></span></strong></td></tr>
<tr><th scope="row">Three agents</th><td class="group-start"><span class="decimal-number"><span>1</span><span>.</span><span>7</span></span></td><td><span class="decimal-number"><span>6</span><span>.</span><span>35</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>432</span></span></td><td><span class="decimal-number"><span>6</span><span>.</span><span>23</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>225</span></span></strong></td><td><strong><span class="decimal-number"><span>6</span><span>.</span><span>19</span></span></strong></td></tr>
<tr><th scope="row">Triple waypoints</th><td class="group-start"><span class="decimal-number"><span>1</span><span></span><span></span></span></td><td><span class="decimal-number"><span>17</span><span>.</span><span>34</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>117</span></span></td><td><span class="decimal-number"><span>11</span><span>.</span><span>51</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0338</span></span></strong></td><td><strong><span class="decimal-number"><span>10</span><span>.</span><span>81</span></span></strong></td></tr>
<tr><th scope="row">Welding</th><td class="group-start"><span class="decimal-number"><span>1</span><span>.</span><span>93</span></span></td><td><span class="decimal-number"><span>14</span><span>.</span><span>49</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>147</span></span></td><td><span class="decimal-number"><span>7</span><span>.</span><span>67</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0417</span></span></strong></td><td><strong><span class="decimal-number"><span>7</span><span>.</span><span>35</span></span></strong></td></tr>
<tr><th scope="row">Arm handover</th><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>8</span></span></td><td><strong><span class="decimal-number"><span>12</span><span>.</span><span>12</span></span></strong></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>0642</span></span></td><td><span class="decimal-number"><span>12</span><span>.</span><span>31</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0265</span></span></strong></td><td><span class="decimal-number"><span>12</span><span>.</span><span>34</span></span></td></tr>
<tr class="section-start"><th scope="row">Egg cartons</th><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>8</span></span></td><td><span class="decimal-number"><span>44</span><span>.</span><span>46</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>195</span></span></td><td><span class="decimal-number"><span>44</span><span>.</span><span>38</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0508</span></span></strong></td><td><strong><span class="decimal-number"><span>43</span><span>.</span><span>03</span></span></strong></td></tr>
<tr><th scope="row">Bottles</th><td class="group-start"><span class="decimal-number"><span>16</span><span></span><span></span></span></td><td><span class="decimal-number"><span>15</span><span>.</span><span>16</span></span></td><td class="group-start"><span class="decimal-number"><span>5</span><span>.</span><span>78</span></span></td><td><span class="decimal-number"><span>15</span><span>.</span><span>37</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>1</span><span>.</span><span>38</span></span></strong></td><td><strong><span class="decimal-number"><span>14</span><span>.</span><span>68</span></span></strong></td></tr>
<tr><th scope="row">Box rearrangement</th><td class="group-start"><span class="decimal-number"><span>3</span><span>.</span><span>39</span></span></td><td><span class="decimal-number"><span>28</span><span>.</span><span>27</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>453</span></span></td><td><span class="decimal-number"><span>28</span><span>.</span><span>29</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>102</span></span></strong></td><td><strong><span class="decimal-number"><span>26</span><span>.</span><span>84</span></span></strong></td></tr>
<tr><th scope="row">Box reorientation</th><td class="group-start"><span class="decimal-number"><span>3</span><span>.</span><span>76</span></span></td><td><span class="decimal-number"><span>55</span><span>.</span><span>74</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>276</span></span></td><td><span class="decimal-number"><span>56</span><span>.</span><span>21</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>108</span></span></strong></td><td><strong><span class="decimal-number"><span>54</span><span>.</span><span>53</span></span></strong></td></tr>
<tr><th scope="row">Pyramid</th><td class="group-start"><span class="decimal-number"><span>3</span><span>.</span><span>23</span></span></td><td><span class="decimal-number"><span>18</span><span>.</span><span>09</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>214</span></span></td><td><span class="decimal-number"><span>15</span><span>.</span><span>44</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0546</span></span></strong></td><td><strong><span class="decimal-number"><span>14</span><span>.</span><span>80</span></span></strong></td></tr>
<tr><th scope="row">Box stacking</th><td class="group-start"><span class="decimal-number"><span>7</span><span>.</span><span>03</span></span></td><td><span class="decimal-number"><span>17</span><span>.</span><span>90</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>284</span></span></td><td><span class="decimal-number"><span>17</span><span>.</span><span>32</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0824</span></span></strong></td><td><strong><span class="decimal-number"><span>16</span><span>.</span><span>23</span></span></strong></td></tr>
<tr class="section-start"><th scope="row">Mobile wall</th><td class="group-start"><span class="decimal-number"><span>11</span><span>.</span><span>6</span></span></td><td><span class="decimal-number"><span>46</span><span>.</span><span>73</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>1</span><span>.</span><span>81</span></span></strong></td><td><strong><span class="decimal-number"><span>46</span><span>.</span><span>11</span></span></strong></td><td class="group-start">—</td><td>—</td></tr>
<tr><th scope="row">Mobile strut</th><td class="group-start"><span class="decimal-number"><span>13</span><span>.</span><span>7</span></span></td><td><span class="decimal-number"><span>326</span><span>.</span><span>51</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>6</span><span>.</span><span>33</span></span></strong></td><td><strong><span class="decimal-number"><span>318</span><span>.</span><span>10</span></span></strong></td><td class="group-start">—</td><td>—</td></tr>
<tr class="section-start"><th scope="row">Truss</th><td class="group-start"><span class="decimal-number"><span>3</span><span>.</span><span>92</span></span></td><td><span class="decimal-number"><span>69</span><span>.</span><span>99</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>808</span></span></td><td><span class="decimal-number"><span>69</span><span>.</span><span>17</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>161</span></span></strong></td><td><strong><span class="decimal-number"><span>64</span><span>.</span><span>46</span></span></strong></td></tr>
<tr><th scope="row">Spiral tower (4 arms)</th><td class="group-start"><span class="decimal-number"><span>26</span><span>.</span><span>4</span></span></td><td><span class="decimal-number"><span>100</span><span>.</span><span>44</span></span></td><td class="group-start"><span class="decimal-number"><span>2</span><span>.</span><span>54</span></span></td><td><span class="decimal-number"><span>96</span><span>.</span><span>89</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>535</span></span></strong></td><td><strong><span class="decimal-number"><span>91</span><span>.</span><span>56</span></span></strong></td></tr>
<tr><th scope="row">Spiral tower (2 arms)</th><td class="group-start"><span class="decimal-number"><span>1</span><span>.</span><span>37</span></span></td><td><span class="decimal-number"><span>44</span><span>.</span><span>21</span></span></td><td class="group-start"><span class="decimal-number"><span>0</span><span>.</span><span>325</span></span></td><td><span class="decimal-number"><span>45</span><span>.</span><span>07</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>0664</span></span></strong></td><td><strong><span class="decimal-number"><span>44</span><span>.</span><span>13</span></span></strong></td></tr>
<tr><th scope="row">Cube</th><td class="group-start"><span class="decimal-number"><span>41</span><span>.</span><span>9</span></span></td><td><span class="decimal-number"><span>135</span><span>.</span><span>30</span></span></td><td class="group-start"><span class="decimal-number"><span>2</span><span>.</span><span>97</span></span></td><td><span class="decimal-number"><span>122</span><span>.</span><span>40</span></span></td><td class="group-start"><strong><span class="decimal-number"><span>0</span><span>.</span><span>547</span></span></strong></td><td><strong><span class="decimal-number"><span>114</span><span>.</span><span>88</span></span></strong></td></tr></tbody></table></div>
<p class="table-note" id="appendix-table-note">Medians over completed runs; five seeds attempted per current backend. Final costs use different budgets: 30–180 s for the current runs, 100–1000 s for the published runs. Bold marks the best value at the displayed precision.</p>
</div>
