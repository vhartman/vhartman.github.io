---
layout: post
title:  "Tracking route prices of the Deutsche Bahn"
date:   2019-12-14 12:31:34 +0200
categories: short scraping
---

Given that I currently live in Stuttgart, and have to (want to!) travel to Zurich regularly, I want to 

1. Book the cheapest route
2. Use the most comfortable route

Both 1. and 2. are usually fulfilled by rail transport, since there exists a direct connection that takes 3h, and is not much more expensive than using i.e. FlixBus. I will not go into the inconveniences that are cause by DB when trains simply do not arrive, arrive with a massive delay, or cause other unexpected difficulties.

<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: 0px;height: 300px;padding: 10px;font-size:10pt; width:200px"><sup>1</sup> <a href="https://www.ke.tu-darmstadt.de/lehre/arbeiten/bachelor/2013/Hirschmann_Fabian.pdf">Here (pdf)</a> is a bachelors thesis that gives a brief introduction on the pricing in the context of building a machine learning model to predict prices for some routes. 
</p>
</div>
How the pricing of routes works is apparently not a straightforward question in itself, even if we neglect the time dependency of the price<sup>1</sup>.

Growing up in Switzerland, I am used to a fixed price per route - no matter when I book the ticket, the cost for a route is the same (assuming the same means of transport, meaning no other via-points. The cost of a route can vary throughout the day though). In Germany, this is not necessarily the case. Thus, I wanted to figure out the ideal time for the purchase (Spoiler: the obvious "buy as soon as possible" seems to be the best strategy according to the data I gathered so far). 

<div style="position: relative;" class="post-side-image">
    <p style="position: absolute;left: 720px; top: 0px;height: 300px;padding: 10px;font-size:10pt; width:200px"><sup>2</sup> The scripts for the tracking and the visualization can be found <a href="https://github.com/vhartman/db-cost-tracking">here</a>. 
</p>
</div>
I wrote a script<sup>2</sup> to scrape the prices for a few of the connections that I am interested in from the website, and added a cronjob to run the script every hour. (I realized later on that Google Flights can track the cheapest connection for this route via rail as well - oh well). Since I am running the script so often, made sure that the price change is not a personal one (i.e. caused by repeatedly looking up the same connection) by checking with a different computer from a different location.

The resulting pricing data for a month for one of the connections is below:

<div style="width: 100%; text-align: center">
    <img src="{{ site.url }}/assets/db-tracking/040120_initial.png" style="width:100%;padding: 10px;">
</div>

Some initial observations:
- The price is not strictly increasing the closer we get to the date of travel
- Different iternaries behave differently over time

Comparing this to some more collected data (I only scraped the connections/days that are actually relevant for my upcoming travel to Switzerland over the christmas holidays):

<div style="width: 100%; text-align: center">
    <img src="{{ site.url }}/assets/db-tracking/full.png" style="width:100%;padding: 10px;">
</div>


Some hypotheses how the pricing over time works:
1. Depending on the occupation of the trains, i.e. previously sold tickets
2. Depending on the time remaining to the date of the connection
3. Depending on predictions of 'normal' usage during a certain day.

All of these attempts to explain the price changes over time are partially refuted by the fact that some of the prices dropped again after an increase. A generally sensible approach to pricing is to increase the cost the scarcer the resource ('a seat in the train') gets, but this does not explain the falling cost after a price hike either.

It might be possible that the number of ticket sales is naively extrapolated from the prvious sales, causing some jumps in prices, and going back to the previous level after a 'calmer' period.

If anybody knows more about the topic, please reach out to me!

**Edit:** Apparently some railway operators use a strategy called [yield management](https://en.wikipedia.org/wiki/Yield_management) to maximize revenue for a given route (according to [trainline](https://faq.trainline.eu/article/192-sudden-ticket-price-increase-decrease)). While common practice with airlines, I was not aware that this is done for rail as well.
