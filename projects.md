---
layout: about
title: Projects
custom_css: cv
permalink: /projects/
custom_title: Projects
---

I like learning about a topic by implementing my own take on it, and documenting it for myself and others to read.

<!---### The Moving Horizon Estimator
...

### Path planning with various algorithms
... --->


<div style="position: relative;"><img src="{{ site.url }}/assets/ind-icon.png" class="side-image" style="width: 100px; left: -120px;"></div>
### [Bachelors Thesis: Inductance based stiffness sensing]({% post_url 2019-10-30-Stiffness-sensing-catheter %})
During my Bachelors Thesis, I built a prototype on an inductance sensing catheter. It is based on the physical effect of eddy currents, and the following change in the eigenfrequency of a resonant LCR-circuit. The final sensing circuit is able to measure displacement to an accuracy of 5nm in a controlled environment.

<hr style="width:80%;margin-left: auto; margin-right: auto; margin-top: 40px;margin-bottom: 20px;">
<h4 style="margin-left:-12px">Project/Writeup in progress</h4>

<div style="position: relative;"><img src="{{ site.url }}/assets/num-meth-icon.png" class="side-image" style="width: 100px; left: -120px;"></div>
{%comment%}
<!--### [Semester Thesis: High Performance Numerical Methods for Optimal Control]({% post_url 2019-11-01-Adams-Bashforth-Boost-Odeint %})-->
{%endcomment%}
### Semester Thesis: High Performance Numerical Methods for Optimal Control
My Semester Thesis resulted in a contribution to Boot Odeint, namely a variable stepsize, variable order controller based on the Adams Bashforth Moulton method. Up to 12 times less function calls are needed during the solution and on appropriate problems, a speed-up of factor four can be achieved over other state of the art integrators with the implemented algorithm.

<div style="position: relative;"><img src="{{ site.url }}/assets/boarding-icon.png" class="side-image" ></div>
### [Simulating a boarding process](https://github.com/vhartman/brd)
I wrote a simulation of various boarding processes for airplanes for a class (Entrepreneurial Risks by Prof. Didier Sornette), and analyzed and visualized the results. This lead to an ongoing project on efficiency improvements in the boarding methods for planes.
