---
layout: cv
title: Towards computing low-makespan solutions for multi-arm multi-task planning problems
permalink: /robplan-low-makespan/
custom_css: cv
custom_title: Towards computing low-makespan solutions for multi-arm multi-task planning problems
---

*Valentin N. Hartmann, Marc Toussaint*
<p style="font-size:8pt">Machine Learning & Robotics Lab, University of Stuttgart, Germany<br>
Learning and Intelligent Systems Group, TU Berlin, Germany</p>

**Brief:**
We use a search over possible assignments and orders in combination with a prioritized multi-robot path planner to produce a low makespan solution to a subset of TAMP problems.

For a more in-depth, but hopefully more accessible version than the paper itself, have a look at [my post on this paper.](/low-makespan-tamp/)

**Abstract:**
<div style="display:block; margin: 0 2em 0 2em">
We propose an approach to find low-makespan solutions to
multi-robot multi-task planning problems in environments
where robots block each other from completing tasks simultaneously.
We introduce a formulation of the problem that allows for an
approach based on greedy descent with random restarts for
generation of the task assignment and task sequence. We then
use a multi-agent path planner to evaluate the makespan of a
given assignment and sequence. The planner decomposes the
problem into multiple simple subproblems that only contain a
single robots and a single task, and can thus be solved quickly
to produce a solution for a fixed task sequence. The solutions
to the subproblems are then combined to form a valid solution
to the original problem.
We showcase the approach on robotic stippling and robotic
bin picking with up to 4 robot arms. The makespan of the solutions found by our algorithm are up to 30% lower compared
to a greedy approach.
</div>

<hr style="margin: 2em 0 2em;">

### Paper 

Latest version: [arXiv](https://arxiv.org/pdf/2305.17527.pdf)

REPLACE

<a href="https://arxiv.org/abs/2305.17527" target="_blank"><img src="/assets/manip-path-planning/thumb.png" style="display:block; margin:0 auto; border: 1px solid #555;"></a>

<hr style="margin: 2em 0 2em;">

### Animations
On the left, the greedy (alternating between the two arms) version is shown, and on the right, the optimized variant can be seen.
<div style="width: 85%;margin:auto">
    <img src="{{ site.url }}/assets/low-makespan/bin_picking_two_arms_greedy_2.gif" style="width:45%; padding: 5px">
    <img src="{{ site.url }}/assets/low-makespan/bin_picking_two_arms_opt.gif" style="width:45%; padding: 5px">
</div>

<hr style="margin: 2em 0 2em;">

### Bibtex

```
@inproceedings{23-hartmann-robplan,
  title = {Towards computing low-makespan solutions for 
           multi-arm multi-task planning problems},
  author = {Hartmann, Valentin N. and Toussaint, Marc},
  year = {2023},
  booktitle={International Conference on Automated Planning and Scheduling:
             Planning and Robotics Workshop (RobPlan)},
  url = {https://arxiv.org/abs/2305.17527},
}
```

<hr style="margin: 2em 0 2em;">

### Funding
The research has been supported by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany’s Excellence Strategy – EXC 2120/1 – 390831618 "IntCDC".
