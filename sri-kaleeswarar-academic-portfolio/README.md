# Sri Kaleeswarar S — Academic Portfolio

A soft pastel, magenta-and-blue academic portfolio built with Jekyll for free GitHub Pages hosting. It includes pages for research/projects, writings, outreach, achievements/CV, contact, and a journal that updates automatically from Markdown posts.

## Before publishing

1. Create a GitHub repository. For a project site, e.g. `sri-kaleeswarar-site`, upload all files in this folder to the repository root.
2. Edit `_config.yml`:
   - `url`: `https://YOUR-GITHUB-USERNAME.github.io`
   - `baseurl`: `/YOUR-REPOSITORY-NAME` (keep the leading slash). If your repository is exactly `YOUR-GITHUB-USERNAME.github.io`, set `baseurl: ""`.
3. Edit `contact.md` and replace `YOUR-PUBLIC-EMAIL@example.com` with a public email address. Update all placeholder links and verify every achievement and date.
4. Put your latest PDF CV at `assets/files/CV.pdf`, or remove the CV button in `index.html` until you have uploaded it.
5. In GitHub repository Settings → Pages, choose **Deploy from a branch**, select `main` and `/(root)`, and save.
6. Wait for the Pages deployment to finish. The website URL will be shown under Settings → Pages.

## Easiest way to add an update

Create a new Markdown file in `_posts/` using the format `YYYY-MM-DD-short-title.md`:

```markdown
---
layout: post
title: "A new research note"
date: 2026-10-20
category: Research
description: "A one-sentence summary that appears in the post list."
tags: [physics, python]
---

## Motivation
Write what question you explored.

## Method
Describe the approach and link your code/data.

## Results and limitations
Report results honestly, including what has not yet been validated.
```

Save, commit, and push. GitHub Pages will rebuild the site and add the post to the home page and journal automatically. You can also create/edit the file through GitHub's web editor; commit the change when done.

## Add a project

For the first version, edit `research.md` and duplicate a project card. Keep repository links, status, and project claims accurate. A later version can move projects into a Jekyll collection so each project gets its own Markdown page.

## Local preview (optional)

GitHub Pages uses Jekyll. If you have Ruby installed, run:

```bash
bundle install
bundle exec jekyll serve
```

Open `http://127.0.0.1:4000` in your browser. If the `github-pages` gem install is too heavy on your laptop, you can skip local preview and let GitHub Pages build it online.

## Content checklist

- [ ] Replace the example GitHub Pages URL and repository base path.
- [ ] Add a professional photo if you want one (optional).
- [ ] Upload the latest CV.
- [ ] Add email and only public professional profiles.
- [ ] Link projects to source code, documentation, releases, and reproducible results.
- [ ] Add publication links instead of copying copyrighted articles.
- [ ] Distinguish completed results, preliminary experiments, and future plans.
- [ ] Test the site on mobile and check every link after deployment.

## Design

White background, soft magenta bubble motifs, pastel blue panels, rounded glossy cards, subtle gradients, and responsive mobile navigation inspired by the soft visual style of Office 2007. No external JavaScript framework is required. Google Fonts is optional; system fonts will be used if unavailable.
