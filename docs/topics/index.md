---
{
  "layout": "page",
  "title": "Topic index",
  "description": "Find connections across the body of work.",
  "resource_id": "topics-index",
  "section": "topics",
  "status": "working-draft",
  "owner": "SIDM editorial team (assignment pending)",
  "contributors": [],
  "last_updated": "2026-10-26",
  "last_reviewed": null,
  "next_review": "2027-01-26",
  "topics": [],
  "source_versions": [],
  "ai_assistance": "AI-assisted starter content; subject to human review.",
  "index_page": true,
  "permalink": "/topics/"
}
---

{% assign all_topics = site.pages | map: 'topics' | join: ',' | split: ',' | uniq | sort %}
{% for topic in all_topics %}{% if topic != '' %}
<h2>{{ topic | escape }}</h2><ul>{% assign entries = site.pages | sort: 'title' %}{% for entry in entries %}{% if entry.topics contains topic %}<li><a href="{{ entry.url | relative_url }}">{{ entry.title | escape }}</a></li>{% endif %}{% endfor %}</ul>
{% endif %}{% endfor %}
