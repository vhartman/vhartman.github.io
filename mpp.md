---
layout: cv
title: Efficient Path Planning In Manipulation Planning Problems by Actively Reusing Validation Effort
permalink: /manipulation-path-planning/
custom_css: cv
custom_title: Efficient Path Planning In Manipulation Planning Problems by Actively Reusing Validation Effort
---

*Valentin N. Hartmann, Joaquim Ortiz-Haro, Marc Toussaint*
<p style="font-size:8pt">Machine Learning & Robotics Lab, University of Stuttgart, Germany<br>
Learning and Intelligent Systems Group, TU Berlin, Germany</p>

**Brief:**
We introduce a decomposed collision checking procedure that enables reuse of collision checking results even if the environment changes.
Collision checking is split in multiple parts, and the search in path planning is ordered by expected validation effort.

**Abstract:**
<div style="display:block; margin: 0 2em 0 2em">
The path planning problems arising in manipulation planning and in task and motion planning settings are typically repetitive: the same manipulator moves in a space that only changes slightly. Despite this potential for reuse of information, few planners fully exploit the available information. To better enable this reuse, we decompose the collision checking into reusable, and non-reusable parts. We then treat the sequences of path planning problems in manipulation planning as a multiquery path planning problem. This allows the usage of planners that actively minimize planning effort over multiple queries, and by doing so, actively reuse previous knowledge. We implement this approach in EIRM* and effort ordered LazyPRM*, and benchmark it on multiple simulated robotic examples. Further, we show that the approach of decomposing collision checks additionally enables the reuse of the gained knowledge over multiple different instances of the same problem, i.e., in a multiquery manipulation planning scenario. The planners using the decomposed collision checking outperform the other planners in initial solution time by up to a factor of two while providing a similar solution quality.
</div>

<hr style="margin: 2em 0 2em;">

### Paper 

Latest version: [arXiv](https://arxiv.org/abs/2303.00637)

<a href="https://arxiv.org/abs/2303.00637" target="_blank"><img src="/assets/manip-path-planning/thumb.png" style="display:block; margin:0 auto; border: 1px solid #555;"></a>

<hr style="margin: 2em 0 2em;">

### Bibtex

```
@inproceedings{23-hartmann-IROS,
  title = {Efficient Path Planning In Manipulation Planning Problems by 
           Actively Reusing Validation Effort},
  author = {Hartmann, Valentin N. and Ortiz-Haro, Joaquim and 
            Toussaint, Marc},
  year = {2023},
  url = {https://arxiv.org/abs/2303.00637},
  arxiv_pdf = {2303.00637}
}
```

<hr style="margin: 2em 0 2em;">

### Funding
The research has been supported by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany’s Excellence Strategy – EXC 2120/1 – 390831618 "IntCDC" and by the German-Israeli Foundation for Scientific Research (GIF) grant I-1491-407.6/2019.
