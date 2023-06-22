---
layout: post
title:  "How much quicker am I on my road bike compared to my city bike?"
subtitle: "or: Is that all a measuring artifact?"
date:   2023-02-20 12:00:00 +0200
permalink: /speed/
categories: data
---

<p class="preface">
    Strava recently suggested to me that I am roughly 3 minutes faster on my ~15 min way to work if I use my road bike compared to my old vintage (former road) bike.
    I wanted to double check.
</p>

# Preface
The weather is nice again here in Berlin, which means that my cycling habit makes me use my road bike for riding to work - it feels nicer to ride, and makes a more pleasant commute.
I log most of my rides on strava, including my way to work.
Strava has a feature that lets you compare your ride time on routes you have ridden before, and thus see if you have been faster or slower on this route compared to previous rides (commutes in this case).

After dusting off my road bike after winter and riding it to the university, Strava let me know that I am much faster with my road bike (higher is better, as the speed is plotted):

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/commute_time.png" style="width:100%; padding: 10px">
</div>

That graph prodded me to have a look at the data to figure out if I am really that much faster (I could save 3 minutes of my 15 minutes commute twice a day!), or if that is some measurement artifact.

#### A bit of background
On my roadbike, I use my bike computer - on my city bike, I am using my phone to log my riding.
The bike computer has the more accurate GPS (or it does better filtering of the data?), and also has some other sensors which might make the data more accurate overall (among them a velocity sensor).

The data that strava uses to compile the speed-plot above is the _riding time_.
That is, not the time from door to door, but the time I spent actually moving (e.g., waiting at red lights is removed).
Since there is a difference in measurement setup, I suspect that the more accurate data could lead to a lower riding time, as the time spent waiting at traffic lights can be more accurately be subtracted.
Stated differently, I believe that the riding time might be overestimated when the phone is the data source, and with the riding time being possibly overestimated, the speed would be underestimated.
That is, the conclusion 'I am faster with my road bike' might be wrong.

All that being said, riding the road bike definitely feels faster - which is one of the reasons I prefer using it.

# Looking at the data
Strava lets me export all my data as a zip folder{% include sidenote.html text='Partially due to GDPR. This download was possible before as well, but you get more data now.'%}.
There is lots of stuff that I do not need in there - for the analysis here, I will rely on the files of the activities, i.e. the actually logged data during the rides, and the 'activities.csv' file, which is essentially an overview of all my rides.

The most obvious initial step is to check if the trend that holds for the riding time also holds for the elapsed time.
For that, we need to find the activities that are a commute, and we need to sort them by bike.

For some reason{% include sidenote.html text='Pretty sure that is just a default that I did not bother to change.'%}, my rides that are created by the bike computer are named in english, while the ones from my phone are named in german.
Thus, the 'sorting by bike' can be achieved by simply looking for 'ride' (compared to 'fahrt') in the activity name.

Figuring out which ride is a commute is a bit more involved{% include sidenote.html text='In theory, it is possible to mark rides as commutes. In practice, I only do that for rides recorded with my phone.'%}.
We could probably get a reasonable proxy by filtering by activity length, but I decided to take a slightly different route, and will have a look at the start and the end coordinates of the activity, and check if that corresponds to my home, respectively work-coordinate.

