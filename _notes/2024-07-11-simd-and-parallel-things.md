---
layout: post
title:  "SIMD and performant algorithms in robotics"
date:   2024-07-12 12:00:00 +0200
permalink: /simd-collection/
categories: performance
---

<p class="preface">
    There was a paper a bit ago that presents a really fast motion planner, using amongst other things SIMD programming for collision checking of edges (which is usually the most time intensive step).
    This got me more into SIMD programming, and hoarding a handful of links related to high-performing implementations of common robotics algorithms.
</p>

The paper/preprint in question is the one [here](https://arxiv.org/pdf/2309.14545.pdf) by [Zak](https://zkingston.com/) and [Wil](https://wbthomason.github.io/).
They present a really fast approach for motion planning, and have open sourced its implementation [here](https://github.com/KavrakiLab/vamp).
One of the things that they leverage is the parallelization of collision checking, which they call fine-grained collision checking.
Compared to 'traditional' parallelization over multiple cores, they do parallel collision checking using vectorization with SIMD.

Since they took a while to open-source their code, I made some experiments myself, which is in very rough shape, but can be found [on github](https://github.com/vhartman/simd-experiments).

In the rest of the note, I want to organize a few links on SIMD blog-posts, and on high performance implementations 

#### Generic cool things
- A while ago there was a discussion of an old (2011) post on [SIMD vs SIMT vs SMT](https://yosefk.com/blog/simd-simt-smt-parallelism-in-nvidia-gpus.html). However, the consensus seems to be that quite a lot of things have changed since then.
- [Here's](https://mcyoung.xyz/2023/11/27/simd-base64/) a great walkthrough of transitioning an algorithm implemented normally to SIMD-code.
- The relevance of [scaling in optimization](https://arxiv.org/pdf/1810.11073), [2](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9905530)

#### Robotics things
- Wil and co had [another paper](https://arxiv.org/abs/2406.02807) on cache/parallelization friendly nearest neighbor structures.
- A [parallel implementation of DDP](https://a2r-lab.org/files/GPU_DDP_WAFR_paper.pdf)
- [Gauss Newton multiple shooting](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8593840)
- [GPU sample based planning](https://arxiv.org/pdf/2403.11383), and [again](https://arc.aiaa.org/doi/epdf/10.2514/1.G001921) and [for aggressive driving](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7487277)
- [Accelerating Robot Dynamics Gradients on a CPU, GPU, and FPGA](https://people.csail.mit.edu/bthom/icra21.pdf)
- [Real time iterations with MPC](https://cse.lab.imtlucca.it/~bemporad/publications/papers/ijc_rtiltv.pdf)
- [curobo from nvidia](https://curobo.org/reports/curobo_report.pdf)
- [rrt on a gpu](https://ieeexplore.ieee.org/abstract/document/7926542)
- [mpc on a gpu](https://arxiv.org/abs/2104.13542)
- [better implementations of algorithms](https://ieeexplore.ieee.org/abstract/document/8794099)
- [tinympc](https://tinympc.org/) and [codegeneration](https://arxiv.org/abs/2403.18149)
- [teaching of parallel things](https://tcpp.cs.gsu.edu/curriculum/sites/default/files/EduPar-02-Teaching_Parallel_Optimization_for_Robotics__EduPar_2024__Final.pdf)

##### Optimizers
- [Sparsity in MPC transcriptions](https://www.sciencedirect.com/science/article/pii/S0167691114002680?fr=RR-2&ref=pdf_download&rr=8a099b5adbe99200), and a [second time](https://ieeexplore.ieee.org/document/7798946)
- [Crocoddyl](https://arxiv.org/pdf/1909.04947)
- [Altro](https://www.ri.cmu.edu/app/uploads/2020/06/altro-iros.pdf)
