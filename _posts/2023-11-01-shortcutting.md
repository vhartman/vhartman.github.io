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
In the following text, we assume that the path is given by a sequence of nodes which are connected by straightline paths.
A simple (but extremely effective) approach to post-process such a path is to shortcut it, that is, taking two (random) points on the path, and trying to connect them with a straight line, as illustrated below.

[illustration]

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
- Path pruning, which only considers the discrete points, and not the intermediate configurations to choose places to cut [here](https://ieeexplore.ieee.org/abstract/document/678449).
- running a local planner between two points [here](https://ieeexplore.ieee.org/document/770365).
- shortcutting with an oracle [here](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=782972)
- deterministic choice of configurations [here](https://mediatum.ub.tum.de/doc/1290791/745347.pdf)
- [here](https://ai.stanford.edu/~mitul/thesis_saha.pdf)
- random once again [here](https://www.di.ens.fr/jean-paul.laumond/promotion/chap5.pdf)

An issue with normal shortcutting is that all dimensions are shortcut simultaneously.
This can lead to some redundant motion that can not be shortcutted.
Specifically, this can occur if shortcutting another dimension of the path can not be shortcutted.

A nice example for this is in the figure below (from the original paper linked above), where a robot with an orientation and a 2d position is used.
The rotational-component of the path can not be changed in this example, since the positional component can not be shortcutted.

<div style="width: 90%;margin:auto">
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

I recently stumbled upon the original paper again, and wanted to double check how my implementatoin performs against the one that is originally proposed in the paper.
I am mostly interested in convergence of the method, repsectively computation speed.

#### Experiments
The methods that we will be looking at are:
- pruning
- shortcutting
- partial shortcutting (single dimensions)
- partial shortcutting (random subset of dimensions)

I run all the methods on a few different scenarios, and report the results below.
For each of the scenarios, I will run RRT-Connect to produce an initial path, and then run the methods above to shortcut the path.

The scenarios we are looking at are i) a simple 2d scenario with obstacles, ii) a robotic manipulator on a table with a bunch of objects lying around and iii) a mobile manipulator in a building construction scenario{% include sidenote.html text='Obviously, this is not a perfect test of the methods, but my intuition tells me that this should paint a sufficient picture.'%}:

[images]

As example, for the 2d-setting, the initial path, and the shortcutted paths look like this:

[images]

Below, I plot the path length against the number of iterations, and against the compute time.

[plots]

Above, we can see that ...

#### Results
..

#### Outlook
Clearly, there are a number of design choices in all the implementations above - the choices range from what to sample, what distributions to sample from, which order to sample things in and so on.
It is questionable if those design choices represent some sort of optimum.

There are some obvious things:
- only colliison check what is necessary.
- find the optimal distribution to sample indices from
