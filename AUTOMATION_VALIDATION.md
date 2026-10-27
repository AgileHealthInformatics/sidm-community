# Automation validation

26 October 2026

Completed:

- 32 local behavioural tests passed using mocked GitHub APIs. Coverage includes project creation, PR creation, stale-checkout rejection, reruns, pagination, duplicate detection, failed-publication recovery, bot identity handling, adoption of existing threads, preservation of human annotations, archived/paused projects, invalid references and safe handling of form text.
- Metadata validation passed for 21 pages and the project register.
- Workflow YAML and Python syntax checked.
- Literal internal page links resolved against permalinks and assets.
- Git diff whitespace checks and update ZIP integrity passed.

Not verified live:

- GitHub API mutations and token permissions in this repository. The connected integration previously returned HTTP 403 on writes; no remote changes or discussions were created.
- Full Jekyll rendering or browser layout for the new Liquid includes. Ruby is unavailable in this environment. The updated CI builds the site and checks generated links using a project base path.
- Deployment or repository settings. Follow AUTOMATION.md and require the first CI run to pass before using the form.

This is an implementation update, not a statement that the service is configured or running.
