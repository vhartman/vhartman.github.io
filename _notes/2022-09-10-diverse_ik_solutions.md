---
layout: post
title:  "Computing diverse IK solutions"
date:   2022-09-10 12:00:00 +0200
permalink: /diverse-ik/
categories: science research
---

# Computing an IK solution
Computing an inverse kinematics solution to a problem can be done in closed form, but typically, optimization approaches are used, as the goal that should be reached is often underspecified (e.g. in the pen plotting case, we do not care about the orientation of the pen around its axis, and we are given quite a bit of freedom of the angle of the axis with respect to the paper we want to make a dot on).

However, the resulting problem is very nonlinear due to collision avoidance requirements.

# Why?
It can be the case that we want to find multiple diverse soltions toa problem. 
The motivation for me is from [this paper] or [this blo post on stippling robots].
In bot cases, I want multiple valid solutions to find sets of solutions for multiple robots thatdo not conflift, i.e. do not collide.

# How?
The dumb approach is simply randomizing the initial pose from which the optimization algorithm starts.
There is some research going on here though:
- Learnig based - Ikflow: https://sites.google.com/view/ikflow
- Also learning based Kim and perez

In other fields:
- Diverse solutions to constraint opt problems: https://www.ijcai.org/Proceedings/15/Papers/043.pdf
- Diverse and similar solutoin in constraint programming: https://www.aaai.org/Papers/AAAI/2005/AAAI05-059.pdf
- Contraint programming: https://en.wikipedia.org/wiki/Constraint_programming
