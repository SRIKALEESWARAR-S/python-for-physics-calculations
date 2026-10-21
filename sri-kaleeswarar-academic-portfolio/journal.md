---
layout: default
title: Journal & Updates
permalink: /journal/
description: Research notes, project releases, articles, talks, and portfolio updates.
---
<section class="page-hero page-shell"><p class="eyebrow">JOURNAL</p><h1>Notes from the workbench.</h1><p class="lead">Short updates on experiments, software releases, writing, talks, and lessons learned.</p></section>
<section class="content-section page-shell"><div class="post-list">{% for post in site.posts %}<a class="post-row" href="{{ post.url | relative_url }}"><div><span class="post-meta">{{ post.date | date: '%b %-d, %Y' }} · {{ post.category | default: 'Update' }}</span><h3>{{ post.title }}</h3><p>{{ post.description }}</p></div><span class="row-arrow">↗</span></a>{% endfor %}{% unless site.posts.size > 0 %}<div class="empty-state"><span class="empty-star">✦</span><h3>Your first update starts here</h3><p>Create a Markdown file in <code>_posts/</code>. It will appear here automatically after the site builds.</p></div>{% endunless %}</div></section>
