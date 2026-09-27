# K-House site scaffold

Standalone static site for K-House, a flexible Exeter jazz group.

## Local preview

Open `index.html` directly in a browser, or serve this folder and visit:

`http://localhost:8000/`

## Netlify publishing

Target free URL:

`https://kay-house.netlify.app/`

Suggested setup:

- Create a new Netlify site from this folder.
- Set the base directory to `K-house` if connecting the full `music` repo.
- The included `netlify.toml` publishes the current folder.
- `k-house` was not available through the Netlify CLI at deploy time, so the live site is `kay-house`.

Netlify Forms should detect `bandmates.html` after deploy and collect submissions for the `bandmate-input` form.

## Pages

- `index.html` - public band page.
- `bandmates.html` - unlisted, noindex input/comment form for bandmates.
- `thanks.html` - form submission confirmation page.

## Edit checklist

- Replace `images/k-house-group.png` when a stronger performance or group photo is available.
- Add real recordings in the listen section.
- Add confirmed gigs in the gigs section.
- Replace draft lineup descriptions with final member names and bios.
- Confirm whether the public name should be `K-House`, `Kay House Trio`, or another variant.
