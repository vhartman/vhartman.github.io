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
It is important to note here that I do want to compute this number for many different configurations $$q$$, so clearly I want to batch this computation{% include sidenote.html text="In the very initial version of the function computing these values, I did actually not batch this. Batching this computation made a huge difference, but we start from the batched version as baseline here."%}.

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

Additionally to this, we should distinguish in our function if we are computing a one-to-many distance, or if we are doing many-to-many distances{% include sidenote.html text="Due to legacy code choices, that will be changed as result of this experiment."%}.

Code for everything can be found [here](https://github.com/vhartman/sliced-dist-bench), and more plots for different dimensions etc. can be found [here](https://github.com/vhartman/sliced-dist-bench/tree/master/final_plots).

# Baseline

We add some logic to decide what we need to compute depending on the function parameters, and translate the formulas above into code using all the numpy functions that make our life quite easy {% include sidenote.html text='We are only going to benchmark the one-to-many setting here. In the other setting, the conversion to a numpy array is a very slow part, and I do not know how to deal with this without a more significant change.'%}:

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
        for i, (s, e) in enumerate(starts.array_slice):
            all_robot_dists[i, :] = np.linalg.norm(diff[:, s:e], axis=1)
    else:
        for i, (s, e) in enumerate(agent_slices):
            all_robot_dists[i, :] = np.max(np.abs(diff[:, s:e]), axis=1)

    if reduction == "max":
        return np.max(all_robot_dists, axis=0) + w * np.sum(all_robot_dists, axis=0)
    elif reduction == "sum":
        return np.sum(all_robot_dists, axis=0)
```

We need to take some care that we aggregate over the correct axes, but other than that, this code is relatively straightforward.

You might argue now that the way that I choose here for the representation for the multi-robot configuration does not make sense, and you could make the whole thing better (more amenable to numpy/vectorization) by representing a single multi robot configuration as 2 dimensional array, where you have one configuration per robot.
The collection of multiple robots would then become a 3 dimensional array, and the only thing that yo'd need to do is to let your operations run over the correct axes.

And I'd love to do this! But unfortunately, my robots can all have different configuration spaces with various dimensionalities, and numpy does apparently not really like ragged arrays.
So at least for now, we are doing the linear layout (i.e., simply stacking all the single robot configurations), and deal with the slicing of the configuration.

In addition to the code above, I am also running a version that 'manually' copmutes the euclidean distance via `sqrt(sum(x^2))`, since I read something on stackoverflow that there is a chance that this is faster in certain cases.

We'll run this for different numbers of points, and different dimensionalities of slices, and plot the runtime vs the number of points in a batch.
We'll do this both for the sum and for the max aggregation, resulting in the following curves for our baseline{% include sidenote.html text="Since this is part of [the work on multi-robot planning](/mrmg-planning/), I am doing the testing and benchmarking using pytest and pytest-benchmark, as this is what I am using there."%}{% include sidenote.html text='I will  show the curves for a system with 2 agents each having 7 DoF, and one with 3 agents each having 3 DoF. The sum and max graphs look roughly similar, and are very straighforward to produce using the code linked above.'%}:

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/sliced-dists/baseline/sum_3_3_3.png" style="width:45%; padding: 10px">
  <img src="{{ site.url }}/assets/sliced-dists/baseline/sum_7_7.png" style="width:45%; padding: 10px">
</div>

We can see that the 'manual' sum-of-squares computation is actually faster than using the numpy norm.
Even though this is not slow on an absolute scale, in the motion planning pipeline, this made up for a majority of the runtime, since this is called very often in some of the subroutines.
Running cProfile on the code above shows that computing the euclidean distance over the slices is most time consuming, and we'll first focus on this part.

#### Speeding up the euclidean distance over slices

As first attempt to speed this up, we'll just take the thing as a whole and jit it using numba.
There are a few small things we need to do, since numba does not like some of the things we did so far, i.e., the numba version I am using does not like the axis-argument in the max/sum function.

```python
@numba.jit((numba.float64[:, :], numba.int64[:, :]), nopython=True, fastmath=True)
def compute_sliced_dists(squared_diff: NDArray, slices: NDArray) -> NDArray:
    num_slices = len(slices)
    num_samples = squared_diff.shape[0]
    dists = np.empty((num_slices, num_samples), dtype=np.float64)

    for i in range(num_slices):
        s, e = slices[i]
        dists[i, :] = np.sqrt(np.sum(squared_diff[:, s:e], axis=1))

    return dists
```

This results in the following curve, already giving a sizeable speedup.

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/sliced-dists/naive_numba/sum_3_3_3.png" style="width:45%; padding: 10px">
  <img src="{{ site.url }}/assets/sliced-dists/naive_numba/sum_7_7.png" style="width:45%; padding: 10px">
</div>

This speedup is (was) already enough together with the batching to not make this part of the code the bottleneck anymore at the time.
However, we are now in the rabbithole of trying to optimize this as much as possible, so we go on.

We can try to parallelize this, instead of only hoping that numba will vectorize this nicely (since I would have assumed initially that numpy code is vectorized itself - we don't trust this stuff anymore now.):

```python
@numba.jit((numba.float64[:, :], numba.int64[:, :]), nopython=True, parallel=True)
def numba_parallelized_sum(
    squared_diff: NDArray, slices: NDArray
) -> NDArray:
    num_agents = len(slices)
    dists = np.zeros((num_agents, squared_diff.shape[0]))

    for i in numba.prange(num_agents):
        s, e = slices[i]
        dists[i, :] = np.sqrt(np.sum(squared_diff[:, s:e], axis=1))

    return dists
```

Sadly, this did not work well:

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/sliced-dists/parallel/sum_3_3_3.png" style="width:45%; padding: 10px">
  <img src="{{ site.url }}/assets/sliced-dists/parallel/sum_7_7.png" style="width:45%; padding: 10px">
</div>

I do not have a great explanation, but I am assuming that the overhead of using prange/the overhead of parallelization is simply not worth it given that the operations that are being executed in parallel are relatively quick itself.
It might also be the case that this only starts making sense once you have many more agents (but in the settings I care about for the moment, you'll never deal with more than ~4-6 agents).
My final guess is that it might simply not work well on my CPU.

We can also see thath the error bars of the timing of the parallelized runs are all over the place, suggesting that there might simply be impact from other things running at the same time.

We can still do better for the sliced distance by rewriting the jitted function a bit.
For some reason, getting rid of numpy, and writing the loop for the sum of squares manually gives a speedup for us here:

```python
@numba.jit((numba.float64[:, :], numba.int64[:, :]), nopython=True, fastmath=True, parallel=True)
def compute_sliced_dists_naive_unrolled(squared_diff: NDArray, slices: NDArray) -> NDArray:
    """Compute Euclidean distances for sliced configurations with optimizations."""
    num_slices = len(slices)
    num_samples = squared_diff.shape[0]
    dists = np.empty((num_slices, num_samples), dtype=np.float64)

    # Process each slice independently
    for i in range(num_slices):
        s, e = slices[i]
        slice_width = e - s

        # Optimize the inner loop for better vectorization and cache usage
        for j in range(num_samples):
            sum_squared = 0.0
            # For larger slices, use a regular loop which Numba can vectorize
            for k in range(s, e):
                sum_squared += squared_diff[j, k]

            dists[i, j] = np.sqrt(sum_squared)

    return dists
```

And the corresponding curves:

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/sliced-dists/unrolled/sum_3_3_3.png" style="width:45%; padding: 10px">
  <img src="{{ site.url }}/assets/sliced-dists/unrolled/sum_7_7.png" style="width:45%; padding: 10px">
</div>

The final thing we'll have a look at is the fact that we computed the squared difference outside of the numba code so far.
Until now, I did believe that at least multiplying is fast in numpy.
But moving the computation of the squared distances into the jitted function gives us another speedup.
I do however believe that this is largely since this gets rid of a big chunk of memory allocation.
With this, the code currently looks like this:

```python
@numba.jit((numba.float64[:, :], numba.int64[:, :]), nopython=True, fastmath=True, parallel=True)
def compute_sliced_dists_naive_unrolled_non_squared(diff: NDArray, slices: NDArray) -> NDArray:
    """Compute Euclidean distances for sliced configurations with optimizations."""
    num_slices = len(slices)
    num_samples = diff.shape[0]
    dists = np.empty((num_slices, num_samples), dtype=np.float64)

    # Process each slice independently
    for i in range(num_slices):
        s, e = slices[i]
        slice_width = e - s

        # Optimize the inner loop for better vectorization and cache usage
        for j in range(num_samples):
            sum_squared = 0.0
            for k in range(s, e):
                sum_squared += diff[j, k] * diff[j, k]

            dists[i, j] = np.sqrt(sum_squared)

    return dists
```

with this performance:

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/sliced-dists/unrolled_no_square/sum_3_3_3.png" style="width:45%; padding: 10px">
  <img src="{{ site.url }}/assets/sliced-dists/unrolled_no_square/sum_7_7.png" style="width:45%; padding: 10px">
</div>

which is a decent speedup compared to the previous version when dealing with large batches and 'large' slices (on the right).

#### Speeding up the sum and max reductions
So far, we optimized the per-agent-metric-computation, and did not touch the aggregation.
With all the optimizations we did now, cProfile shows that the `sum` and the `max` are now a large part of the total computation time.

Since we were succesful with numba before, why change the receipe? Since we have two different possible reductions, we have the sum reduction:

```python
@numba.jit(numba.float64[:](numba.float64[:, :]), nopython=True, fastmath=True)
def compute_sum_reduction(dists: NDArray) -> NDArray:
    """Compute sum reduction across robot distances."""
    num_slices, num_samples = dists.shape
    result = np.empty(num_samples, dtype=np.float64)

    # Manually compute sum along axis 0
    for j in range(num_samples):
        sum_val = 0.0
        for i in range(num_slices):
            sum_val += dists[i, j]
        result[j] = sum_val

    return result

```

And the max reduction:

```python
@numba.jit(
    numba.float64[:](numba.float64[:, :], numba.float64), nopython=True, fastmath=True
)
def compute_max_sum_reduction(dists: NDArray, w: float) -> NDArray:
    """Compute max + w*sum reduction across robot distances."""
    num_slices, num_samples = dists.shape
    result = np.empty(num_samples, dtype=np.float64)

    # Manually compute max along axis 0
    for j in range(num_samples):
        max_val = dists[0, j]
        sum_val = dists[0, j]
        for i in range(1, num_slices):
            if dists[i, j] > max_val:
                max_val = dists[i, j]
            sum_val += dists[i, j]
        result[j] = max_val + w * sum_val

    return result
```

Introducing this now brings down the performance a bit more:

<div style="width: 100%;margin:auto; text-align: center;">
  <img src="{{ site.url }}/assets/sliced-dists/numba_reduction/sum_3_3_3.png" style="width:45%; padding: 10px">
  <img src="{{ site.url }}/assets/sliced-dists/numba_reduction/sum_7_7.png" style="width:45%; padding: 10px">
</div>

And this is the point where I am stopping now.
I am sure that the point where I should have switched to a C++ implementation was crossed a long time ago, but I unfortunately started the multi robot planning project with python, and I am too deep in now to switch.

I also fully believe that there is still a bit of potential left by ensuring that the array layout is fine (i.e., that we are summing over the fast running axis.), but these computations are now by far not the botleneck anymore.

Another thing to optimize now would be avoiding the branching in the function itself, and just specialize each function - this would e.g. allow to just run the max over the whole array once, instead of once for the metric and once for the reduction.

# Conclusion
I guess my takeaway here is that you should not always blindly believe the default options to be the fastest.
There are many places where people will just tell you that numpy clearly is the fastest - and it likely is in most cases!
But in reality this is extremely dependent on your array sizes and the workload in general.

The other problem that still exists can be found in the many to many dist/cost computation: the creation of the array from the list of states.

I did try to experiment a bit with preallocation of arrays, and seeing if this makes life easier, but it did not change much at the time.

This points to an issue that is rooted a bit more deeply in the design choices that I made: There must be a better way to ensure that the configurations that I am creating are more easily accessible than they are currently when stored in this list format.