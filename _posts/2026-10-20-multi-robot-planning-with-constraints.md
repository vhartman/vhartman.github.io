---
layout: post
title: "Multi-robot multi-goal planning with linear constraints"
date: 2026-10-13 12:00:00 +0200
# permalink: /scalable-multi-robot-shortcutting/
categories: path-planning
# published: false
---

<p class="preface">
I am writing up work by a student here because I think it deserves some more visibility, and as motivation to make me finally merge this into the main branch of the multi-robot multi-goal planning benchmark I am maintaining.
</p>

During my postdoc, I was mostly working on multi-robot multi-goal motion planning, and how to make this planning (1) possible at all, (2) optimal, and (3) reasonably fast.
I think (1) is (at least to me) pretty clearly solved by now.
(2) is also at least theoretically done, but not in a practicaly way, since the planners tend to be too slow still.

Also during my postdoc, I (together with [Yijiang](https://yijiangh.github.io/)) supervised a student for a semester thesis working on a constrained version of the planners, to enable, e.g., bimanual transport, or 'hold something upright during transport'.
This supervision resulted in [this poster](https://www.research-collection.ethz.ch/entities/publication/27c0540e-6bde-4314-b068-c48e70002b93).

This post here is a short writeup of the work he did, both to motivate me to finally finish a merge that I started a while ago, and to add the examples we came up with to the repo.{% include sidenote.html text='And to be honest, to understand the implementation details that sometimes get lost during a thesis.'%}

Here, as a first part, I will focus on the integration of the linear (equality and inequality) constraints, since they make some behaviors available that is quite nice (coupled motion between separate robots through shared joints), and it is quite a bit simpler than the nonlinear constraints that he also worked on.

Nonlinear constraints do work in very similar ways as the linear constraints but require a bit more integration work for the actual implementation, so I'll leave the writeup and the finalization of the merge for the future (and the next post).

# Related work: Motion planning with constraints

We are only going ot tackle the planning with constraints for sampling based planners, so this is the related work I am goign to talk about here.{% include sidenote.html text='For optimization based planning you do not need to do too much, except for adding the constraint to your optimization problem.'%}

In motion planning in general, we want to find a path consisting of a sequence of configurations $$q$$, that lead from a start to a goal (or a goal-set), and are colllision free $$q\in\mathcal{C}_\text{free}$$.
In constrained motion planning, we do not only want to find a collision free path, but that collision free path also needs to fulfill some set of constraints.
So our configurations need to be in some (possibly lower dimensional) manifold of the space:

$$
q \in \left(\mathcal{C}_\text{constrained} = \{ q | f(q) = 0 \}\right) \cap \mathcal{C}_\text{free}.
$$

Here $$f(q)$$ could be almost anything, such as a constraint for a specific joint index (e.g., $$q_5 = 0$$), or a more complex transformation such as 'the end-effectors z-axis always needs to point upwards'.

From a conceptual standpoint, one of the ways to deal with this is quite simple: instead of sampling the free space, we can just sample the constraint manifold, and run the same planners.
In these planners, we then obviously also need to ensure that the connections between the samples are in the constrained submanifold, but that's about it.

The problems then pile up when we actually think about the details:{% include sidenote.html text='As always, unfortunately.'%} In collision free planning (even witout constraints), we sometimes do already have difficulties to sample collision free configurations, mostly in narrow passages.
This is the case since we ususally do some form of rejections sampling: we sample in the full configurations space of all robots and then reject anything that is in collision.
If we are then in a narrow passage, the likelihood of sampling something collsion free is simply quite low.

Now, when looking at constraints, the sampling procedure becomes more complex: Some constraint manifolds have volume zero, meaning that we will never sample them by random chance, meaning that we can not continue doing what we did before.
One solution to this problem is trying to project samples onto the constraints, i.e., sampling a configuration (which does not necessarily fulfill the constraints), and then moving the configuration onto the constraint manifold.
This is what [this work here](https://www.annualreviews.org/content/journals/10.1146/annurev-control-060117-105226) or [here](https://journals.sagepub.com/doi/full/10.1177/0278364919868530?casa_token=mmu4TIl7LZ8AAAAA%3Afydy_11WtGfWEGMYDTAb4ySOcu0Mf8iG4R_H9AoqMvzP5RrNZCKk-O_Y_tsmbwuLOrO8-rtgYjOXCiA) introduced.

The projection step can be done in various ways, the simplest one is formulating a small optimization problem, and running gradient descent in order to obtain the samples.
This opens a bit of a can of worms:
The approach of simply running gradient descent brings samples only to the boundary of the space, which we do not like in many cases.
For some more discussion [marc paper].

In order to make the planners faster, we can keep doing the same things, but parallelize the projection step, as [McVAMP](https://commalab.org/papers/mcvamp/) did.
There are some other nice gems in there, but that's the gist of it.

Slightly differently, instead of sampling and projecting, we can also try to reparametrize our space such that all configurations that we sample are in the constrained space by definition.
This is what [ReVAMP](https://arxiv.org/pdf/2609.30213v1) is doing, again in a parallelized fashion.

#### Affine constraints

If we constrain ourself to only affine constraints, $$f(q)$$ will always have the form $$Aq - b = 0$$, or for inequalities $$Aq - b \leq 0$$, and the problem will become much simpler.
Particularly, the projection operations that we mentioned above become a lot simpler.
In some cases we do not even need to project samples, but we can directly sample from the constraint manifold.

Since this is what we'll look at in detail, I am not going to talk about the methods of linear projections here, but will do that a couple sections further down.

# Multi robot planning with multiple goals

Multi-robot multi-goal planning with can be written as a single big motion planning problem, where different constraints become active at various different times.

Until now (respectively in the previous paper), the only constraints we allowed were equality or set constraitns at single timesteps.
These constraints at the single timesteps are the mode switches, i.e., configurations or 'goals' that we have to pass through before being allowed to go to the next goal.
An example for this is that if we want to do a pick and place sequence, we first need to reach the configuration (the equality constraint) that 'grabs something', then we go to the configuration that 'places something'.
These examples already imply a relatively wide set of possible constraints.

If we are given these goal-constraints, the motion planning problem is then usually 'reach these goals in a certain order', in order to enable for example a 'pick and place' sequence of multiple robots, or to enable multiple robots stacking objects on top of each other.
To simplify some things, we are going to assume for now that we are only tackling settings where the order of goals we have to reach is fully given.

Importantly, these goal constraints are only for a subset of all robots: that means that different robots have different goals at the same time.
A simple example would be that robot 1 needs to pick object A before robot 2 picks object B.
Here, the constraint (or the goal-configuration) of robot 1 picking object A does not have any impact on robot 2, which can move freely.

# Introducing task-constraints to the problem

In the formulation we have here, introducing constraints is relatively straightforward for the problem formulation.
In addition to the setting before (i.e., having goal constraints), a task now simply contains any additional constraints that need to be respected _during that task_.
Additionally, there might be global constraints that we need to respect: it could be the case that some robots are coupled, or that we have two robot arms mounted on a shared base.
Linear inequality constraints could also be used to model more complex joint limits than just bounding boxes on each joint separately.

So the only thing we have to do is adding constraints to the tasks and any global constraints that might have to be respected at all times.
At planning time, we can then just look up in each mode what constraints have to be satisfied (all global constraints plus all constraints of all currently active tasks), and take those into account in our planner.

This alteration of the original problem is true both for nonlinear and linear consttraints, and also for equality and inequality constraints.

#### Multi robot planning problems with constraints

I am goign to give some examples for linear constraints here, and wht they enable.
I am already doing that with animations since this is making my life much easier.

- linked bar thing
- RFL
- husky

[images or gifs already]

#### Why do we need these constraints

Now, in a couple of these scenarios we only have the equality constraints due to a modeling choice we made: We choose to model two robot arms on a shared base as two separate robots, that are coupled through an equality constraint.

That means that we are introducing  the degrees of freedom of the base twice (or more times): for each robot once.

The question that you should ask here is 'why you would want to model these problems like that'?
After all, for a qhared base, you could simply model the problem such that you do only have the base once.
And the answer to this is largely historical, but I do also believe that through this modeling choice soem things become simpler thatn they would be compared to the more intuitive modelling choice.

Particularly, mode-switching behavior, and goal constraints for separate robots beceom a  more difficult to represenrt, respectively a there is a bit more bookkeeping involved.
Thsi is since mutliple robots would now share some of the degrees of freedom, and we would not have the clear assignment of robot indices to degrees of freedom anymore.
Again, to be clear, I think it would also be possible to do this the other way, but I believe that it would be more difficult.

- Each logical robot keeps its own configuration block, including a copy of any shared base joints. Equality constraints make these copies describe the same physical configuration; they do not introduce additional physical freedom.
- This fits the existing interfaces for robot assignments, partial goals, sampling, and shortcutting, which assume disjoint configuration blocks for different robots.
- A goal can refer to the working arm and its base without specifying the other arm's private joints. The shared base is still coupled: leaving the other arm free does not give it an independent base pose.
- With unique physical coordinates, several logical robots would refer to the same joint indices. That is possible, but operations such as freezing a robot, changing a subset, or checking conflicting goals would need explicit overlap handling.
- Global and mode-dependent constraints can use the same configuration layout. Eliminating constraints separately in each mode could instead require different coordinate maps, and bookkeeping when crossing a mode boundary. Permanent shared joints could still be eliminated once globally.
- Keeping the logical robot views also preserves the meaning of our current per-robot distances and path cost. A reduced representation could preserve these too, but simply replacing them with a Euclidean distance over unique joints would change the objective.

This is an implementation and bookkeeping choice, not a claim that the redundant formulation is fundamentally better. We could keep the external logical-robot interface while sampling unique physical coordinates internally and expanding them back into the redundant representation; informed sampling would still need to respect the original cost bound.

#### Planning with constraints

So now how do we solve this problem?
The answer is simple: We take the approach from above that works for constrained planning in the single goal setting, and add a bit of book-keeping to deal with the fact that the required constraints change over the different modes.

In our multi robot multi goal planner, we then project sampled configurations onto the subspace that the constraints encode.
The only difficulty is then keeping track of which constraints are active in which mode, and on which robots/indices of the full space.

So the devil is in the detail, which we already glanced over a bit above: We have to ask ourselves some questions that make annoyingly a lot of difference:

- How do we sample? Do we just sample uniformly random, or do we do something else? Can we reparametrize our space?
 - Should we do any kind of informed smapling? if so, how?
- If we can not reparameterize our constrained manifold, how do we actually project our samples?
- If we project, how?
  - iterative projection
  - orthogonal projection (penrose moore)
- Where in the algorithm do we project our samples?
- what do we do with inequality constraints?

Once we answered those questions, we are effectively done.
So this i swhat we are going to do now, but ot in the order above.

**Projection methots:** We do project our samples here after sampling uniformly first, since this is the most generic thing we can do, and this definitely works for all linear constraints that we can think of.

- The baseline we are looking at is a bit of overkill, but it is treating the equality constraint as QP, and using gradient descent to project onto the constraint.
- We then do somethign more sensible, and solve for the constraint directly.
- The we start doing fancier stuff: ...
- codex fill in keywords

**Informed smampling:** We do informed sampling after we have found a solution, and we do informed sampling by forst samping uniformly again, then projecting, and then rejcting samples that can not decrease the cost that we currently have.

**Inequality constraints:** Finally, we deal with inequality constraints agian by rejecting samples that do not fulfill them. An alternative woul dbe to project onto the boundary, but that has the problem that this would lead to a non-unifrom density, respectively to a high number of smaples _on_ the boundary.

#### Shortcutting with constraints
As a recap: shortcutting effectively replaces parts of an existing pth with a linear interpolation.

compared to constraint free motino planning, shortcutting becomes a bit more annoying in the case with general nonlinear constraints.
The fun realization that is going to make our live a lot easier for now is that a linear interpolation between two configurations that fulfill a linear constraint will always lead to a constraint fulfilling configuration as well, and the same is true for  inequality constraints.

so the only difficulty is in the end figuring out what we can shortcut, since soem degrees of freedom might be linked together through constraints.

and the other questino i sthen how we should actually shortcut.

# Benchmarking

We are first starting with a bit of a microbenchmark on the projections:

...

We are going to hve a look at shortcutting alone:

...

Next, we run the full planner with different projection methods.

...


# Take away

This problem formulation is nicely simple, and adding constraints is relatively easy.
What it boils down to is in the end a series o fdispatches to samples satisfying the various constraints, and orchestrating them.

For linear constraints these samplers are easy.
For non-linear constraints this will become a bit more annoying because ti changes how much time is spent in various parts of the algorithms.

#### Open questions

- weird cost functions
- clearly suboptimal
- problems tackled here make it clear that the goal-choice is very important
