---
{
  "layout": "page",
  "title": "Project and discussion automation",
  "description": "How the demonstrator connects project proposals, discussions and related resources.",
  "resource_id": "about-project-automation",
  "section": "about",
  "status": "working-draft",
  "owner": "Proposal author: Dr Tito Castillo",
  "contributors": [],
  "last_updated": "2026-10-26",
  "last_reviewed": null,
  "next_review": "2027-01-26",
  "topics": [
    "participation"
  ],
  "source_versions": [],
  "ai_assistance": "AI-assisted implementation and documentation; subject to human review.",
  "permalink": "/about/project-automation/",
  "project_ids": []
}
---

## From a question to a project proposal

A repository maintainer completes **Actions → Create project proposal → Run workflow**. The form asks for a title, question, scope and audience, and whether a discussion should be established after merge. A unique project identifier and page are prepared automatically in a pull request.

The maintainer reviews the wording and the automated checks before merging. This review permits publication of the proposal; it does not constitute organisational endorsement or approval of an operational programme.

## Discussion creation and recovery

When publication and discussion automation are enabled, the next Pages build looks for a bot-created discussion containing the project identifier. It creates one only if none exists. Later builds recover the discussion number and URL, keeping the link on the project page current. Existing discussions can be explicitly adopted by recording their number once in the project register.

The automated opening section is refreshed from the register. Replies and text outside that section are preserved. A duplicate match stops the build for investigation rather than choosing a thread arbitrarily.

## Related content

Pages carry a list of project identifiers in their metadata. Those associations generate the related resources on each project page and the links back to projects on each resource. A resource can support several projects. Unknown identifiers fail validation.

## Responsibilities and limits

The form is available to repository users with permission to run workflows. It is not a public submission form for people without GitHub accounts. Ordinary contributors can still propose material through the repository's existing contribution routes.

Discussion creation requires repository Discussions and the agreed category to exist. An administrator enables the automation once. The existing pilot is supplied with discussion creation switched off until selected. No project conversations are created merely by downloading this package.

Discussion links are generated during publication rather than committed to the main branch. The source register remains the authoritative record of project scope; the discussion's stable project marker provides the persistent association. Publishing can fail after a discussion has been created; rerunning the workflow reuses that thread.
