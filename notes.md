---
# You don't need to edit this file, it's empty on purpose.
# Edit theme's home layout instead if you wanna make some changes
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
layout: default
permalink: /notes/
---

<h2>Notes</h2>

This page is a loose collection of some thoughts, collection of links for specific topics, and sometimes drafts for posts that might graduate to the other page at some point.

<ul class="post-list">
  {% assign sorted = site.notes | sort: 'date' | reverse  %}
  {% for note in sorted %}
    <li>
      <h3 style="position: relative">
        <span class="post-meta" style=" position: absolute; width: 120px; top: .6em; left: -90px; ">
              {{ note.date | date: "%b %-d %Y"}}</span>
          <a class="post-link" href="{{ note.url }}">
            {{ note.title }}
          </a>
        </h3>
    </li>
  {% endfor %}
</ul>

