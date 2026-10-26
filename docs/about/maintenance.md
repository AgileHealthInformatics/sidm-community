---
{
  "layout": "page",
  "title": "Maintaining the site",
  "description": "An editorial process supported by automated publishing.",
  "resource_id": "about-maintenance",
  "section": "about",
  "status": "working-draft",
  "owner": "SIDM editorial team (assignment pending)",
  "contributors": [],
  "last_updated": "2026-10-26",
  "last_reviewed": null,
  "next_review": "2027-01-26",
  "topics": [],
  "source_versions": [],
  "ai_assistance": "AI-assisted starter content; subject to human review.",
  "permalink": "/about/maintenance/"
}
---

| Responsibility | Work |
|---|---|
| Editorial coordinator | Triage contributions, assign reviewers and maintain the publication queue. |
| Resource owner | Check sources, respond to comments and review the resource when its subject changes. |
| Technical maintainer and deputy | Maintain configuration, dependencies, permissions and the publishing workflow. |
| Steering group | Set priorities, appoint owners and handle endorsement decisions. |

## Monthly editorial review

Review new suggestions and stalled contributions. Run the review-date report and allocate overdue reviews. Choose work according to its importance and available ownership rather than filling every section of the site.

## Quarterly technical review

Review access and dependency updates. Confirm the deputy can build and deploy the site. Check broken links and ensure the repository can be cloned and rebuilt. Follow the operational runbook in `MAINTENANCE.md`.

## Publication

Proposed changes are checked before acceptance. Merging into the main branch triggers a fresh build and Pages deployment. Repository administrators must configure required review and checks before public launch. The workflow files alone do not enforce those repository settings.
