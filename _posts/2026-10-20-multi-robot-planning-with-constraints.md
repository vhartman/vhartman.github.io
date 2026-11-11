---
layout: post
title: "Multi-robot multi-goal planning with affine constraints"
date: 2026-11-01 12:00:00 +0200
# permalink: /scalable-multi-robot-shortcutting/
categories: path-planning
# published: false
---

<p class="preface">
I am writing up work by a student here because I think it deserves some more visibility.
As a secondary benefit, it is motivation to make me finally merge this into the main branch of the multi-robot multi-goal planning benchmark I am maintaining.
</p>

During my postdoc, I was mostly working on multi-robot multi-goal motion planning, and how to make this planning (1) possible at all, (2) optimal, and (3) reasonably fast.
I think (1) is (at least to me) pretty clearly solved by now.
(2) is also at least theoretically done, but not in a practical way, since the planners tend to be too slow.

Also during my postdoc, I (together with [Yijiang](https://yijiangh.github.io/)) supervised a student (Giovanni Ielmini) for a semester thesis working on a constrained version of the planners, to enable, e.g., bimanual transport, or 'hold something upright during transport'.
This supervision resulted in [this poster](https://www.research-collection.ethz.ch/entities/publication/27c0540e-6bde-4314-b068-c48e70002b93).

This post here is a short writeup of the work he did, both to motivate me to finally finish a merge that I started a while ago, and to add the examples we came up with to the repo.{% include sidenote.html text='And to be honest, to understand the implementation details that sometimes get lost during a thesis.'%}

Here, as a first part, I will focus on the integration of the linear (equality and inequality) constraints, since they make some behaviors available that is quite nice (coupled motion between separate robots through shared joints), and it is quite a bit simpler than the nonlinear constraints that he also worked on.

Nonlinear constraints do work in very similar ways as the linear constraints but require a bit more integration work for the actual implementation, so I'll leave the writeup and the finalization of the merge for the future (and the next post).

# Motion planning with constraints

We are only going to tackle the planning with constraints for sampling-based planners, so this is the related work I am going to talk about here.{% include sidenote.html text='For optimization-based planning you do not need to do too much, except for adding the constraint to your optimization problem.'%}

In motion planning in general, we want to find a path consisting of a sequence of configurations $$q$$, that lead from a start to a goal (or a goal set), and are collision-free $$q\in\mathcal{C}_\text{free}$$.
In constrained motion planning, we do not only want to find a collision-free path, but that collision-free path also needs to fulfill some set of constraints.
So our configurations need to be in some (possibly lower-dimensional) manifold of the space:

$$
q \in \left(\mathcal{C}_\text{constrained} = \{ q | f(q) = 0 \}\right) \cap \mathcal{C}_\text{free}.
$$

Here $$f(q)$$ could be almost anything, such as a constraint for a specific joint index (e.g., $$q_5 = 0$$), or a more complex transformation such as 'the end-effectors z-axis always needs to point upwards'.

From a conceptual standpoint, one of the ways to deal with this is quite simple: instead of sampling the free space, we can just sample the constraint manifold, and run the same planners.
In these planners, we then obviously also need to ensure that the connections between the samples are in the constrained submanifold, but that's about it.

The problems then pile up when we actually think about the details:{% include sidenote.html text='As always, unfortunately.'%} In collision-free planning (even without constraints), we sometimes do already have difficulties to sample collision-free configurations, mostly in narrow passages.
This is the case since we usually do some form of rejections sampling: we sample in the full configurations space of all robots and then reject anything that is in collision.
If we are then in a narrow passage, the likelihood of sampling something collision-free is simply quite low.

Now, when looking at constraints, the sampling procedure becomes more complex: Some constraint manifolds have volume zero, meaning that we will never sample them by random chance, meaning that we can not continue doing what we did before.
One solution to this problem is trying to project samples onto the constraints, i.e., sampling a configuration (which does not necessarily fulfill the constraints), and then moving the configuration onto the constraint manifold.
This is what [this work here](https://www.annualreviews.org/content/journals/10.1146/annurev-control-060117-105226) or [here](https://journals.sagepub.com/doi/full/10.1177/0278364919868530?casa_token=mmu4TIl7LZ8AAAAA%3Afydy_11WtGfWEGMYDTAb4ySOcu0Mf8iG4R_H9AoqMvzP5RrNZCKk-O_Y_tsmbwuLOrO8-rtgYjOXCiA) introduced.

The projection step can be done in various ways, the simplest one is formulating a small optimization problem, and running gradient descent in order to obtain the samples.
This opens a bit of a can of worms:
The approach of simply running gradient descent brings samples only to the boundary of the space, which we do not like in many cases.{% include sidenote.html text='This concerns only inequality constraints.'%}
Further, we will not always do very well in discovering different parts of the solution manifold.
For some more discussion [see this paper](https://arxiv.org/pdf/2407.03035).

In order to make the planners faster, we can keep doing the same things, but parallelize the projection step, as [McVAMP](https://commalab.org/papers/mcvamp/) did.
There are some other nice gems in there, but that's the gist of it.

Slightly differently, instead of sampling and projecting, we can also try to reparametrize our space such that all configurations that we sample are in the constrained space by definition.
This is what [ReVAMP](https://arxiv.org/pdf/2609.30213v1) is doing, again in a parallelized fashion.

#### Affine constraints

If we constrain ourself to only affine constraints, $$f(q)$$ will always have the form $$Aq - b = 0$$, or for inequalities $$Hq - h \leq 0$$, and the problem will become much simpler.
Particularly, the projection operations that we mentioned above become a lot simpler.
In some cases we do not even need to project samples, but we can directly sample from the constraint manifold.

Since this is what we'll look at in detail, I am not going to talk about the methods of linear projections here, but will do that a couple sections further down.

# Multi-robot planning with multiple goals

Multi-robot multi-goal planning can be written as a single (big) motion planning problem, where different constraints become active at various different times throughout the problem.

The only constraints we allowed until now were equality or set constraints at single timesteps.
These constraints at the single timesteps are the mode switches, i.e., configurations or 'goals' that we have to reach before being allowed to proceed to the next goal.
For example: if we want to do a pick-and-place sequence, we first need to reach the configuration (the equality constraint) that 'grabs something', then we plan a path to the configuration that 'places something'.
We are here not imposing anything on the form of those constraints: They can contain end-effector constraints, they could be pose constraints, they could be single configurations, or they could be a disjoint set of various different poses.
The only thing that we require here are that we can sample valid solutions satisfying the constraint.

If we are given these goal constraints, the motion planning problem is then usually 'reach these goals in a certain order', in order to enable for example a 'pick-and-place' sequence of multiple robots, or to enable multiple robots stacking objects on top of each other.
For now (without loss of too much generality) we are going to assume that we are only tackling settings where the order of goals we have to reach is fully given.

Adapting the description from a paper ([WRAP](https://arxiv.org/pdf/2609.29407)) a student (William Schnyder) I supervised wrote, whose description I like better than mine:
We use $$\mathcal C=\prod_{r\in\mathcal R}\mathcal C_r$$ as the joint configuration space (as implicitly done above), and $$m_k$$ as the mode before goal $$k$$.
We want to find a continuous path $$q:[0,T]\to\mathcal C$$ and times $$0=t_0<\cdots<t_K=T$$ satisfying

$$q(0)=q_{\mathrm{start}},\qquad q_{S_k}(t_k)\in G_k,\qquad q(t)\in\mathcal Q_{\mathrm{free},m_k}\ \text{for }t\in[t_{k-1},t_k].$$

The modes specify how and where objects are attached (and are therefore enough to reconstruct the collision geometry).

Importantly, these goal constraints/the goal set $$G_k$$ applies to a subset of all robots $$S_k\subseteq\mathcal R$$ at a time: different robots can have different goals at the same time.
A simple example would be that robot 1 needs to pick object A before robot 2 picks object B.
Here, the constraint (or the goal configuration) of robot 1 picking object A does not have any impact on robot 2, which can move freely.

# Introducing path constraints to the problem

In the formulation we have here, introducing constraints is relatively straightforward for the problem formulation.
In addition to the setting before (i.e., having goal constraints), a task now simply contains any additional constraints that need to be respected _during that task_.
Additionally, there might be global constraints that we need to respect: it could be the case that some robots are coupled, or that we have two robot arms mounted on a shared base.
Linear inequality constraints could also be used to model more complex joint limits than just bounding boxes on each joint separately.

So the only thing we have to do is adding constraints to the tasks and any global constraints that might have to be respected at all times.
At planning time, we can then just look up in each mode what constraints have to be satisfied (all global constraints plus all constraints of all currently active tasks), and take those into account in our planner.

We extend the motion planning problem from above with globally active constraints and task constraints.
We use $$F_m$$ to describe the set of constraint-satisfying configurations:

$$F_m=\{q\mid A_mq=b_m,\ H_mq\leq h_m,\ \ell\leq q\leq u\}.$$

Instead of only constraining the configurations to fulfill the goal constraints from above, we now require $$q(t)\in F_{m_k}\cap\mathcal C_{\mathrm{free},m_k}$$ throughout each mode.
At a mode switch, the configuration must satisfy the goal and both modes' applicable constraints.

This alteration of the original problem can also be adapted to the nonlinear constraints by replacing the set definition.

#### Multi-robot planning problems with constraints

I am going to give some examples for linear constraints here, and what they enable.
Below, you can see the videos for

- 'Linked puzzle': A setting where the circle and the rectangle have to reach the other side and go back, but they are linked through their $$y$$ axis.
- 'RFL stacking' models the [robotic fabrication lab](https://ita.arch.ethz.ch/archteclab/rfl.html) at ETH Zürich, a large-scale fabricator for digital fabrication. It has four ceiling-mounted robots, of which 2 share the same $$y$$-axis. Since they are mounted on the same moving axis, they can also not swap positions both in $$x$$ and in $$y$$ direction, leading to both equality and inequality constraints.
- 'Husky stacking' is a setting with two UR10s on a Husky base.
- 'Single carrier' is a setting where two OpenArm arms are mounted on a UR10, similar to what [Ultra robotics](https://ultra.tech/) is using. The two-carrier settings use two of these assemblies.
- 'Shared rail' has $$N$$ UR5s on a shared rail. This is similar to the RFL setting above, but with more robots to test scaling of the inequality constraint-handling. In the 'Linked rail' variant, the robots also need to obey a max-distance constraint between each other.
- 'Constrained corridor' is a setting with a mobile UR5 with an artificially constrained corridor where it can move. In this setting, this is a bit of a made-up example, but in practice, this just establishes handling non-box boundaries. The tapered variant is called 'Constrained corridor (tapered)'.

<div class="constraint-video-grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;">
<figure style="margin:0;min-width:0;">
<figcaption>Linked puzzle</figcaption>
<video autoplay loop muted playsinline controls preload="none" aria-label="Linked puzzle" poster="{{ site.url }}/assets/multi-robot-constraints/puzzle-clean-poster.jpg" style="display:block;width:100%;">
<source src="{{ site.url }}/assets/multi-robot-constraints/puzzle-clean.mp4" type="video/mp4">
</video>
</figure>
<figure style="margin:0;min-width:0;">
<figcaption>RFL stacking</figcaption>
<video autoplay loop muted playsinline controls preload="none" aria-label="RFL stacking" poster="{{ site.url }}/assets/multi-robot-constraints/rfl-stacking-clean-poster.jpg" style="display:block;width:100%;">
<source src="{{ site.url }}/assets/multi-robot-constraints/rfl-stacking-clean.mp4" type="video/mp4">
</video>
</figure>
<figure style="margin:0;min-width:0;">
<figcaption>Husky stacking</figcaption>
<video autoplay loop muted playsinline controls preload="none" aria-label="Husky stacking" poster="{{ site.url }}/assets/multi-robot-constraints/husky-stacking-clean-poster.jpg" style="display:block;width:100%;">
<source src="{{ site.url }}/assets/multi-robot-constraints/husky-stacking-clean.mp4" type="video/mp4">
</video>
</figure>
<figure style="margin:0;min-width:0;">
<figcaption>Two-carrier sorting (single table)</figcaption>
<video autoplay loop muted playsinline controls preload="none" aria-label="Two-carrier single-table sorting" poster="{{ site.url }}/assets/multi-robot-constraints/two-carrier-sorting-single-table-clean-poster.jpg" style="display:block;width:100%;">
<source src="{{ site.url }}/assets/multi-robot-constraints/two-carrier-sorting-single-table-clean.mp4" type="video/mp4">
</video>
</figure>
<figure style="margin:0;min-width:0;">
<figcaption>Shared rail: 3 UR5s</figcaption>
<video autoplay loop muted playsinline controls preload="none" aria-label="Shared rail: 3 UR5s" poster="{{ site.url }}/assets/multi-robot-constraints/shared-rail-three-clean-poster.jpg" style="display:block;width:100%;">
<source src="{{ site.url }}/assets/multi-robot-constraints/shared-rail-three-clean.mp4" type="video/mp4">
</video>
</figure>
<figure style="margin:0;min-width:0;">
<figcaption>Constrained corridor: mobile UR5</figcaption>
<video autoplay loop muted playsinline controls preload="none" aria-label="Constrained corridor: mobile UR5" poster="{{ site.url }}/assets/multi-robot-constraints/mobile-corridor-clean-poster.jpg" style="display:block;width:100%;">
<source src="{{ site.url }}/assets/multi-robot-constraints/mobile-corridor-clean.mp4" type="video/mp4">
</video>
</figure>
</div>

#### Why do we need these constraints

Now, in a couple of these scenarios we only have the equality constraints due to a modeling choice we made: We choose to model two robot arms on a shared base as two separate robots, that are coupled through an equality constraint.
That means that we are introducing the degrees of freedom of the base twice (or more times): for each robot once.

The question that you should ask here is 'why you would want to model these problems like that'?
After all, for a shared base, you could simply model the problem such that we only have the base once in our degrees of freedom.
The answer to this is largely historical, but I do also believe that through this modeling choice some things become much simpler than they would be compared to the more intuitive modelling choice.

In many cases in our planner we want to refer to a single robot (for example in shortcutting), or to a subset of all indices which belong to a single robot.
If we use the more intuitive representation, some indices belong to multiple robots, therefore requiring some bookkeeping.
Additionally, the goal constraints and mode switching becomes a bit more involved.

But I think it would also be possible to achieve this multi-robot multi-goal planning the other way:
This is an implementation and bookkeeping choice, not a claim that the redundant formulation is fundamentally better.
We could keep the external logical-robot interface while sampling unique physical coordinates internally and expanding them back into the redundant representation; informed sampling would still need to respect the original cost bound.

#### Planning with constraints

So now how do we solve this problem?
The answer is annoyingly{% include sidenote.html text='Because who does not like to invent some new stuff?'%} simple: We take the approach from above that works for constrained planning in the single-goal setting, and add a bit of bookkeeping to deal with the fact that the required constraints change over the different modes.

That means that in our planners we project sampled configurations onto the subspace that the constraints encode.
The only difficulty is then keeping track of which constraints are active in which mode, and on which robots/indices of the full space.
So the devil is in the detail, which we already glanced over a bit above: We have to ask ourselves some questions about implementation choices that make a lot of difference:

- Can we reparametrize our space in order to avoid projection?
- If we can not reparameterize our constrained set, how do we sample and project our samples?
  - Do we just sample uniformly random, or do we do something else? 
- Where in the algorithm do we project our samples?
- Should we do any kind of informed sampling? If so, how?

This all concerns equality constraints. 
The question that is then left is how do we actually deal with the inequality constraints?

Once we answered all those questions, we are effectively done with our sampling, and we can run the normal sampling-based planner in this subspace.
So this is what we are going to do now, but not in the order above.

**Projection methods:** For a linear equality constraint $$Aq-b=0$$, we can compute the projection of a sample $$q$$ with a closed-form solution: $$q_\mathrm{proj}=q-A^+(Aq-b)$$, where $$A^+$$ is the Moore--Penrose pseudoinverse.
For a fixed set of constraints $$A$$ we could then compute $$A^+$$ once, and reuse it.

Alternatively, we can try to find a point $$q_0$$ satisfying the constraints, and then find the directions in which we are allowed to move without breaking the constraints.
We can do this by finding the orthonormal basis $$Z$$ satisfying $$AZ=0$$.
From a sample $$q$$, we can then compute the nullspace coordinates (the coordinates in which we can move without violating the constraint) via $$z=Z^\top(q - q_0)$$.
Then $$q_\text{proj} = q_0 + Z(Z^\top(q - q_0))$$ will be a new valid configuration.
Here, we can also precompute $$ZZ^\top$$, trading off two possibly sparse matrix-vector products with a single possibly dense matrix-vector multiplications.

Below, we compare projection, nullspace sampling, and the dense projector in a microbenchmark.
We compare version where we compute multiple samples at a time, i.e., batch the solution, and only run a single projection method at a time.

**Inequality constraints:** Finally, we need to deal with inequality constraints.

- The simplest way possible would be rejecting samples that do not fulfill the constraints after we projected onto the equality constraints. The problem is the usual one with rejection sampling: If the constrained space is small compared to the full space, we have a very low probability of success.
- An alternative would be to project onto the boundary, but that has the problem that this would lead to a non-uniform density, respectively to a high number of samples _on_ the boundary.{% include sidenote.html text='This can have implications on the planning, and how quickly the planner converges to a good solution.'%} This projection onto the boundary can be done with a small quadratic program.
- In many cases it is possible to directly sample the inequality constraints:
  - One possibility for some affine constraints is directly sampling the feasible polytope given by the constraints. This usually requires some preprocessing of the constraints, and is not always practical. 
  - Sampling the valid region of the constraints can also be done by projection onto the constraint and then running [hit-and-run sampling](https://search.r-project.org/CRAN/refmans/hitandrun/html/hitandrun-package.html). As an extension, we can rescale some axes of the polytope in order to better explore narrow regions.

**Informed sampling:** To improve our solution after we have found the first path, we do the same thing as in the vanilla planner: We do informed sampling, and we do shortcutting. Informed sampling is then done similar to what we do now already as well: We sample a point, and reject it if there is no chance that the point could improve the solution cost even in the best case.

Again, as before, there's the same problems as usual with rejection sampling: Namely that we get a smaller and smaller probability of actually finding samples that improve the solution.

There's some smarter stuff that we can do that I'll talk about in more detail in a later post, but we can also do hit-and-run sampling for informed sampling to avoid the rejection sampling problems.

#### Shortcutting with constraints
As a recap: shortcutting basically replaces high-cost (i.e. long) parts of an existing path with a linear interpolation.
We do this by choosing two points on the path, and checking if the two points could be connected with a cheaper path (i.e. the linear interpolation).

Compared to constraint-free motion planning, shortcutting becomes a bit more complicated if we consider general nonlinear constraints, since the linear interpolation between two points does not necessarily fulfill the constraints anymore.
The fun realization that is going to make our lives a lot{% include sidenote.html text='And I truly mean a lot!'%} easier is that a linear interpolation between two configurations that fulfill a linear constraint will always lead to a constraint-fulfilling configuration as well, and the same is true for  inequality constraints.

We discussed multi-robot shortcutting before [here](/multi-robot-shortcutting) and [here](/scalable-multi-robot-shortcutting), and the approach we ended up with was roughly:

- Choose a subset of robots that we shortcut at once.
- Shortcut those robots
- Repeat

The issue that we can now have is that some robots are linked through constraints (specifically robots that share a degree of freedom that is duplicated).
That means that if we shortcut one of those robots, but not the other, we break the constraint, meaning that we need to account for that in our very simple loop above.

We can do that by identifying the groups that need to be shortcut together, i.e., all the degrees of freedom that are linked through constraints, and then respect those groups in the first step.
So instead of 'choosing a set of robots', we choose a set of indices that can not break any constraint, and then proceed as before.

We can then try to figure out the best way to choose the points between which we shortcut, and the best way of choosing groups to shortcut, but this is not an analysis we do here.

# Benchmarking

**Equality projections:**
We are first starting with a microbenchmark of the projection methods: As mentioned before, we compare the three projection methods from above.
We do this on a couple of the environments that we introduced above, both for a free sample we need in planning, and also using a 'pinned transition', i.e., a sample satisfying a transition constraint.{% include sidenote.html text='In the unconstrained setting, sampling a transition can be done by (1) sampling a goal, and then (2) sampling the rest of the robots/the free dimensions. With constraints, a given goal configuration can be part of a constraint, meaning that we can not sample the rest of the dimensions freely, but need to make sure that the constraints are all satisfied.'%}

<img src="{{ site.url }}/assets/multi-robot-constraints/equality-batching.png" alt="Matched scalar and batch-of-256 equality projections across seven scenarios, measured serially on mains power with setup excluded" style="width:100%;">

Generally, the batched projection is a magnitude faster for all the approaches.
Between the methods, the difference is definitely observable, but only roughly a factor of two:
The cached pseudoinverse approach is consistently the best when batched for the ordinary configurations.
For the transition configurations, there is no clear winner between the methods.

**Inequality sampling:** We continue with a similar microbenchmark on the inequality-satisfying constraints. Similar to before, we do again look at both the 'free' and the transition samples.

<img src="{{ site.url }}/assets/multi-robot-constraints/inequality-batching.png" alt="Matched scalar and batch-of-256 inequality samplers, measured serially on mains power with setup excluded" style="width:100%;">

Compared to before, for the inequality sampling there is not as much to gain by batching, except in the rejection approach.
Direct feasible sampling tends to be the fastest method, but there is no clear winner on all the environments.
We can however see that rejection sampling can be much slower than the other approaches if we have many constraints, or the free space is much larger than the constraint-satisfying manifold.

Below we also look at the distribution of the samples.
However, the more important result is the performance of the projection method in the planner, which we'll look at below.

<details>
<summary>Boundary samples and correlation</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/inequality-sampling-diagnostics.png" alt="Boundary concentration and sample correlation; free-space samples on the left and pinned-transition samples on the right" style="width:100%;">
<p>Lag one means comparing each sample with the next one. For each coordinate, we measure how strongly its values are correlated between consecutive samples, and show the largest correlation across coordinates that are not fixed.
<br>
Values near 1 mean that successive samples are similar; values near 0 mean little correlation.</p>
</details>

**Shortcutting:** Before proceeding with the full planners, we are going to have a look at shortcutting alone:
We take a valid initial path, and run different shortcutting versions on the plans to see how convergence differs between the methods.

The methods are effectively a copy from the previous posts [here](/multi-robot-shortcutting) and [here](/scalable-multi-robot-shortcutting):

- *Full* shortcuts all coordinates at the same time
- *Index groups* samples coordinate groups and adds equality-coupled indices to the set
- *Mechanism groups* combine equality-connected blocks belonging to the same robot set.

Then, how we sample endpoints:

- *Compatible runs* directly sample uniformly in the interval that keeps the robots' tasks unchanged
- *Endpoints* samples uniformly over the whole path and checks admissibility afterwards.

Finally, we adapt the methods from before:

- *Robot tree + gain* operates on logical robots
- *Equality-atom tree + gain* uses mechanism groups instead.

<img src="{{ site.url }}/assets/multi-robot-constraints/offline-shortcutting.png" alt="Offline shortcutting cost over time for clearing eight blocks, building two stacks, two-carrier stacking, and single-carrier sorting" style="width:100%;">

Sampling by robot as we did very successfully before does barely help here, since most single-robot attempts violate some constraint.
Thus, Robot tree + gain barely improves.
On the other hand, using equality-aware groups improve three scenes quickly.

<details>
<summary>Logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/offline-shortcutting-log.png" alt="Offline shortcutting cost with a logarithmic time axis" style="width:100%;">
</details>

<details>
<summary>All shortcutting methods</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/offline-shortcutting-all.png" alt="All ten shortcutting methods on the same four paths" style="width:100%;">
<details>
<summary>Logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/offline-shortcutting-all-log.png" alt="All ten shortcutting methods with a logarithmic time axis" style="width:100%;">
</details>
</details>

**Planning:** Finally, we run the full planner with different inequality-sampling methods.

<img src="{{ site.url }}/assets/multi-robot-constraints/inequality-planning.png" alt="Planning convergence for QP projection, direct feasible sampling, and direct sampling with an informed walk on six scenarios, with five planner seeds per policy" style="width:100%;">

The sampling policies find the initial solutions in similar times, as also seen below.
Convergence is also relatively similar.
The biggest thing to notice in the plots below is that rejection sampling does not find a feasible solution in some of the problems that have a smaller feasible set.

The informed walk lowers median final cost a bit compared to the other methods.

<details>
<summary>Time to first solution</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/inequality-planning-first.png" alt="Fraction solved over time across all five seeds, retaining timeouts" style="width:100%;">
</details>

<details>
<summary>Logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/inequality-planning-log.png" alt="Three-policy inequality planning comparison with a logarithmic time axis" style="width:100%;">
</details>

<details>
<summary>All inequality-sampling policies</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/inequality-planning-all.png" alt="All five inequality-sampling policies, including rejection and rounded hit-and-run" style="width:100%;">
<details>
<summary>Logarithmic time axis</summary>
<img src="{{ site.url }}/assets/multi-robot-constraints/inequality-planning-all-log.png" alt="All five inequality-sampling policies with a logarithmic time axis" style="width:100%;">
</details>
</details>

#### Interactive viewer

<iframe
  src="{{ '/assets/multi-robot-constraints/viewer/index.html?data=two-carrier-stacking' | relative_url }}"
  title="Interactive replay of constrained multi-robot paths"
  loading="lazy"
  allowfullscreen
  style="display:block;position:relative;left:50%;transform:translateX(-50%);width:min(960px,94vw);max-width:none;height:600px;border:1px solid #ddd;border-radius:8px;margin:1rem 0;">
</iframe>

# Take away

This problem formulation is nice and simple: adding constraints is relatively easy.
What it boils down to is in the end a series of dispatchers to samplers that satisfy the various constraints, and orchestrating them.
The same approach can with a few minor additions be used to sample nonlinear constraints, and plan using the same way.

For linear constraints these samplers are relatively simple, but we can already see that some implementation details can play a big role in how quick we get so a solution and how well we converge.
For nonlinear constraints this will become a bit more annoying because it changes how much time is spent in various parts of the algorithms.

Caching and batching make equality projection practically free.
Inequality sampling is the harder problem, and very scene-dependent.
Shortcutting must respect coupled coordinates in order to have any chance to be useful.

Finally, I noticed during this work again how important diligent shortcutting is, and that we need to ensure that we really shortcut everything at some point, otherwise we end up with a lot of superfluous movement by robots that are not the 'active' robots.

#### Open questions

The clear next objective is extending this to nonlinear constraints, which enables much more realistic constraints, such as bimanual tasks, or orientation constraints when grasping and transporting something, or possibly also distance constraints between robots.

The problems tackled here (particularly the two-carrier scenarios in the interactive viewer) make it clear to me that the choice of keyframes is very important for how the path looks overall.