The files from the bike computer are '.fit.gz' files, which we need to convert to '.gpx' files to be able to easily look at the actual movement coordinates and timestamps.
I did this using the python library [fit2gpx](https://pypi.org/project/fit2gpx/).
To then work with the gpx files, I used [gpxpy](https://pypi.org/project/gpxpy/).

#### Filtering the rides
To check if my ride starts at home/ends at the university and vice-verca, I am comparing the start-coordinate and the goal-coordinate with the coordinate of my home, and the coordinate of my working place (the university).

Only plotting the rides in question gives roughly this (left is city bike, right is road bike):

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/city_bike_paths.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/road_bike_paths.png" style="width:45%; padding: 10px">
</div>

Here, I colored the rides to the university in orange and the ones back home blue.
There are a bunch of outliers, but its not that many, so we'll keep it as is for now.

With the bikes distinguished, and the rides filtered, so we are only considering the ones that actually go from university to home, and the other way, we can make pretty histograms of the elapsed time between start and end:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/htw_elapsed.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_elapsed.png" style="width:45%; padding: 10px">
</div>

we can also plot histograms of the average speed for both ways:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/htw_speed_avg.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_speed_avg.png" style="width:45%; padding: 10px">
</div>

We could now do a bunch of statistical tests to figure out if that is actually a significant difference, and if the hypothesis 'I am faster with my road bike' holds, but I am not doing that.
I am simply going to claim that the histograms above seem different enough for me to believe that there is a significant difference.

To ensure that I am not simply starting the logging later (and thus shortening the path, and the time), I also had a look at the distance-histogram which shows relatively clearly that there is no big variation in the ride-distances.

With all these plots, I think I can fairly confidently confirm that I am roughly 3 minutes quicker with the road bike.

# Going deeper
Of course, correlation does not imply causation.
The 'being faster' could for example be caused by only taking the road bike on days with good weather (which is the case as mentioned in the beginning - I am not taking the nice road bike in rain etc.).

Rather than only answering the question I posed initially, I am also interested in the question why I am actually faster with the road bike.
As alluded to above, this is likely very hard to answer.
Is it the better tires of the bike (probably)? Is it the better weather (maybe)? Am I more aerodynamic (unlikely)?

One thing that might help answer this, is looking at moving time vs. elapsed time.
That might give some information on time spent at traffic lights etc., and tell me if I am just spending more time accelerating/decelerating with the older bike.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/htw_diff.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_diff.png" style="width:45%; padding: 10px">
</div>

There is no significant difference in moving and elapsed time between the road bike and the city bike: I am spending roughly the same time 'not moving' for both types of bikes.

One notable mention is that there is a long tail on both ways on the way from home to the university, but only for the city bike on the other way.
The long tails correspond to me getting a Döner (on my way to work, for lunch), and going shopping.
When taking my road bike, I am not going shopping, since I don't like leaving my road bike unattended.

Next, we have a look at the histogram of the speeds that is not averaged over the complete ride.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/htw_speed.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_speed.png" style="width:45%; padding: 10px">
</div>

This clearly shows that not only the average speed is higher for the road bike, there is also less time spent at slow speeds (meaning that I slow down/speed up faster).
Some of the city-bike distribution looks a bit strange, particularly the dip at ~10km/h.
But we'll accept this at face value for now, and will have a look at the next question{% include sidenote.html text='Similar to before, I am assuming that some of this might have to do with the difference in measurement setup - the velocity sensor that is in use on the road bike will make this definitely more accurate.'%}.

Next, we are looking at the question 'Where am I faster?'.
For that, I am plotting distance (i.e., 'where am I on the route') vs. speed.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/htw_speed_progress.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_speed_progress.png" style="width:45%; padding: 10px">
</div>

However, directly plotting the estimated elapsed distance vs speed gives obvious artifacts:
I would expect to be standing still (i.e. 0 velocity) at the same place (e.g., at traffic lights) for all the rides.
While it is _roughly_ the same places that the speed goes to 0, it seems a bit noisy, and might mess up some interpretations.

That being said, we can clearly see that I tend to go faster with the road bike.
Notably, on the way from work home, I was trying to get a KOM for a while - this is clearly visible - and now knowing that, this is also visibe in the speed-histogram above, where there is a bit more density at the ~40km/h part.

The reason for the misalignment could be two main things: 
- I am not starting the logging at the same place (and thus shifting the measurement)
- the sensor is inaccurate, and adds a bit of noise in the distance-measurement

To fix this, I am projecting the points in the gpx file onto a manually traced path, and copmute the moved distance from that.
That makes the graph above look like this:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/htw_projected.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_projected.png" style="width:45%; padding: 10px">
</div>

This still has a bit of noise, but the 0-velocity-points are much clearer now.

from that plot, we see that there is no clear single part of the commute where I am faster with my road bike - I am more or less consistently faster over the complete route.
To see a bit more, we can plot them separately instead of overlaying them.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/htw_projected_road.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_projected_road.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/htw_projected_city.png" style="width:45%; padding: 10px">
    <img src="{{ site.url }}/assets/strava-v2/wth_projected_city.png" style="width:45%; padding: 10px">
</div>

Again, in general it is visible that I tend to be faster everywhere with the road bike.
Additionally, it seems like there are a few places where I do not stop as often with the road bike.

# Conclusion
I am now fairly certain that I am actually faster with my road-bike, and this is not just due to the different measurement setup.

#### Further things to do with this data
- I have alsways wanted to figure out the optimal speed between two traffic lights. With the data I have of me riding (and stopping) between traffic lights, I should be able to figure out the time-delays the traffic lights have between them. Thus, I might be able to figure out where I have to ride a bit faster to still go over green - or the other way around: I can ride slower, and thus relax 'on the way' instead of just standing at the red light, because I rode too fast.
- When looking at the plots of the path, it becomes visible that there seems to be more noise on the measurements when I am in between buildings. While this is to be expected, it might be interesting to have an in-depth look at that.
