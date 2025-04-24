---
layout: post
title:  "So you think numpy is always the fastest?"
subtitle: "or: How to best compute sums of euclidean distances."
date:   2025-04-20 12:00:00 +0200
permalink: /fast-numpy-aggregation/
categories: numerics path-planning science
---

<p class="preface">
In multi robot planning, you'll need to compute some cost or distance at some point. Depending on how you represent a configuration, this might require different sequences of operations. <br>
In my case, I have an n-dimensional array, and I want to compute the euclidean distance over a set of (non-overlapping) slices, and then take the sum or the max of the separate values.

You'd think that just doing this with generic numpy operations is always the fastest approach. <br><br>
Spoiler: You would be wrong.
</p>

This post is motivated by my recent work on multi-robot multi-goal motion planning, where to decide what is a good path, we want to compute a cost or a distance that depends on multiple robots, and their respective poses.

Concretely, I want to compute

$$
c(q_1, q_2) =  w\sum_{i\in R} ||q_1^i - q_2^i||_2 + (1-w)\max_{i\in R} ||q_1^i - q_2^i||_2
$$

where $$q_1 = [q_1^1 ... q_1^R]$$, and the same for $$q_2$$.
It is important to note here that I do want to compute this number for many different configurations $$q$$, so clearly I want to batch this computation {% include sidenote.html text="In the very initial version of the function computing these values, I did actually not batch this. Batching this computation made a huge difference, but we start from the batched version as baseline here."%}.

In the general case, we also don't always use the euclidean norm as single-robot metric (i.e., as the inner part of the computation), but sometimes want to use a more general L-p norm. 
In the following experiments, we consider two cases, the euclidean norm, and the maximum of the absolute values, i.e. the inf-norm:

$$
c(q_1, q_2) =  w\sum_{i\in R} \max_j|q_1^{i,j} - q_2^{i,j}| + (1-w)\max_{i\in R} \max_j|q_1^{i,j} - q_2^{i,j}|
$$

So in total, there's four possible combinations of things that we might need to compute:

- metric: euclidean, reduction: sum
- metric: abs max, reduction: sum
- metric: euclidean, reduction: max
- metric: abs max, reduction: max

Additionally to this, we should distinguish in our function if we are computing a one-to-many distance, or if we are doing many-to-many distances{% include sidenote.html text="Due to legacy code choices, that will b changed as result of this experiment."%}.

