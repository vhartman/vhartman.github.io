---
layout: post
title:  "Producing high quality paths: Partial shortcutting"
#subtitle: "Analyzing runtime of different post pro"
date:   2023-11-01 12:00:00 +0200
permalink: /partial-shortcutting/
categories: science research pathplanning
---

<p class="preface">
    Four years into my PhD, I start questioning if some of the things that I implemented in the beginning are actually good or if things could be done better.
    Better in this case is mostly related to 'faster'.
</p>

In path planning, a common approach is using a fast planner (often times RRT-Connect) that produces not so great results, and then using this as basis for further refinement.
Particularly, RRT-Connect (or most other sampling based solutions) produce very jagged paths, since the points that make out the path are randomly sampled{% include sidenote.html text='For a brief intro to how RRT-Connect works, see the [original paper](https://www.cs.cmu.edu/afs/cs/academic/class/15494-s12/readings/kuffner_icra2000.pdf), it is very approachable in my opinion.'%}.

There are a variety of methods{% include sidenote.html text='A [solid collection](https://ompl.kavrakilab.org/classompl_1_1geometric_1_1PathSimplifier.html) is implemented in OMPL.'%} to improve such a path after the initial planning - in this post, we are looking at shortcutting, respectively [partial shortcutting](https://journals.sagepub.com/doi/pdf/10.1177/0278364907079280?casa_token=myXrF9aYFUoAAAAA:_tqBBzr2VCL0X2n5vv8A7Bmxu6oNGsrMcjowsoeXPIid3xNjqlOlgJExtO1kkJi7i1YQZZj--RnE).

Code for the experiments and implementations is available [here](...).

#### Post-processing: (Partial) Shortcutting
In the following text, we assume that the path is given by a sequence of nodes which are connected by straightline paths{% include sidenote.html text='This is a great assumption if we are looking at robots that operate without kinodynamic constraints and we are doing geometric path planning. It is less great if we are looking at the dynamics of a robot as well.'%}.
A simple (but extremely effective) approach to post-process such a path is to shortcut it, that is, taking two (random) points on the path, and trying to connect them with a straight line, as illustrated below.

<div style="width: 90%; display: flex; justify-content: center; align-items: center; margin: auto;">
    <img src="{{ site.url }}/assets/shortcutting/illustration.png" style="width:70%; padding: 5px">
</div>

Here, the green shortcut is a valid one (since the new part of the path does not intersect with the obstacles), and the red shortcut is invalid (since it intersects one of the obstacles).
This procedure can be done either for a fixed number of iterations, or until some metric is satisfied.
In pseudocode, shortcutting looks like this:

```python
def interpolate(q0, q1, pts):
    edge = []
    for i in range(pts):
        edge[i] = q0 + (q1-q0) * i / pts
    return edge

def shortcut(path, max_iterations):
    for _ in range(max_iterations):
        # choose two random points
        i = rnd() % path.N
        j = rnd() % path.N

        edge = interpolate(path[i], path[j])
        if length(edge) < length(path[i:j]) and valid(edge):
            path[i:j] = edge
        
    return path
```

In many cases, this removes the redundant back and forth that is typical for a plan from a sampling based motion planner very effectively.
Having now covered the preliminaries, there are various variants of the proposed algorithm above, such as
- Path pruning, which only considers the discrete points (i.e. the dots in the example above), and not the intermediate configurations to choose places to cut (more formally described [here](https://ieeexplore.ieee.org/abstract/document/678449)).
- Instead of simply doing a strightline connection, one could run a local planner between two points as described  [here](https://ieeexplore.ieee.org/document/770365).
- shortcutting with an oracle [here](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=782972)
- Instead of randomly choosing points on the path, one can choose them deterministically (see [here](https://mediatum.ub.tum.de/doc/1290791/745347.pdf))
- [here](https://ai.stanford.edu/~mitul/thesis_saha.pdf)
- random once again [here](https://www.di.ens.fr/jean-paul.laumond/promotion/chap5.pdf)

An issue with normal shortcutting is that all dimensions are shortcut simultaneously.
This can lead to some redundant motion that can not be shortcutted.
Specifically, this can occur if shortcutting another dimension of the path can not be shortcutted.

A nice example for this is in the figure below (from the original paper linked above), where a robot with an orientation and a 2d position is used.
The rotational-component of the path can not be changed in this example, since the positional component can not be shortcutted.

<div style="width: 90%; display: flex; justify-content: center; align-items: center; margin: auto;">
    <img src="{{ site.url }}/assets/shortcutting/partial_shortcut.png" style="width:70%; padding: 5px">
</div>

A solution to this problem is shortcutting each dimension separately as seen above on the rightmost illustration, where only the rotational-dimension is shortcut, but the other two dimensions follow the same path from the original solution.

```python
def interpolate_subset(q0, q1, index):
    return []

def shortcut(path, max_iterations):
    for _ in range(max_iterations):
        # choose two random points
        i = rnd() % path.N
        j = rnd() % path.N
        dim = rnd() % path[0].N

        edge = interpolate_subset(path[i], path[j], dim)
        if length(edge) < length(path[i:j]) and valid(edge):
            path[i:j] = edge
        
    return path
```

However, while this usually leads to a shorter final path, this approach might take many more iterations for the same shortcut in case a shortcut is actually feasible for all dimensions at the same time.
For this reason{% include sidenote.html text='And possibly some misunderstanding/misremembering of the actually proposed method'%}, at the beginning of my PhD, I implemented a method that randomly samples a set of indices from the dimensions to shortcut, and then shortcuts those indices:

```python
def interpolate_subset(q0, q1, index):
    return []

def shortcut(path, max_iterations):
    for _ in range(max_iterations):
        # choose two random points
        i = rnd() % path.N
        j = rnd() % path.N

        num_indices = rnd() % path[0].N
        indices = []

        edge = interpolate_subset(path[i], path[j], indices)
        if length(edge) < length(path[i:j]) and valid(edge):
            path[i:j] = edge
        
    return path
```

I recently stumbled upon the original paper again, and wanted to double check how my implementation performs against the one that is originally proposed in the paper.
I am mostly interested in convergence of the method, repsectively computation speed.

#### Experiments
The methods that we will compare are a selection of the things above:
- pruning
- shortcutting
- partial shortcutting (with a single dimension at a time)
- partial shortcutting (with a random subset of dimensions)

I run all the methods on a few different scenarios, and report the results below.
For each of the scenarios, I used RRT-Connect to produce an initial path, and then run the methods above to postprocess the path.

Since I am mostly interested in manipulation planning, the scenarios I am using are from previous papers of mine, and will contain things to be manipulated.
Particularly, I am going to be looking at multiple paths in the same environment, where the agent is moving things around (e.g. a path that leads to a robot picking something up and a path that leads to some placement position).

Conretely, the scenarios are i) a simple 2d scenario with obstacles where a 'sofa' has to be moved through a narrow corridor, ii) a robotic manipulator on a table with a bunch of objects lying around, one of which has to be moved and iii) a mobile manipulator that has to move an actual table to a different room{% include sidenote.html text='Obviously, this is not a perfect test of the methods, but my intuition tells me that this should paint a sufficient picture.'%}:

<div style="width: 90%; display: flex; justify-content: center; align-items: center; margin: auto;">
  <div style="width: 25%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/scenes/sofa_0.png" style="width:100%;">
  </div>
  <div style="width: 25%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/scenes/handover_0.png" style="width:100%;">
  </div>
  <div style="width: 25%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/scenes/move_table_0.png" style="width:100%;">
  </div>
</div>

As example, for the 2d-setting, the initial path, and the shortcutted paths look like this:

[images]

Below, I plot the path length against the compute time.
I ran all the shortcutters 50 times.
The thick line is the median of all runs for that specific method and the shaded area in the same color is the 95% non-parametric confidence interval.

<div style="width: 90%; display: flex; justify-content: center; align-items: center; margin: auto;">
  <div style="width: 50%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/sofa_0_20231111_131031.png" style="width:100%;">
  </div>
  <div style="width: 50%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/sofa_1_20231111_131031.png" style="width:100%;">
  </div>
</div>

<div style="width: 90%; display: flex; justify-content: center; align-items: center; margin: auto;">
  <div style="width: 52%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/Handover_0_20231111_131218.png" style="width:100%;">
  </div>
  <div style="width: 50%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/Handover_1_20231111_131218.png" style="width:100%;">
  </div>
</div>

<div style="width: 90%; display: flex; justify-content: center; align-items: center; margin: auto;">
  <div style="width: 52%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/MoveTable_0_20231111_174024.png" style="width:100%;">
  </div>
  <div style="width: 50%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/MoveTable_1_20231111_174024.png" style="width:100%;">
  </div>
</div>

The first thing to notice is that the plots above are very different from the ones shown in the original paper.
Partial shortcutting with only a single dimension seems to be slower then normal shortcutting in quite a few of the cases.
This might have to do with the type of problem we are looking at though.
When focussing on the experiments (a) and (f) of the original paper (a planar corridor, and a manipulator), a similar effect can be seen as the one we have here.

In the plots above, the subset-shortcutter is consistently the fastest and finds the shortest paths.
Further, the expected effect appears for the shortcutting and the pruning, namely thtat they do not get the path length as low as the other two approaches.

#### Ablations
In additon to the experiments above, I wanted to add a few ablations that show which things matter, respectively things that I learned during these experiments.

The first one is **how we discretize a path**: Since we want to look not only at the corners of the path for shortcutting, we typically discretize the edges between them more finely, such that we can simply sample random indiceds for shortcutting afterwards.

However, there is a conflict with collision checking when discretizing the path.
Collision checking of a path typically works by discretizing the path into some defined resolution, and then collision checking these states.
Now, if the path is _too finely_ discretized (finer than the collision checking resolution), this leads to many more collision checks that are done on the path compared to only checking at a certain resolution.

The following two plots are with different ways of discretizing a path:

<div style="width: 90%; display: flex; justify-content: center; align-items: center; margin: auto;">
  <div style="width: 52%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/MoveTable_0_20231111_174024.png" style="width:100%;">
  </div>
  <div style="width: 50%; padding: 5px;">
    <img src="{{ site.url }}/assets/shortcutting/exp/MoveTable_1_20231111_174024.png" style="width:100%;">
  </div>
</div>

#### Takeways
Clearly, there are a few things that one should keep in mind when implementing shortcutting.
The thing that surprised me the most (but should be obvious) is that a too fine discretization can lead to unintended problems (your shortcutter being very slow).

The second thing is that the subset-shortcutting seems to be quite a bit better than the single-dimension shortcutting on the scenarios that I care about most, and the performance seems to be similar to the one from the shortuctter that always gors for the full set of indices.

#### Outlook
Clearly, there are a number of design choices in all the implementations above - the choices range from what to sample, what distributions to sample from, which order to sample things in and so on.
It is questionable if those design choices represent some sort of optimum.
A thing to do then might be to try to find optimal distributions that we sample things from.

Additionally, there are some thigs that can clearly be optimized.
If we do shortcutting for only a single dimension, that only changes some of the parts of the robot we are looking at.
Thus, we might be able to save some time by only collision checking the parts of the robot that actually changed.

Next, there are a number of things that could be cached here, to avoid e.g., attempting to (unsuccessfully!) shortcut the same thing twice.

Finally, it would be interesting to collect some metrics on where time is spent.
From experience, the most time is usually taken by the _valid_ edges (since the validation-attempt of invalid edges typically terminates earlier).
From this follows that it would be desirable to avoid the 'incremental' improvements, and ideally try to find the big improvements first.
