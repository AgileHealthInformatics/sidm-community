# Project and discussion automation

Implementation update for the SIDM proposal demonstrator, 26 October 2026.

## What is implemented

A maintainer completes a GitHub Actions form. Automation creates a project identifier, a landing page and a project-register entry on a new branch, then opens a pull request. After human review and merge, the normal Pages build can create the proposal discussion, generate its website link and list related resources automatically.

No GitHub Projects board is required. These are SIDM enquiry projects, represented by repository metadata and public pages. Discussion creation does not imply approval of a work programme or BCS endorsement.

## Install the update

1. Pull any outstanding remote changes into your Windows checkout before applying this package. Preserve any uncommitted work first.
2. Extract the ZIP into `C:\Users\TitoCastillo\projects\sidm-community`, merging folders and replacing matching files. Files belong directly under the repository root, not in an extra nested folder. Include `.github` and `.gitignore`.
3. Review `git diff`. The update retains the corrected dynamic Pages base-path behaviour and the proposal notices. It does not replace your site configuration or home page.
4. Commit and push the supplied changes. Wait for **Check contribution** to pass. The package does not activate repository settings or create discussions by itself.

```powershell
cd C:\Users\TitoCastillo\projects\sidm-community
git add .github docs scripts templates tests .gitignore AUTOMATION.md AUTOMATION_VALIDATION.md
git commit -m "Automate project proposals and discussion links"
git push
```

## One-time GitHub setup

### Enable discussions and select a category

In repository **Settings → General → Features**, enable Discussions if not already enabled. Use the existing **General** category for the pilot, or create a category for project proposals. Categories are managed by people; this automation does not create them.

### Add repository variables

Under **Settings → Secrets and variables → Actions → Variables**, configure:

| Variable | Value |
|---|---|
| `PUBLISH_SITE` | `true` to publish, as already configured |
| `PROJECT_DISCUSSIONS_ENABLED` | `true` to allow the publisher to establish and refresh project discussions |
| `PROJECT_DISCUSSION_CATEGORY` | The exact category name, for example `General` |

These are repository variables, not secrets. The built-in `GITHUB_TOKEN` supplies authentication, so no personal access token is needed. The workflow explicitly requests the permissions it needs.

### Permit creation of proposal pull requests

Under **Settings → Actions → General → Workflow permissions**, enable **Allow GitHub Actions to create and approve pull requests**. Although GitHub's setting refers to approvals, the supplied automation only creates PRs; it never approves or merges them. Organisation policy may control this setting.

Retain human review and branch protection. A bot-created PR may display **Approve workflows to run**. Select that when appropriate, wait for **Build and validate**, then review and merge. No direct writes to `main` or branch-protection bypass are required.

## Create a project

1. Open **Actions → Create project proposal → Run workflow** on `main`.
2. Enter a title, question, scope and intended audience.
3. Leave **Create a proposal discussion after this PR is merged** selected if a discussion is wanted.
4. Run the workflow. Its summary links to the generated pull request.
5. Review the page and project register. Approve CI when prompted, wait for checks, and merge.
6. The resulting Pages build creates or finds the discussion and displays **Discuss this proposal on GitHub** on the project page.

The identifier is `ENQ-` followed by the workflow run ID. This is unique across requests and stable across reruns, without a fragile shared sequence counter. The folder and URL use the same identifier. The human-readable title can change without changing the URL.

The form is a GitHub Actions manual-dispatch form, available to maintainers with workflow-running access. It is not an anonymous form on GitHub Pages. Contributors without that access can use the existing enquiry issue template; a maintainer can turn the agreed proposal into a project using the form.

## Existing pilot ENQ-001

The register includes the current data-definitions pilot and associates its evidence, findings, AI method and review checklist. Its `discussion_requested` value is **false**, so importing the update does not start a pilot conversation automatically.

If no discussion exists, change that value to `true` in `docs/_data/projects.json`, review and merge. If you already created a discussion manually, instead set `discussion_number` to that thread's number, obtained from its GitHub URL. The publisher adopts that thread without altering its opening message. No reciprocal link copying is needed for the website; add a project-page link to a human-owned opening message if desired.

## Associate resources with projects

On a resource page, add the identifier to JSON front matter:

