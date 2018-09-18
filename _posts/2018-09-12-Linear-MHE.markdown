---
layout: post
title:  "The linear Moving Horizon Estimator"
date:   2018-09-12 09:31:34 +0200
categories: MHE
---

One of the strengths of moving horizon estimation is it's explicit possibility to deal with nonlinear state equations. Nonetheless, the version for linear systems is computationally far simpler, making it an ideal first testbed for various approaches to get accurate estimates from data with outliers.

### The moving horizon estimator
...

For a first test, a very simple double integrator with a gaussian noise distribution on the sensor, and a gaussian disturbance is used. As a comparison, the Kalman filter is implemented as well, and initialized with the same initial value.

As expected, both algorithms result in the same estimate for the simple linear system with gaussian noise distributions. In the next step, the noise distributions are replaced by non-gaussian distibutions. In Figure [], the used distibutions are gaussians truncated at [], in Figure [], the distribution is uniform, and in Figure [], the original distribution is squared.
