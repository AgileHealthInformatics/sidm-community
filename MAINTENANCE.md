# Maintenance runbook

## Routine edits

Copy a template into the appropriate `docs/` folder. Update JSON metadata, body and source references. Section and topic indexes update automatically. To add a top-level section also update `docs/_data/navigation.yml`. Downloadable files belong in `docs/assets/downloads/`.

## Monthly editorial review

Run `python scripts/review_dates.py`. Review the report, new issues and stalled pull requests. Assign owners and reviewers. A passed build is not substantive review. Update `last_reviewed` only after an actual review; changing `last_updated` does not reset it. Archived pages remain accessible with their status visible.

## Technical maintenance

Review Dependabot proposals and changes to action versions before merging. The Jekyll Pages build action controls CI Ruby dependencies; its environment can evolve independently of the local Gemfile. Review the Pages action release notes and test builds after upgrades. Re-check permissions quarterly and ensure a deputy can operate the site.

Run **Review dates and external links** manually or inspect its monthly report artifact. External link failures are advisory: rate limits, login pages and bot protection can produce false positives. Do not auto-delete resources on that basis. Reports do not automatically create issues or notify the editorial team beyond normal Actions behaviour; the coordinator must review them.

## Failed publication

Open Actions, identify the failing step and inspect its log. Fix the source in a pull request. Do not disable checks to force publication. A failed build leaves the last successful deployment in place. For a missing stylesheet or navigation path, check the Pages base path and the use of `relative_url`.

## Rollback

Revert the problematic merged commit through a reviewed pull request. Merge the revert to rebuild and deploy the previous source state. For a serious accidental disclosure, stop publication and escalate to repository administrators: reverting does not remove sensitive material from Git history, artifacts or caches.

## Continuity

The repository is the source of truth. Keep an independent clone or agreed backup and record account ownership outside the public repository. A custom domain, if introduced, needs documented ownership and renewal arrangements. Keep confidential committee records in a separate authorised system.
