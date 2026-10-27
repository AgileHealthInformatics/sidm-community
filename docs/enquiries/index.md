---
{
  "layout": "page",
  "title": "Proposed projects and enquiries",
  "description": "Explore project proposals, related resources and their discussion spaces.",
  "resource_id": "enquiries-index",
  "section": "enquiries",
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
  "permalink": "/enquiries/"
}
---

Project entries describe proposals for consideration. A discussion link, where shown, opens the corresponding GitHub conversation; it does not signify SIDM or BCS endorsement.

<div class="cards">
{% assign projects = site.data.projects | sort %}
{% for pair in projects %}{% assign pid = pair[0] %}{% assign project = pair[1] %}
<a class="card" href="{{ project.permalink | relative_url }}"><span class="eyebrow">{{ pid | escape }} · {{ project.status | escape }}</span><h2>{{ project.title | escape }}</h2><p>{{ project.summary | escape }}</p></a>
{% endfor %}
</div>

## Preparing another project proposal

Repository maintainers can use **Actions → Create project proposal → Run workflow** to supply a title, question, scope and audience. The automation prepares a pull request for review; it does not publish an unreviewed project immediately.

[Read how the project automation works]({{ '/about/project-automation/' | relative_url }}).