Code for everything can be found [here](https://github.com/vhartman/nu-nmpc/tree/blog_version).

# Baseline

We add some logic to decide what we need to compute depending on the function parameters, and translate the formulas above into code using all the numpy functions that make our life quite easy:

```python
def batch_config_cost(
    starts: List[Configuration],
    batch_other: List[Configuration],
    metric: str = "max",
    reduction: str = "max",
    w: float = 0.01,
) -> NDArray:
    if isinstance(starts, Configuration) and isinstance(batch_other, np.ndarray):
        diff = starts.state() - batch_other
        all_robot_dists = np.zeros((starts._num_agents, diff.shape[0]))
        agent_slices = starts.array_slice
    else:
        diff = np.array([start.q.state() for start in starts]) - np.array(
            [other.q.state() for other in batch_other], dtype=np.float64
        )
        all_robot_dists = np.zeros((starts[0].q._num_agents, diff.shape[0]))
        agent_slices = starts[0].q.array_slice

    if metric == "euclidean":
        all_robot_dists = np.zeros((starts._num_agents, diff.shape[0]))

        squared_diff = diff * diff
        for i, (s, e) in enumerate(starts.array_slice):
            # Use sqrt(sum(x^2)) instead of np.linalg.norm
            # and pre-computed squared differences
            all_robot_dists[i, :] = np.sqrt(np.sum(squared_diff[:, s:e], axis=1))
    else:
        for i, (s, e) in enumerate(agent_slices):
            all_robot_dists[i, :] = np.max(np.abs(diff[:, s:e]), axis=1)

    if reduction == "max":
        return np.max(all_robot_dists, axis=0) + w * np.sum(all_robot_dists, axis=0)
    elif reduction == "sum":
        return np.sum(all_robot_dists, axis=0)
```

We need to take some care that we aggregate over the correct axes, but other than that, this code is relatively straightforward.

You might argue now that the way that I choose here for the multi-robot configuration does not make sense, and you could make the whole thing better (more amenable to numpy/vectorization) by representing a single multi robot configuration as 2 dimensional array, where you have one configuration per robot.
The collection of multiple robots would then become a 3 dimensional array, and the only thing that yo'd need to do is to let your ooperations run over the correct axes.

And I'd love to do this! But unfortunately, my robots can all have different configuration spaces, and numpy does apparently not really like ragged arrays.
So at least for now, we are doing the linear layout (i.e., simply stacking all the single robot configurations), and deal with the slicing of the configuration.

Since this is part of [the work on multi-robot planning](/mrmg-planning/), I am doing the testing and benchmarking using pytest and pytest-benchmark.
We'll run this for different numbers of points, and different dimensionalities of slices, and plot the runtime vs the number of points in a batch.
We'll run this both for the sum and for the max aggregation, resulting in the following curves:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_5.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_10.png" style="width:29%; padding: 10px">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_20.png" style="width:29%; padding: 10px">
  <figcaption><span style="color: #1f77b4;">Blue</span> is position, <span style="color: #ff7f0e;">orange</span> is velocity, and <span style="color: #2ca02c;">green</span> is acceleration. The constraints for each variable are shown in the corresponding color.</figcaption>
</div>

Even though this is not slow on an absolute scale, in the motion planning pipeline, this made up for a majority of the runtime, since this is called very often in some of the subroutines.

# Einsum?

# Enter: numba
Running cProfile on this whole thing shows that computing the euclidean distance over the slices is most problematic, and we'll first focus on this part.

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_20.png" style="width:29%; padding: 10px">
  <figcaption>The flamegraph corrsponding to the baseline version.</figcaption>
</div>

#### Speeding up the euclidean distance over slices

As first attempt to speed this up, we'll just take the thing as a whole and jit it using numba.
There are a few small things we need to do, since numba does not like some of the things we did so far, i.e., the numba version I am using does not like the axis-argument in the max/sum function.

```python
@jit
def compute_sliced_euclidean_dists():
  pass
```

This results in the following curve, already giving a sizeable speedup.
This speedup is (was) already enough to not make this part of the code the bottleneck anymore at the time.
However, we are now in the rabbithole of trying to optimize this as much as possible, so we go on.

We can try to parallelize this:

```python
@jit
def parallel_compute_sliced_euclidean_dists():
  pass
```

Sadly, this did not work. 
I do not have a great explanation, but I am assuming that the overhead of using prange/the overhead of parallelization is simply not worth it given that the operations that are being executed in parallel are relatively quick itself.

We can still do better for the sliced distance by rewriting the jitted function a bit.
For some reason, unrolling the loop gives a speedup for us here:

```python
@jit
def unrolled_compute_sliced_euclidean_dists():
  pass
```

And the corresponding curves:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_20.png" style="width:29%; padding: 10px">
  <figcaption>The flamegraph corrsponding to the baseline version.</figcaption>
</div>

Finally, until now, I did believe that at least multiplying is fast in numpy.
But moving the computation of the squared distances into the jitted function gives us another speedup.
I do however believe that this is largely since this gets rid of a big chunk of memory allocation.
With this, the code currently looks like this:

```python
@jit
def unrolled_compute_sliced_euclidean_dists():
  pass
```

with this performance:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_20.png" style="width:29%; padding: 10px">
  <figcaption>The flamegraph corrsponding to the baseline version.</figcaption>
</div>

#### Speeding up the sum and max reductions
So far, we optimized the per-agent-metric-computation, and did not touch the aggregation.
With all the optimizations we did now, cProfile shows that the `sum` and the `max` are now a large part of the total computation time.

Since we were succesful with numba before, why change the receipe? Here we go:

```python
def compute_sum_max_reduction():
  pass

def compute_max_reduction():
  pass
```

Curves:

<div style="width: 90%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/nu_mpc/lin_sys_n_20.png" style="width:29%; padding: 10px">
  <figcaption>The flamegraph corrsponding to the baseline version.</figcaption>
</div>

And this is the point where I am stopping now.
I am sure that the point where I should have switched to a C++ implementation was crossed a long time ago, but I unfortunately started the multi robot planning project with python, and I am too deep in now to switch.

I also fully believe that there is still a bit of potential left by ensuring that the array layout is fine (i.e., that we are summing over the fast running axis.), but these computations are now by far not the botleneck anymore.

Another thing to optimize now would be avoiding the branching in the function itself, and just specialize each function - this would e.g. allow to just run the max over the whole array once, instead of once for the metric and once for the reduction.

# Conclusion
I guess my takeaway here is that you should not always blindly believe the default options to be the fastest.
There are many places where people will just tell you that numpy clearly is the fastest - and it likely is in most cases!
But in reality this is extremely dependent on your array sizes and the workload in general.