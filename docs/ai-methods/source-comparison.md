---
{
  "layout": "page",
  "title": "Comparing specifications with AI",
  "description": "A reproducible method with explicit human verification.",
  "resource_id": "ai-methods-source-comparison",
  "section": "ai-methods",
  "status": "working-draft",
  "owner": "SIDM editorial team (assignment pending)",
  "contributors": [],
  "last_updated": "2026-10-26",
  "last_reviewed": null,
  "next_review": "2027-01-26",
  "topics": [
    "AI",
    "assurance"
  ],
  "source_versions": [],
  "ai_assistance": "AI-assisted starter content; subject to human review.",
  "permalink": "/ai-methods/source-comparison/",
  "project_ids": [
    "ENQ-001"
  ]
}
---

## Prepare

Record source title, publisher, version, date, authoritative URL and the passages selected. Check processing permissions. Use public or authorised material only. Preserve tables, units, qualifiers and cardinalities; check extraction against the original layout.

## Analyse

Use the prompt in `templates/prompts/source-comparison.md`. Ask for candidate findings tied to the supplied source identifiers and clauses. Require the model to distinguish missing evidence, different scope and possible contradiction. Do not let the model invent absent citations.

## Verify

A human reviewer examines every candidate against the original specification. Record accepted and rejected findings as well as unresolved questions. Check a sample of source clauses independently for issues the model missed; verification of flagged issues alone cannot establish completeness.

## Record and evaluate

Record the model and version as reported by the service, execution date, prompt version, supplied sources and material settings. Do not claim exact repeatability for a changing hosted model. Record time spent preparing inputs and checking results, including corrections. Compare with a small independent manual review before making claims of time savings or improved coverage.

## Publish

Publish the permitted evidence, human decisions, limitations and useful method. Raw outputs are working material and should be shared only where appropriate. Do not present fluent summaries as consensus or formal standards interpretations.
