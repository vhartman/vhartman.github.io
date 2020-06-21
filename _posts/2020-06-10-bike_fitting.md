---
layout: post
title:  "Finding my optimal position on a bike. Virtually."
subtitle: "or: Just another rabbit hole to dig in."
date:   2020-06-10 12:00:00 +0200
permalink: /bike_fitting/
categories: bike simulation
---

<p style="font-style: italic">
With my move to Berlin, and the subsequent lockdown, rowing became impossible fro now, and I started to ride my bike a lot more.
The position on the bike is the most important part to output the maximum power, and is influenced by several parameters.
Changing the seat hight and how far forward it is, and the hight of the handlebar is fairly straightforward.
On the other hand, changing the crank length is not as cheap and requires some extra equipment.
Hence, before taking the leap to a different crank lenght, I wanted to simulate how a different crank would affect my position on the bike<sup>1</sup>.</p>

<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: -50px;height: 300px;padding: 10px;font-size:10pt; width:200px">
<sup>1</sup>
As usual, the code to reproduce the experiments is <a href="https://github.com/vhartman/bike_fitting">here</a>.
</p>
</div>

There are various [rules](analyticcycling.com/PedalOpCrankLength_Page.html) [of](https://www.stevehoggbikefitting.com/bikefit/2011/06/crank-length-which-one/) [thumb](https://highpath.co.uk/crank-length-calculation/) (some of which are directly mcontradicting each other) that give you a guess on what crank length you should use, and a [lot](https://www.cyclist.co.uk/in-depth/360/bike-fit-variables-no-2-crank-length#:~:text=Cranks%20are%20measured%20from%20the,will%20come%20with%20longer%20cranks.) [of](https://cyclingtips.com/2017/09/crank-length-forget-leverage-power-fit/) [pages](https://www.trainingpeaks.com/blog/the-benefits-of-reducing-your-crank-length/) discussing crank length.
In the end, it all boils down to the measurements of your own body.
This post/analysis is directly motivated by this [video discussing crank length](https://www.youtube.com/watch?v=S0SpYdxg1UY).

# Data collection
Everything starts with data collection, and to do that, I took pictures of myself sitting on the bike with my foot (and hence my whole leg) in different positions.
I marked approximate locations of the relevant joints (hip, knee, ankle) with tape, to be able to mark them more accurately and repeatably on all the images.
The camera should be placed as far away as possible (obviously while still seeing the markers clearly) to ensure that the image is not distorted, and that every point we are measuring is approximately in the same plane, and not too affected/offset by perspective.

<div style="width: 100%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/raw_1.JPG" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/bike_fitting/marked_1.png" style="width:46%; padding: 10px">
</div>
<div style="width: 100%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/raw_2.JPG" style="width:46%; padding: 10px">
    <img src="{{ site.url }}/assets/bike_fitting/marked_2.png" style="width:46%; padding: 10px">
</div>
<figcaption style="padding-bottom: 10px">On the left side is the unmarked image, the right side is the marked image, with the circles indicating the possible movement.</figcaption>

We will assume the hip as fixed on the saddle (in reality, there is probably some slight movement), and the crank is clearly rotating around the fixed axle.
That leaves the angle between the foot and the shin,  (i.e. ankle flexion), and the knee-angle as degrees of freedom in our leg when pedalling on the bike.
Assuming that the foot stays at a constant angle is not too bad of an assumption, but it is not perfectly realistic either.
Hence, I took several pictures (19) of myself with the crank in different positions, and marked all of them.
This helps me with two goals:
- Getting a possibility to obtain an estimate for the crank-foot-angle-mapping<sup>2</sup>
- Obtaining more data to get a better estimate for the lengths between joints

<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: -70px;height: 300px;padding: 10px;font-size:10pt; width:200px">
<sup>2</sup>
Note that there could be some systematic error introduced, since I was pedalling in reverse.
The fact that no force is transferred on the foot/pedal system might lead to a systematic error in the measurements.
</p>
</div>

The fitted function is of the form 

$$f(\alpha) = \beta_1 + \beta_2\sin(\beta_3\alpha + \beta_4)$$

and seems to approximate the measured data ok enough.
When fitting the function to the measurements, I added the same data again, with an offset of $$2\pi$$ to obtain the periodicity in the parameters.
If this is not done, the function-fit is more dependent on the values at the edges of the data-range.

Plotting the foot-angles obtained from the pictures against the fitted function, and the distribution of the lengths of the connections between the joints gives the plots below:
<div style="width: 100%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/fitting_sens.png" style="width:46%; padding: 10px; vertical-align:top">
    <img src="{{ site.url }}/assets/bike_fitting/lengths.png" style="width:46%; padding: 10px; vertical-align:top">
</div>
<figcaption style="padding-bottom: 10px">Left side: Foot angle (measured and fitted). Right side: Lengths between some measured points, and standard deviation.</figcaption>

We also plot the 'skeletons' for the measurements we took from the images:
<div style="width: 50%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/measured_coords.png" style="width:40%; padding: 10px; vertical-align:top">
    <img src="{{ site.url }}/assets/bike_fitting/measured_coords_fixed.png" style="width:40%; padding: 10px; vertical-align:top">
</div>

where we can see that I attached the marking at the hip in the wrong place.
However, by elongating the thigh about 10% we can find the position that would have been correct (shown on the right)<sup>3</sup>.

<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: -50px;height: 300px;padding: 10px;font-size:10pt; width:200px">
<sup>3</sup>
The exact number can be found by fitting a circle to the measured points of the 'hip' and elongating the thigh by the radius of the circle.
</p>
</div>

# Estimating Positions and Angles
Given the crank-foot-angle curve we fitted above, we can regard the mechanism as a [four-bar mechanism](https://en.wikipedia.org/wiki/Four-bar_linkage), and its positions are fully determined if we are given one of the angles.
In our case, the angle we use to determine all the other poitions is the crank angle.

For a given crank angle it is straightforward to find the position of the pedal, and using the foot angle from the function, we get the position of the ankle.
We then use the known length of the femur and the lenght of the shin to find the intersection of the two circles (see e.g. [here](https://mathworld.wolfram.com/Circle-CircleIntersection.html) - we always know which of the two intersection points is the right one), and hence, the position of the knee.

With the additional assumption of a constant cadence of 80 revolutions per minute, we can compute the velocity and acceleration of the joints, and center of masses.
We start with the angles, and angular velocity and acceleration of the thigh, and compare it against the measured values.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/angular.png" style="width:100%; padding: 10px">
</div>
<figcaption style="padding-bottom: 10px">Thigh angle, angular velocity, and angular acceleration.</figcaption>

Now, having the ability to compute the movement of the joints, it is possible to alter the geometry, such as seat hight, hip position, and the part that propmted all of this: the crank length.
Changing the crank length also leads to a change in seat height since the leg does not have to be extended as much in its lowest position.

Generally, it is desirable to have an almost fully extended leg at the bottom, and a big angle at the top as well.
A larger angle at the top is desirable, since a larger force can be excerted in a more extended position<sup>4</sup>.
It can also avoid the feeling of pushing the knees into the chest, when in a more aerodynamic position.

<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: -70px;height: 300px;padding: 10px;font-size:10pt; width:200px">
<sup>4</sup>
This seems to 'common knowledge'.
There are a few studies (<a href="https://biomedical-engineering-online.biomedcentral.com/articles/10.1186/s12938-018-0610-5">[1]</a>, <a href="https://www.me.utexas.edu/~neptune/Papers/jab26%284%29.pdf">[2]</a>), but I can't seem to find an 'intuitive' explanation.
</p>
</div>

#### Adjusting the geometry
In the following, we compare 3 changes in position on the bike, and how the changes affect the angles, velocities, and accelerations in the leg:
- Shorter crank length - my current crank arm is 175 mm long, I want to test one that is 165mm long<sup>5</sup>
- Shifting the hip forward by 10 mm
- Lowering the saddle 100 mm as an counterexample of what to do

<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: -90px;height: 300px;padding: 10px;font-size:10pt; width:200px">
<sup>5</sup>
Since I am interested in what happens if we maintain the same speed, I am looking at two scenarios for the shorter crank length: either the cadence is increased, and the force is kept constant (i.e. shifting gears to obtain a different transmission), or the cadence is kept constant, and the force is increased.
In reality, a mix of both will probably occur.
</p>
</div>

For the analysis of the shorter crank, I am looking at two cases that would result in the same speed in the end:
- A different gearing, i.e. pedalling at a higher cadence, and
- pedalling at the same cadence with a higher peak force

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/angular_comp.png" style="width:100%; padding: 10px">
</div>
<figcaption style="padding-bottom: 10px">Thigh angle, angular velocity, and angular acceleration.</figcaption>

As we can see, and as expected:
- the shorter crank leads to better angles - but only by about 3° in the most extreme position,
  - depending on the gearing/force tradeoff, the peak acceleration of the thigh can be reduced quite a bit,
- shifting the hip forwards produces a similar result, when only looking at the angles (unfortunately, I am already shifted forward maximally, also: realistically, this would already lead to a bit of an adjustment in the foot angle, which is not taken into account here)
- decreasing the saddle height by 10cm is definitely not desirable (as if this was a question)

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/dynamics_diff.png" style="width:100%; padding: 10px">
</div>

Looking at the accelearations of the center of masses of the parts of the leg, we see that
- the shorter crank at the same cadence decreases the necessary acceleration (and thus the necessary force to 'stop' the upwards movement) in the thigh a bit
- riding at a higher cadence will increase it by roughly the same amount

#### Sensitivity analysis
I wanted to see how strongly the results are dependent on the accuracy of the measurements.
To check that, I added some offsets to the measurements of the hip position, and the lengths of the legs.
The other positions (crank length, axle position) stay the same.

The distribution of configurations I test have gaussian noise with 5% standard deviation around the actually measured values.
I.e. a measured femur-length of 48cm leads to values between 45.6 and 50.4 with a probability of 68%.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/angular_sens.png" style="width:100%; padding: 10px">
</div>
<figcaption style="padding-bottom: 10px">Thigh angle, angular velocity, and angular acceleration - blue: disturbed measurements at the same geometry, orange: shorter crank with the same disturbed measurements, black: measurements.</figcaption>

While we can see in the plot above that the angle varies quite a bit, the occuring velocities and accelerations are definitely lower when dealing with a shorter crank.
In addition, the shorter crank seems to lead to slighlty less extreme angles - meaning that the point of our analysis above is valid.

# Estimating forces
Clearly, we do not only care about the position of the legs, we care about where and how power is applied to the road through the pedal.
Various articles ([1](https://link.springer.com/article/10.1007/BF00696088), [2](https://www.researchgate.net/publication/261871567_Pedal_force_effectiveness_in_cycling_A_review_of_constraints_and_training_effects)) estimate the force that is excerted on the pedal, and I found one scientific paper that actually measures the application of the forces over time, respectively dependent on the angle of the crank.

To make my life a bit easier, I am approximating the curve described in the paper as a sinusoidal, that is cut off, when we are at the lowest point of the revolution - that is, we do not apply force to the pedal, but neither does the pedal apply a force to the foot.

In addition to the force that we get in the foot, there are forces from the acceleration and deceleration of the leg.
This paper [here](https://exrx.net/Kinesiology/Segments) has a distribution of the weight of a person on different parts of the body, and where the center of mass is.
For us, the weight of the foot (1% BW), shin (4% BW), and thigh (14% BW) is relevant to compute the moments and forces.
We use the recursive newton euler algorithm to propagate the forces through the leg, and assume that the hip takes all the force.

This gives us the following forces in the joints:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/forces.png" style="width:100%; padding: 10px">
</div>

From the forces in the thigh, we can figure out the moment arount the hip joint that we need to produce with our muscles<sup>6</sup>:
<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: -70px;height: 300px;padding: 10px;font-size:10pt; width:200px">
<sup>6</sup>
The model I use to obtain the forces in the leg is clearly oversimplified, as the assumption that our muscles only produce a torque around the hip joint is wrong.
</p>
</div>
<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/bike_fitting/moment.png" style="width:100%; padding: 10px">
</div>
<figcaption style="padding-bottom: 10px">Moment vs femur angle plot for different cadences.</figcaption>

From the plot above, we see that while we need to produce slighly higher peak torques, we need to produce them at more advantageous angles compared to the baseline.
We also see that the required moment is slightly lower when pedalling at a higher cadence.

# Results
In general, I found out/realized that it mostly comes down to personal preference what crank length should be chosen to maximize performance.
There is a slight upside to working with shorter cranks, but a higher cadence has to be doable by the rider.
In addition, it seems like too long cranks lead to higher shear forces in the knee, and thus a larger possibility of injury (see [here](https://ridefar.info/2017/02/crank-length-and-comfort-for-long-distance-cyclists/)).

Comfort seems to be a major point that is discussed on blogs, but this is not something that can be easily formulated in an objective manner to lookt at.
The consensus among the posts that I read over the course of this project seems to be that most cranks that are delivered with bikes as standard is are too long - however, it seems to be mostly a question of actually trying different crank lengths to figure out which is ideal for each person.
Power output does not seems to be affected by the crank length in most scientific publications.

### Outlook/Future Ideas
While working on this whole project, I dug myself deeper and deeper into a rabbit hole of scientific literature and muscle models that could be implemented to get a more accurate force estimate and various other ideas.
- A full model, including muscles, and muscle activations could be built using the previously made measurements.
Obviously, some estimates would have to be made regarding muscle-size, activation speeds etc, but it would likely be more accurate than the current version.
This model could be used to attempt to find the most efficient 'pedal stroke', which would be more of a machine-learning/optimization exsercise, rather than actually learning something about the pedal stroke to ride the bike more efficiently.
- Translate the model into something more interactive, that could e.g. be used directly in the browser.
- Test the findings in reality - as mentioned in the introduction, it is not as straightforward to switch cranks as I thought it would be initially.
Hence, I have to wait until the community-bike-shops are back open again to actually test changing the cranks of my bike.
I am also debating with myself if it is worth it to change the cranks on the soon to be city bike, or if I should wait until I get a new bike.
