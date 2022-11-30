---
layout: about
title: Ideas
custom_css: cv
permalink: /ideas/
custom_title: Things I am interested in
---
Inspired by [Kevin Lynagh](https://kevinlynagh.com/), I maintain an ongoing list of ideas that I want to work on eventually, and possibly pair on.
Some of them are inspirde by research papers that I want to replicate to better understand the intricacies, some of them come from unanswered questions that came up in my life somewhere.
Other things are topics that I simply wondered about at some point, and want do dig deeper for a bit.

Note that most of these ideass are not projects I am supervising as part of my PhD, these are things I am doing for fun, and in general not very academic.

#### Robotics
- **Optimal behavour of a vacuuming robot to cover the floor space efficiently:**
This would probably entail generating 'realistic' rooms automatically, deciding what sensors a vacuum robot should have (I am thinking only proximity), and what possible behaviours a robot can follow from that.
- **Landing a rocket**: I am foremost interested in simply building a model (possibly in 2D for a start), and applying various approaches to the problem.
- **Examining the effect of modern stepsize controllers in numerical control**: This is a version of what I did in a Thesis during my masters, and I would like to dig a bit deeper here. This would go in the direction discussed [here](https://github.com/scipy/scipy/issues/9822) in the scipy numerical integration community.
- **Exploring SAT solvers**: Not entirely sure what I am specifically looking for here. Kevin Lynagh has a few ideas to the topic on his page, I am mostly interested if this can be used for robotics applications.

#### Software
- **Traveling Salesman Problem-Art**: This involves approximating an image via a bunch of dots, and connecting them with the shortest path.
Possible topics to pursue here are: optimal stippling, benchmarking different approaches of TSP-solvers, interfacing between python and cpp.
- **Simulating a leg through a pedal-stroke**:
Following up on my project I did before, I want to see when (and how) we actually apply pressure on the pedal.
- **[Passing networks (PDF)](https://arxiv.org/pdf/1807.00534.pdf) in soccer** over the curse of a season.
How do passing networks change if the coach is replaced? Are there general trends visible in winning teams? <br>
   There is an additional paper doing a deep dive of FC Barcelona in their most successful season [here](https://www.nature.com/articles/s41598-019-49969-2). Data for one season for several leagues is available [here](https://figshare.com/collections/Soccer_match_event_dataset/4415000/4).


#### Papers
- **Moving horizon estimation**: Enabling (amongst various other things) constrained state estimation, this is the counterpart to MPC for state estimation.
This is a catch-it-all item on the list for various topics - please reach out if you are into state estimation/control.

#### Games
- **Dog**: Dog is a version of the boardgame [*Mensch ärger dich nicht*](https://en.wikipedia.org/wiki/Mensch_%C3%A4rgere_Dich_nicht) that is played wih cards. [Here](https://www.dogspiel.info/index.php/spiel) is an explanation in german, and [here](https://www.dogspiel.info/images/pdfs/rules.pdf) are the rules in english. I am interested if there is some sort of optimal stragtey, and building an artificial intelligence that can play (well?).
- **Käsekästchen/Dots and Boxes**: This [game](https://en.wikipedia.org/wiki/Dots_and_Boxes) is a childrens game, but has surprisingly [many strategic nuances](https://www.mat.univie.ac.at/~ifischer/papers/dots.pdf). I am interested in a computational approach to playing this game (Monte-carlo tree search? Reinforcement learning?)
- **Labyrith**: This [game](https://en.wikipedia.org/wiki/Labyrinth_(board_game)) has the goal to visit a set of symbols with a figure. The figures move on a maze, which can be altered by pushing in new parts of the maze (and pushing others out). As in the previous two points, I am interested in figuring out if there is some optimal way to play this game.
