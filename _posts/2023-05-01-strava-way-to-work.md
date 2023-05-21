---
layout: post
title:  "How much quicker am I on my road bike compared to my city bike?"
subtitle: "or: Is that all a measuring artifact?"
date:   2023-02-20 12:00:00 +0200
permalink: /speed/
categories: data
---

<p class="preface">
    Strava recently suggested to me that I am roughly 3 minutes faster on my ~15 min way to work if I use my road bike compared to my old vintage city bike.
    I wanted to double check.
</p>

# Preface
The weather is getting nicer again here in Berlin, which means that my cycling habit makes me take my road bike for riding to work.
I log most of my rides on strava, including my way to work.
Strava has a feature that tells you if you have been faster or slower on a given route if you have ridden this route before.

After dusting off my road bike and riding it to the university, strava told me that I am much faster with my road bike:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/commute_time.png" style="width:100%; padding: 10px">
</div>

That graph prodded me to have a look at the data to figure out if I am really that much faster (I could save 3 minutes of my 15 minutes commute twice a day!), or if that is some measurement artifact.

#### A bit of background
On my roadbike, I have a bike computer, on my city bike, I am using my phone to log my riding.
The bike copmuter has the more accurate GPS (or it does better filtering of the data?), and also has some other sensors which make the data more accurate overall I suspect (among them a velocity sensor).

The data that strava uses to compile the graph above is the _riding time_. That is, not the time from door to door, but the time I spent actually riding.
Since there is a difference in measurement setup, I suspect that the more accurate data could lead to a lower riding time, as the time spent waiting at traffic lights can be more accurately be subtracted.
Stated differently, I believe that the riding time is overestimated when the phone is the data source.

All that being said, riding the road bike definitely feels faster.

# Looking at the data
Strava lets me export all my data {% include sidenote.html text='Partially due to GDPR. This download was possible before as well, but you get more data now.'%} and gives it to me in a zip file.

There is lots of stuff that I do not need in there - for the analysis here, I will rely on the files of the activities, and the 'activities.csv' file.

The most obvious initial step is to check if the trend that holds for the moving time also holds for the elapsed time.

For that, we need to filter the activities by bike, and by 'is this a commute?'.

For some reason, my rides on strava that are created by the bike computer are named in english, while the ones from my phone are in german.
Thus, the first filtering criteria can be achieved by simply looking for 'ride' in the activity name.

The second one is a bit more involved{% include sidenote.html text='In theory, it is possible to mark rides as commutes. In practice, I only do that for rides recorded with my phone.'%}.
We could probably get a reasonable proxy by filtering by activity length.
I do take a slightly different route, and will have a look at the start and the end coordinates of the activity, and check if that corresponds to my home, respectively work-coordinate.

Before being able to look at coordinates, we need to convert the '.fit.gz' files from the bike computer to '.gpx' files.
I did this using the python library [fit2gpx](https://pypi.org/project/fit2gpx/).
To then work with the gpx files, I used [gpxpy](https://pypi.org/project/gpxpy/).

#### Filtering the rides
To check if my ride starts at home/ends at the university and vice-verca, I am comparing the start-coordinate and the goal-coordinate with the coordinate of my home, and the coordinate of my working place (the university).

Only plotting the rides in question gives roughly this:

[Plot of all bike rides]

Here, I colored the rides to the university in green and the ones back home red.

With the bikes distinguished, and the rides filtered, so we are only considering the ones that actually go from university to home, and the other way, we can make pretty histograms of the elapsed time between start and end:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/moving_time_histogram.png" style="width:100%; padding: 10px">
</div>

we can also plot histograms of the average speed for both ways:

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/speeds.png" style="width:100%; padding: 10px">
</div>

To ensure that I am not simply starting the logging later (and thus shortening the path), we can have a look at the histogram of the distances:

[]

Also, going back to the paths above, and coloring the rides the same as in the histograms, we can zoom in a little bit to see where the paths start and end respectively:

[...]

With all these plots, I think I can fairly confidently answer the question posed above: yes, I am quicker with the road bike: roughly 3 minutes.

Of course, correlation does not imply causation.
The 'being faster' could for example be caused by only taking the road bike on days with good weather (which is the case as mentioned in the beginning - I am not taking the nice road bike in rain etc.).

# Going deeper
Rather than only answering the question I posed initially, I am also interested in the question why I am actually faster with the road bike.
As alluded to above, this is likely very hard to answer.
Is it the better tires of the bike? Is it the better weather? Am I more aerodynamic?

One thing that might help answer this, is looking at moving time vs elapsed time.
That might help give some information on time spent at traffic lights etc., and possibly tell me if I am just spending more time accelerating/decelerating with the older bike.

<div style="width: 90%;margin:auto">
    <img src="{{ site.url }}/assets/strava-v2/timediff_histogram.png" style="width:100%; padding: 10px">
</div>

Here, we can see that the difference in moving and elapsed time does not differ much between the road bike and the city bike.
One notable mention is that there is a long tail on both ways on the way from home to the university, but only for the city bike on the other way.
The long tails correspond to me getting a doner (on my way to work, for lunch), and going shopping.
If I am taking my road bike, I am not going shopping, since I don't like leaving my road bike unattended.

This plot tells me that I am spending roughly the same time 'not moving' for both types of bikes.

Next, we are looking at the intermediate question 'Where am I faster?'.
I suspect that I am actually not _that much_ faster with the road bike, but just fast enough to not get held up by a few traffic lights, which avoids decelerating/accelerating, and thus save a bunch of time.

For that, I am plotting distance vs speed.
However, directly plotting the estimated elapsed distance vs speed gives obvious artefacts:

[plot speed vs dist not-so-nice]

Typically, I would expect to be standing still at the same place in all cases (i.e. at a traffic light).
What is happening here could be two things: 
- I am starting the logging too late
- the sensor is inaccurate, and thus adding a bit of noise in the measurement

To fix this, I am starting the distance measurement from a fixed coordinate, and I am projecting the points in the gpx file onto my actual path when computing the moved distance.
That makes the graph above look like this:

[PLot speed vs dist nice]

