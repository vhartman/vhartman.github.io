---
layout: cv
title: Long-Horizon Multi-Robot Rearrangement Planning for Construction Assembly
permalink: /multi-robot/
custom_css: cv
custom_title: Long-Horizon Multi-Robot Rearrangement Planning for Construction Assembly
---

*Valentin N. Hartmann, Andreas Orthey, Danny Driess, Ozgur S. Oguz, Marc Toussaint*
<p style="font-size:8pt">Machine Learning & Robotics Lab, University of Stuttgart, Germany<br>
Learning and Intelligent Systems Group, TU Berlin, Germany</p>

**Brief:**
By factoring a bigger problem in several subproblems that can be solved with few robots, we can compose a solution to the original problem. We greedily choose subproblems and agents to solve them, and account for previously solved problems. We demonstrate this on multiple construction scenarios, and on a more classical task and motion planning problem: stacking boxes with real robots.


**Abstract:**
<div style="display:block; margin: 0 2em 0 2em">
Robotic assembly planning enables architects to explicitly account for the assembly process during the design phase, and enables efficient building methods that profit from the robots' different capabilities. Previous work has addressed planning of robot assembly sequences and identifying the feasibility of architectural designs. This paper extends previous work by enabling planning with large, heterogeneous teams of robots.
<br>
<br>
We present a planning system which enables parallelization of complex task and motion planning problems by iteratively solving smaller subproblems. Combining optimization methods to solve for manipulation constraints with a sampling-based bi-directional space-time path planner enables us to plan cooperative multi-robot manipulation with unknown arrival-times. Thus, our solver allows for completing subproblems and tasks with differing timescales and synchronizes them effectively. We demonstrate the approach on multiple case-studies to show the robustness over long planning horizons and scalability to many objects and agents of our algorithm. Finally, we also demonstrate the execution of the computed plans on two robot arms to showcase the feasibility in the real world.
</div>

<hr style="margin: 2em 0 2em;">

### Paper 

Latest version: [arXiv](https://arxiv.org/abs/2106.02489)

<a href="https://arxiv.org/abs/2106.02489" target="_blank"><img src="/assets/multi-robot-thumb.png" style="display:block; margin:0 auto; border: 1px solid #555;"></a>

<hr style="margin: 2em 0 2em;">

### Videos

This video contains an overview of the experiments we did, the scenarios we consider, and a short overview on how the algorithm works.

<iframe style="display:block; margin: 0 auto;" width="600px" height="340" src="https://www.youtube.com/embed/GqhouvL5dig" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

<br>


We also executed a plan that our planner generates on a real robotic system.
The goal-configuration is a tower made of 6 boxes in the middle of the table.
This is achieved by the two arms.

The plan is executed open-loop in this demonstration, which explains the small inaccuracies when the arms are placing the boxes.
<iframe style="display:block; margin: 0 auto;" width="600px" height="340" src="https://www.youtube.com/embed/KILyXQDcEZw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

<hr style="margin: 2em 0 2em;">

### Bibtex

```
@article{22-hartmann-TRO,
  title = {Long-Horizon Multi-Robot Rearrangement Planning for
  		  Construction Assembly},
  author = {Hartmann, Valentin N. and Orthey, Andreas and Driess, Danny and Oguz, Ozgur S. and Toussaint, Marc},
  journal = {Transactions on Robotics},
  issn = {1552-3098},
  year = {2022},
  arxiv_pdf = {2106.02489},
  youtube = {GqhouvL5dig},
  web = {https://vhartmann.com/multi-robot/},
  doi = {10.1109/TRO.2022.3198020}
}
```

<hr style="margin: 2em 0 2em;">

### Funding
This research has been supported by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany’s Excellence Strategy – EXC 2120/1 – 390831618.

<hr style="margin: 2em 0 2em;">

### History
- 1st version (02.21): Rejected at RRS 2021
- [2nd version (06.21)](https://arxiv.org/abs/2106.02489v1): Revise and resubmit at TRO
  - Minor changes
- [3rd version (03.22)](https://arxiv.org/abs/2106.02489): Currently under review at TRO
  - Added more illustrations
  - Added algorithms
  - Added robot experiments
- [final, published version (08.22)](https://ieeexplore.ieee.org/document/9868234): Accepted at TRO 
  - content as above
  - formatting changed for camera ready
