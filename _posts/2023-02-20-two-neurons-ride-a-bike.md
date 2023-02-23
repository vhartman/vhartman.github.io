---
layout: post
title:  "Replicating 'It Takes Two Neurons To Ride a Bicycle'"
#subtitle: "or: .."
date:   2023-02-20 12:00:00 +0200
permalink: /two-neurons-bike/
categories: replication science
---

I wanted to recreate this paper from 2004 at NeurIPS: ["It Takes Two Neurons To Ride a Bicycle" from Matthew Cook](http://paradise.caltech.edu/~cook/papers/TwoNeurons.pdf).
My complete implementation is available [here]().

# Setting up the bike simulation

First, it turns out that it is actually hard to find the equations of motion that describe a bike.
There is a plethora of papers ([[1]](https://www.researchgate.net/profile/Anders-Lennartsson-2/publication/3207639_Bicycle_dynamics_and_control_Adapted_bicycles_for_education_and_research/links/56974ffb08ae34f3cf1e1a7c/Bicycle-dynamics-and-control-Adapted-bicycles-for-education-and-research.pdf) [[2]](http://bicycle.tudelft.nl/schwab/Bicycle/BicycleHistoryReview/FraSuhRie90.pdf) [[3]](https://thef1clan.com/2020/12/23/vehicle-dynamics-the-dynamic-bicycle-model/) [[4]](https://www.tandfonline.com/doi/abs/10.1080/00423114.2013.793365?role=button&needAccess=true&journalCode=nvsd20), [[5]](https://authors.library.caltech.edu/536/1/GETieeeicra95.pdf)) but in the end, it was much easier to just set this problem up in pybullet, and make a bike run in a full fledged simulator, compared to setting up some system of equations, and integrating that forward.

The bike I used was this one:
<div style="width: 50%;margin:auto">
    <img src="{{ site.url }}/assets/bike-neurons/bike.png" style="width:100%; padding: 10px">
</div>
which is part of pybullet.
*But*, the wheels have a wrong offset, resulting in the center of mass being offset to the side from the wheelbase.
Thus, the coordinates of the visual and the inertial part of the 'frontWheelLink' and 'backWheelLink' in the urdf need to be changed to:

```
<collision>
  <origin rpy="1.57 0 0" xyz="0 0.02762793 0"/>
  <geometry>
   <mesh filename="files/wheel_scaled.stl"/>
  </geometry>
</collision>
```

After that, some physics parameters need to be set to allow for unsteered versions of the bike.
I am not going to elaborate on that here, see the code for this.

#### Path of an unsteered bicycle
My initial core motivation for reimplementing this paper was Figure 2. from the paper that shows the path of the frontwheel for 800 runs when the bike is not steered.
Here's the original:

<div style="width: 50%;margin:auto">
    <img src="{{ site.url }}/assets/bike-neurons/org_fig_2.png" style="width:100%; padding: 10px">
</div>

I was not able to get exactly the same result, but got pretty close.
Here's a few figures with different initial speeds (from the top left to the bottom right, 3m/s, 4m/s, 5m/s, 6m/s):

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike-neurons/frontwheel_trace_vel_3.png" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/bike-neurons/frontwheel_trace_vel_4.png" style="width:46%; padding: 10px">

    <img src="{{ site.url }}/assets/bike-neurons/frontwheel_trace_vel_5.png" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/bike-neurons/frontwheel_trace_vel_6.png" style="width:46%; padding: 10px">
</div>

I suspect the main difference between the original plot and my reproductions is due to the different bike geometry.
Generally, the result seems to be very sensitive to the initial conditions, so there is also the possibility that choosing the 'right' initial perturbations leads to an even more similar plot.

#### The two neuron controller and tracing a path
With the simulation up and running, I implemented the two-neuron-controller described by the paper.

The two neuron controller gets the heading of the bike $$\theta$$, the leaning $$\gamma$$, and the leaning-velocity $$\dot\gamma$$ as input.
The action the controller takes is the torque that is applied to the handlebar.

The controller is then formed by the two equations:

$$
\begin{align}
\gamma_\text{desired} &= \sigma(c_1(\theta_\text{desired} - \theta))\\
\tau_h &= c_2(\gamma_\text{desired} - \gamma) - c_3\dot{\gamma}
\end{align}
$$

Where $$\sigma()$$ is a thresholding function that ensures that the controller does not go crazy if the desired angle is too far away from the actual angle.
I used the sigmoid-function for $$\sigma$$, and centered it around the x-axis.
This is _extremely_ close to a hierarchical PD controller of the form $$u = k_p * e + k_d * \dot{e}$$.

There is one caveat here: The difference between two angles is not nicely described bu subtracting the two angles from each other.
This leads to issues if e.g. $$\theta_\text{desired}=-\pi+\varepsilon$$ and $$\theta=\pi-\varepsilon$$.
The difference we want is $$2\varepsilon$$, but the result we get when subtracting the two values is $$-2\pi+2\varepsilon$$. 

I did spend some time runing the parameters of this controller, resulting in the values $$c_1 = -1, c_2 = 100, c_3 = 100$$
The controller is able to stabilize the bike and follow a path defined by a sequence of points.
The points are used to compute the required angle, and once the bike gets close to a point, we are steering to the next point.

I spent some more effort, and ran a random search to improve the controller parameters.
I defined the reward $$R = -0.1 * (\theta - \theta_\text{desired}) + 1$$ given at each timestep.
This should punish deviation from a desired angle, but reward not falling over.
Falling over lead to a 'reward' of $$-10000$$.
A reward of $$1000$$ was given for reaching the next point in the path, and an additional reward of $$5000$$ was given for reaching the last point in the path.

My hand-tuned, initial parameters reached $$27911.346$$ on the reward above for a square path, and a circular path.

The best parameters of the random search were $$c_{1,2,3} = [-0.95, 22.959, 27.761 ]$$, which reached a reward of $$44966.643$$.

Following two paths looks like this for the hand tuned, and the found controller:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike-neurons/circle_path.png" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/bike-neurons/square_path.png" style="width:46%; padding: 10px">
</div>

#### Sketchy RL solutions
The paper also discusses a fairly simple controller (one that has an oracle and can choose the best action by looking into the future one step andn choosing the best action) - we'll skip that part.

In the paper, a few RL approaches are discussed, but all of them mainly exploited the value function.
I wanted to see that for myself.
I implemented a reinforcement learining based approach which has the objective to keep the bike upright.

The observations I fed to the RL algorithm{% include sidenote.html text='I used a simple tabular-q-learning implementation, as I assumed that there should not be much difficulty.'%} were the heading of the bike $$\theta$$, the leaning $$\gamma$$, and the leaning-velocity $$\dot\gamma$$.
The action the controller can take is the torque that is applied to the handlebar.
The reward it gets is 1 for each timestep the simulation runs.

The training graphs look roughly like this:

[]

And the resulting behaviour is:

[]

I would expect much better results if we changed the metric to some form of path-following.

# Final Words
The paper is fun, well written, and results in nice plots.

My main difficulty in replicating the paper were 
- figuring out that the bike-model in pybullet has a center of mass that is offset, and
- computing the leaning and heading angles.

I think the claim that two neurons are needed to ride a bike (given that it is actuated) is reasonable with the caveat that computation of the steering angle needs to be done carefully.

I might want to have a look at running some learning/control algorithm on this system, and also deal with pedalling speed to give the bike a bit more agility.
