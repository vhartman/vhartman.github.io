---
layout: post
title:  "A collection of parallel and performant algorithms (in robotics)"
date:   2024-07-12 12:00:00 +0200
permalink: /simd-collection/
categories: performance
---

<p class="preface">
    There was a paper a bit ago that presents a really fast motion planner, using amongst other things SIMD programming for collision checking of edges (which is usually the most time intensive step in motion planning for robots).
    This got me more into SIMD programming, and hoarding a handful of links related to high-performing implementations of common robotics algorithms.
    This post is me closing a bunch of tabs and archiving their content here in case I'll need it again. 
</p>

The paper/preprint in question is the one [here](https://arxiv.org/pdf/2309.14545.pdf) by [Zak](https://zkingston.com/) and [Wil](https://wbthomason.github.io/).
They present a really fast approach for motion planning, and have open sourced its implementation [here](https://github.com/KavrakiLab/vamp).
One of the things that they leverage is the parallelization of collision checking, which they call fine-grained collision checking.
Compared to 'traditional' parallelization over multiple cores, they do parallel collision checking using vectorization with SIMD.

Since they took a while to open-source their code, I made some experiments myself, which is in very rough shape, but can be found [on github](https://github.com/vhartman/simd-experiments).
This shows a ~10x speedup on 2D collision checking (albeit not demoed in a motion planning setting).

In the rest of the note, I want to organize a few links on SIMD blog-posts, posts on how to achieve high performance implementations of various algorithms (matmul for example), and a large part of robotics papers/algorithms.

#### Generic cool performance related literature
- A while ago there was a discussion on hackernews of an old (2011) post on [SIMD vs SIMT vs SMT](https://yosefk.com/blog/simd-simt-smt-parallelism-in-nvidia-gpus.html). However, the consensus seems to be that quite a lot of things have changed since then, and the differences between the different programming models are not as distinguished anymore since the three different approaches borrowed many things from each other.
- [Here's](https://mcyoung.xyz/2023/11/27/simd-base64/) a great walkthrough of transitioning an algorithm implemented normally to SIMD-code. There is a nice intro to what SIMD programming actually is, and why it is faster than 'normal' code.
- Here's an overview of how [teaching of parallel programming](https://tcpp.cs.gsu.edu/curriculum/sites/default/files/EduPar-02-Teaching_Parallel_Optimization_for_Robotics__EduPar_2024__Final.pdf) is done by Brian Plancher, a robotics professor at Columbia.
- This list would not be complete without the [intel intrinsic guide](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html) or [agner fogs optimization resources](https://agner.org/optimize/) which are both crucial resources for anyone trying to get started with SIMD programming (or code optimizations in general).
- I also found [this simd tutorial](https://fabiensanglard.net/revisiting_the_pathtracer/SIMD_Tutorial.pdf) useful.
- Finally, [here is a great writeup of how to achieve fast matmul in cpp on a cpu](https://salykova.github.io/matmul-cpu).
- And here is something similar for [optimizing a kernel for matmul on a GPU](https://siboehm.com/articles/22/CUDA-MMM).

#### Robotics related literature (papers)

**Planning: Sampling based and trajectory optimization**
- [Clayton W. Ramsey](https://claytonwramsey.com/), Wil and Zak had [another paper](https://arxiv.org/abs/2406.02807) on cache/parallelization friendly nearest neighbor structures. There is also [a blog post](https://claytonwramsey.com/blog/captree) on its contents.
- Brian Placher (the same as above) and gang have a paper on a [parallel implementation of DDP](https://a2r-lab.org/files/GPU_DDP_WAFR_paper.pdf). It is parallel on various granularities, i.e. on an algorithmic level (leveraging gauss newton multiple shooting), and also on an implementation level. Their conclusion is that the parallelizations they analyzed can help achieve faster convergence in some cases, but how well it works i sheavily dependent on the problem.
- The paper [here proposes a parallel version of something similar to rrt](https://ieeexplore.ieee.org/abstract/document/7926542), and achieves fast planing times. The paper is from 2017, and the paper from Wil and Zak proposes a much faster planner.
- [cuRobo from nvidia](https://curobo.org/reports/curobo_report.pdf) is a collection of various things to achieve good motion planning times. The report is quite interesting to read. At the time of writing, cuRobo does not work for more than two robots, and is only doing motion planning.
- [Motion planing templates](https://ieeexplore.ieee.org/abstract/document/8794099) is a paper suggesting templated motion planning in order to be able to specialize to specific robot geometries at compile time. It is from [Brian Ichnowski](https://ichnow.ski/) who is generally doing cool things in robotics.
 
**Control**
- [Gauss Newton multiple shooting](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8593840) is a combination of dynamic programming and multiple shooting, which allows parallelization of the algorithm. This is the paper that introduces the algorithm level parallelization used in the DDP paper above.
- [MPPI](https://arc.aiaa.org/doi/epdf/10.2514/1.G001921) is a method that relies on sampling noise, using it as control input to a dynamic system and rolling it out over a certain prediction-horizon. [Here](https://sites.gatech.edu/acds/mppi/) is a collection of research contributions from Gatech.
- [MPPI is implemented on a GPU for robot locomotion](https://arxiv.org/pdf/2403.11383), or [for aggressive driving](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7487277)
- [Accelerating Robot Dynamics Gradients on a CPU, GPU, and FPGA](https://people.csail.mit.edu/bthom/icra21.pdf)
- Nvidia has more work on implementing things on GPUs, here with the example of running MPPI [on a gpu](https://arxiv.org/abs/2104.13542) for manipulation, called STORM.
- [Tinympc](https://tinympc.org/) is an MPC solver for embedded systems, that also has [codegeneration](https://arxiv.org/abs/2403.18149) capabilities.
- [Real time iterations with MPC](https://cse.lab.imtlucca.it/~bemporad/publications/papers/ijc_rtiltv.pdf) is a core contribution that shows how to apply (nonlinear) MPC in reality, by only doing a few iterations at a time, and therefore guaranteeing compute times of the control algorithm.

**Optimizers**
For many robotics applications, optimizers are _very_ important.
- [OSQP](https://osqp.org/docs/index.html) is one of the most used solvers for quadratic programs.
- [Clarabel](https://clarabel.org/stable/) is new, implemented in rust, being able to deal with cones.
- [Crocoddyl](https://arxiv.org/pdf/1909.04947) is a formulation of DDP for contact-switched systems.
- [Altro](https://www.ri.cmu.edu/app/uploads/2020/06/altro-iros.pdf) is a fast solver for constrained traj. opt.
- The relevance of [scaling in your formulation of an optimization problem](https://arxiv.org/pdf/1810.11073), [and something similar in robotics](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9905530).
- On the relevance of [sparsity in MPC transcriptions](https://www.sciencedirect.com/science/article/pii/S0167691114002680?fr=RR-2&ref=pdf_download&rr=8a099b5adbe99200), and a [second time](https://ieeexplore.ieee.org/document/7798946).

I am interested in everything performace related similar to the things above.
If you think you have something that is relevant to the list, please let me know!
