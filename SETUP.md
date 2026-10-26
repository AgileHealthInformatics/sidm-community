# Setup and launch

## 1. Ownership and import

Agree the organisation account, two administrators, editorial coordinator and technical deputy. Create an empty repository with default branch `main`. Extract the archive and upload **all contents of the sidm-community folder**, including `.github` and `.gitignore`; do not upload the enclosing folder as an extra directory. Git is the most reliable way to preserve dotfolders.

```sh
git init -b main
git add .
git commit -m "Add SIDM community starter"
git remote add origin https://github.com/YOUR-ORGANISATION/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote address with the actual repository. A public repository exposes all tracked files and history, not just the site output.

## 2. Configuration

In `docs/_config.yml`, set `repository_url` to the repository HTTPS URL (no trailing slash) and `contact_email` to the agreed public editorial address. Set `url` to the site's origin if desired. Do not hard-code a repository name in content links: use `relative_url` as the templates do. The Pages workflow obtains the base path automatically, supporting project sites and custom-domain/root sites.

Review content, appoint owners and agree licensing before launch. `LICENSE.md` is intentionally a decision record rather than an unauthorised grant of rights. Do not add official logos or claim BCS approval without the appropriate agreement.

## 3. Turn on publication

Pages deployment is disabled by default. This allows the first push to run CI without immediately publishing the proposal.

1. Under Settings > Pages, choose GitHub Actions as the source.
2. Under Settings > Secrets and variables > Actions > Variables, add the repository variable `PUBLISH_SITE` with value `true` when ready to publish.
3. Run **Publish Pages** manually on `main`, or merge a change into `main`.
4. Inspect the run and use its deployment URL. No custom domain is required.

The workflow builds `docs/` using `docs/_config.yml`, validates generated internal links and uploads only `_site/`. A separate deployment job publishes that artifact. Do not change the artifact path to the repository root.

## 4. Review controls

Replace commented examples in `.github/CODEOWNERS` with real organisation teams or usernames that have write access. In branch protection or a ruleset for `main`, require pull requests, one approving reviewer, dismissal of stale approvals and the **Build and validate** status check. Require code-owner review once assignments are valid. Restrict bypass permissions. Protect `.github/` changes as well as content.

Under the `github-pages` environment, restrict deployments to `main`. Configure approval if required by the agreed governance. Settings availability can vary by account plan; verify the controls actually apply. The ZIP cannot configure these account settings.

## 5. Launch checks

- Confirm the configured editorial contact works and has consented to publication.
- Review the home page, pilot scope and draft status language.
- Confirm licensing and source permissions.
- Check desktop and mobile layouts, keyboard navigation and download links.
- Open a test pull request and confirm checks/reviews apply.
- Verify a merged correction publishes and the deputy can follow the runbook.

Remove the global starter notice in `docs/_layouts/page.html` only after the site framing is agreed. Page-level resource status should remain visible.

## Documentation

- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- https://jekyllrb.com/docs/