```json
"project_ids": ["ENQ-001"]
```

A resource may belong to several registered projects. The site automatically produces:

- Related resources on each project landing page.
- Related projects on each resource.
- A project index generated from the register.
- A discussion button whenever the generated link record is available.

Only a landing page has the singular `project_id` field. New project pages generated by the form include both fields automatically. Identifying which project a resource belongs to remains an editorial decision; the automation maintains the resulting links and indexes.

## Data and ownership

| File or record | Role |
|---|---|
| `docs/_data/projects.json` | Authoritative project descriptions, landing paths and discussion request flags |
| Project page front matter | Page identity and project membership |
| Discussion marker `<!-- sidm-project:ENQ-001 -->` | Persistent project-to-discussion association in GitHub |
| `docs/_data/project_discussions.json` | Derived number/URL mapping, generated during a build and ignored by Git |
| `project-discussion-links` workflow artifact | Diagnostic snapshot of the derived mapping |

The register's question, scope and audience are authoritative for the generated discussion opening. The initial page copies those fields when created; subsequent prose changes to a page do not silently change project scope in the register. Review both when changing scope.

The build-generated mapping deliberately avoids a second bot commit or PR just to record a discussion number. It also avoids the problem that a push using `GITHUB_TOKEN` does not automatically start another Pages build. The existing Pages build publishes the mapping and the pages together.

## Recovery and reruns

Discussion discovery paginates through the repository and matches both the stable project marker and the GitHub Actions bot identity. Rerunning a build reuses the existing discussion. It does not rely on the previous artifact being available.

If a build fails after creating a thread, fix the failure and rerun **Publish Pages** on `main`; the thread is recovered. Do not delete and recreate it to retry. Mutation calls are not retried automatically after ambiguous network errors.

The opening message contains `sidm-generated:start` and `sidm-generated:end` boundaries. The build refreshes that section and title from the register, preserving replies and text outside the boundaries. Do not edit the generated section directly. Removing its boundaries fails the build rather than overwriting the thread. An explicitly adopted thread is never rewritten.

Multiple matching bot discussions fail closed. Choose the authoritative thread by setting `discussion_number` and resolve duplicates separately. Closed or deleted threads are not automatically managed; if an explicit number is missing, the build stops with an actionable error. An archived project does not get a new discussion, but an existing association can remain visible.

A rerun of **Create project proposal** returns the existing PR, including if it is closed. To intentionally propose another project, start a new workflow run. If a partially completed run left a branch but no PR, matching contents can be reused; differing content is not overwritten. If `main` advanced between checkout and preparation, rerun against its current state.

## Disabled and local modes

With discussion automation disabled, no GitHub API calls are made by the sync step. The project page shows that a discussion is not connected in the preview. A local build uses this offline mode by default. Set the variable to true and republish to restore the live links.

No discussion is created when `PUBLISH_SITE` is disabled, because synchronisation is part of the gated Pages workflow. Discussions and website publication are public operations once the administrator enables them and a ready project is merged.

## Transfer and domain changes

The publisher obtains the Pages base URL from `configure-pages`, so it supports project paths, root sites and custom domains. A later build refreshes the generated backlink if that URL changes. After a repository transfer, review organisation permissions and category configuration, then rerun the publisher.

## Files and checks

- `scripts/project_model.py`: metadata validation and safe page scaffolding.
- `scripts/project_automation.py`: project PR creation, discussion discovery and synchronisation.
- `scripts/set_base_path.py`: the corrected Pages base-path configuration.
- `.github/workflows/create-project.yml`: the maintainer form.
- `.github/workflows/pages.yml`: discussion synchronisation and publication.
- `.github/workflows/ci.yml`: project checks, tests and project-path link validation.
- `tests/test_project_automation.py`: mocked-API and local behavioural tests.

```sh
python scripts/validate_content.py
python scripts/project_automation.py validate
python -m unittest discover -s tests -v
python scripts/project_automation.py sync
```

The last command defaults to offline mode unless enabled through environment variables. Never put a token in a tracked file.

## Reference documentation checked

- https://docs.github.com/en/actions/concepts/security/github_token
- https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- https://github.com/actions/configure-pages/blob/main/action.yml
