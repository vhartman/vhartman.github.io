---
layout: post
title:  "Steering a rocket towards orbit using random trees"
date:   2018-03-26 12:31:34 +0200
categories: rocket RRT pathplanning
---

Path finding is usually not used to find _a_ path, but rather an optimal path, or at least a reasonably optimal path. Obviously, this is not necessarily the best way to find the most cost efficient path, but it is a way, that might be interesting.

# Rocket dynamics
It is necessary to know the dynamical model of the rocket to be able to build up our random tree. Several detailed models for such a rocket exist as seen here [link]. For simplicitiy and to verify that the idea works, here we will first consider a very simplified model. The state (that will be sampled in the RRT algorithm) of the rocket consists of 
\\[x = [p_x, p_z, v_x, v_z, \alpha, \omega, m_R]^T \\]
![rocket variables and coordinate frame]({{ site.baseurl }}/images/rocket_variables.png){: .center-third}

The forces that are acting on the body that we are considering are

* Gravity
\\[F_G = G\frac{m_em_R}{r^2}\\]
with 
  * the gravitational constant $$G = 6.674e-11$$
  * the mass of the earth $$m_e = 5.97e24$$
  * the mass of the rocket $$m_R$$
  * The distance between the center of the earth and the current position of the rocket $$r = 6.371e3 + \sqrt{p_x^2 + p_y^2}$$
* Drag
\\[D = \frac{1}{2}C_dA\rho v^2\\]
with 
  * The drag coefficient $$C_d$$
  * The relevant area $$A$$
  * The density of air $$\rho(p_x, p_z)$$ depending on the height of the rocket. Taken from [NASA][nasa-air].
  * The relative speed of the rocket compared to the air $$v^2 = v_x^2 + v_z^2$$
* Axial propulsion
\\[F_P = u_1\\]
* Rotational propulsion
\\[M_P = u_2\\]

With this, the full dynamics in the form $$\dot{x} = f(x, u)$$ are

<center>$$
    \dot{x} = 
    \begin{bmatrix}v_x \\ v_z \\ a_x \\ a_z \\ \omega \\ \dot{\omega} \\ \dot{m_R} \end{bmatrix}
    =
    \begin{bmatrix}
    x_3\\
    x_4\\
    \frac{1}{m_R}\left[G\frac{m_ex_7x_1}{(x_1^2 + (x_2 + r_e)^2)^{3/2}} - \frac{1}{2}C_DA\rho x_3(x_3^2 + x_4^2)^{1/2} + \cos\alpha ku_1\right]\\
    \frac{1}{m_R}\left[G\frac{m_ex_7(x_2 + r_e)}{(x_1^2 + (x_2 + r_e)^2)^{3/2}} - \frac{1}{2}C_DA\rho x_4(x_3^2 + x_4^2)^{1/2} + \sin\alpha ku_1\right]\\
    x_6\\
    u_2\\
    -u_1
    \end{bmatrix}
$$</center>
# Random trees

[nasa-air]: https://www.grc.nasa.gov/www/k-12/airplane/atmosmet.html
