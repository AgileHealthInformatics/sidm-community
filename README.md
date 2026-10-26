# SIDM community repository

A complete starter for a proposed SIDM body of work: a Jekyll website, contribution templates, pilot enquiry, AI review method, validation scripts and GitHub Pages workflow.

**Status:** proposal for review. No GitHub repository or website has been created remotely. No organisational endorsement, partnership, named appointment or completed standards analysis is claimed. No confidential minutes or action trackers are included.

## Start here

1. Read `SETUP.md` and agree ownership, editorial contacts and reuse terms.
2. Import this folder into an empty organisation-owned GitHub repository.
3. Set `repository_url` and `contact_email` in `docs/_config.yml`.
4. Configure Pages, reviewers and branch protection as described in `SETUP.md`.
5. Review the starter content before enabling public publication.

## Local build

Install Ruby and Bundler, following https://jekyllrb.com/docs/installation/.

```sh
bundle install
bundle exec jekyll serve --source docs --config docs/_config.yml --baseurl ""
```

Open http://localhost:4000. Configuration and source pages are in `docs/`. Generated output is `_site/` and is not committed. The Gemfile targets Jekyll 3.10 for compatibility with the Pages Jekyll build action. Commit a generated `Gemfile.lock` after the first successful local install if using Bundler for reproducible local builds; the supplied CI uses the Pages action's own dependencies.

## Checks

```sh
python scripts/validate_content.py
python scripts/review_dates.py
bundle exec jekyll build --source docs --config docs/_config.yml --baseurl /sidm-community
python scripts/check_site.py _site --baseurl /sidm-community
```

Python 3.11+ is recommended; checks use only the standard library. Front matter is JSON between YAML delimiters, which is valid YAML and enables dependency-free checks. Preserve this format when using the templates.

## Contents

- `docs/`: public pages, layouts, navigation, CSS and downloads.
- `templates/`: editorial and AI prompt templates; not built into the site.
- `scripts/`: metadata, generated-site link and review-date checks.
- `.github/`: CI, deployment, scheduled maintenance and contribution forms.
- `SETUP.md`, `MAINTENANCE.md`: technical and editorial runbooks.

The site has no analytics, external fonts, API calls or AI service integration. AI support is a documented human-led method. Administrative settings and external accounts cannot be embedded in a ZIP.
