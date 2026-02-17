## Installation

1. **Copy the repo to your machine** — Clone the repository so you have the project locally.

   **Using SSH** (preferred; requires SSH key setup—see [Adding a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)):
   ```bash
   git clone git@github.com:DataCenterEnergyMonitor/dashboard.git
   cd dashboard
   ```

   **Using HTTPS** (no SSH key required):
   ```bash
   git clone https://github.com/DataCenterEnergyMonitor/dashboard.git
   cd dashboard
   ```

2. **Create the conda environment** — From the project root:
   ```bash
   conda env create -f environment.yml
   ```

3. **Activate the environment**:
   ```bash
   conda activate dcewm
   ```

4. (Optional) **Register the Jupyter kernel** for use with Jupyter notebooks and Quarto (.qmd) files with built-in python code chunks:
   ```bash
   python -m ipykernel install --user --name dcewm --display-name "dcewm"
   ```

## Run the app

From the project root with the `dcewm` environment activated:

```bash
python src/server.py
```

The dashboard is served at `http://0.0.0.0:8050` (or `http://localhost:8050`).

## Build prerequisites

When the **global_policies** dataset is updated, refresh the geocoding cache so map locations stay in sync:

1. Ensure the conda environment is activated (`conda activate dcewm`).
2. From the project root, run:
   ```bash
   python scripts/update_geocoding_cache.py
   ```

2. **Render Quarto files to HTML** (data/methodology static pages). Requires [Quarto](https://quarto.org/) installed separately. 
From the project root:
   ```bash
   cd src/static_pages && quarto render
   ```
   Output is written to `assets/static_pages/`.
   
3. Remove the folder `assets/static_pages/site_libs`. This prevents Quarto’s default site styles from overwriting the dashboard’s site-wide styles.
Run from the project root.
   ```bash
   rm -rf assets/static_pages/site_libs
   ```

4. Create the data directories (at project root, not under `src`):
   ```bash
   mkdir -p data/dependencies
   ```

5. **Load core data files** into `data/`. 
Place supporting files such as geocoding cache, GeoJSON, and metadata under `data/dependencies/`.

## Project structure

High-level layout of the DCEWM dashboard. Build artifacts (`__pycache__`, `.pyc`), temp files (`~$*`), and archive copies are omitted.

**Shared vs feature-specific** — Changes to **shared** files affect the whole app or many features; coordinate with teammates and notify before editing (see [Code Change Process Flow](#code-change-process-flow)). **Feature-specific** areas can be owned by one person per feature; less coordination needed as long as one lead per feature.

#### Shared files (central registration)

These files contain the code that connects **all** features to the app (imports, routes, menu, data loading). They are updated whenever a new feature is added and are the main source of merge conflicts. **Notify the team before editing** and follow the practices below.

| File | Why it's central | What you add for a new feature |
|------|------------------|---------------------------------|
| **`src/app.py`** | Single entry point: imports every page and callback, loads all datasets, registers callbacks, defines routing | New `from pages...` / `from callbacks...` imports; new `load_*()` calls and variables; new entries in `data_dict` and `chart_configs` (if the feature has charts); new `register_*_callbacks(...)`; new `elif pathname == "/your-route"` in `display_page`; optionally `kpi_data_sources`. |
| **`src/data_loader.py`** | All dataset loading and metadata live here | New `load_*()` function for the feature’s data; `update_metadata()` will pick up new Excel files in `data/` automatically. |
| **`menu_structure.yaml`** | Single definition of navbar, landing cards, and KPI cards | New item under `navbar.main.left-menu` (or right); new entry in `landing_page_cards`; optionally `kpi_cards` or `data_page` section. |

**How to update shared files without causing conflicts**

**When working alone (no collaborators):** A simple cycle is: pull main → create feature branch → develop with frequent commits → push feature branch → open PR → merge to main → pull main and repeat. You only need to "merge main into your branch" (step 2 below) if main has new commits while you're on the feature branch (e.g. a long-lived branch or after you merged another PR).

1. **Communicate before editing** — In your PR and team channel, state that you will touch `app.py` / `data_loader.py` / `menu_structure.yaml` and for which feature. Avoid two people editing the same central file at the same time.
2. **Merge main first** — Before changing any shared file, update main and bring it into your branch. **New to Git: use merge.** Run: `git checkout main && git pull && git checkout <your-branch> && git merge main`. (Use rebase only if you're comfortable with rewriting history and force-pushing: `git fetch origin && git rebase origin/main`.) Whichever path you apply, resolve any conflicts in your branch right away so others don’t hit the same conflicts.
3. **One feature, minimal central changes** — Keep the feature logic in its own modules (e.g. `pages/`, `callbacks/`, `figures/`). In the central files, add only what's needed to register the feature: one new loader in `data_loader.py`, one new route and callback registration in `app.py`, one new menu/card block in `menu_structure.yaml`. Smaller diffs merge more easily.
4. **Register the feature first, then build** — Add the feature to the central files first with minimal changes (e.g. new loader stub in `data_loader.py`, new menu entry and route in `menu_structure.yaml` and `app.py`, route returning a placeholder page). Push so the structure is on the branch and others can see or adjust shared files if needed. Then implement the feature end-to-end in feature-specific files (pages, callbacks, figures). This avoids everyone editing the same central files at once and keeps coordination clear.
5. **Collaboration option: request Admin to add central registration** — When working with others, a cleaner approach is: in the PR (or before), the feature author requests an **Admin** (or designated person) to add all necessary central-file changes—imports, routes, menu entry, data loader—and push. Once that is on the branch, the author (and others) can work on feature-specific files without touching `app.py`, `data_loader.py`, or `menu_structure.yaml`. Only one person commits to those files, so conflict risk drops. Consider adding this as a step in your [Code Change Process Flow](#code-change-process-flow) when collaborating.

| Shared (coordinate with team) | Feature-specific (one lead per feature, any time) |
|------------------------------|---------------------------------------------------|
| `app.py`, `data_loader.py`, `server.py` | `callbacks/company_reporting_trends/`, `callbacks/global_policies/` |
| `menu_structure.yaml` | `callbacks/*_callbacks.py` (per-feature, e.g. reporting, pue_wue) |
| `layouts/`, `components/` (navbar, footer, filter_panel, figure_card, etc.) | `components/filters/company_reporting_trends/`, `components/filters/global_policies/`, other `filters/*.py` |
| `callbacks/base_chart_callback.py`, `figures/styles.py` | `figures/global_policies/`, and per-feature figures (`pue_chart`, `wue_chart`, etc.) |
| `helpers/`, `assets/styles.css` | `pages/company_reporting_trends/`, `pages/global_policies/`, and other `pages/*_page.py` per feature |
| `data/`, `scripts/` | `src/static_pages/` (Quarto) per section |

```
dashboard/
├── Dockerfile
├── README.md
├── environment.yml
├── menu_structure.yaml              ← shared
│
├── assets/
│   ├── *.png, *.svg
│   ├── styles.css                   ← shared
│   ├── previews/
│   └── static_pages/
│
├── data/                            ← shared
│   ├── *.xlsx, *.csv
│   ├── dependencies/
│   └── archive/
│
├── scripts/                         ← shared
│   └── update_geocoding_cache.py
│
└── src/
    ├── app.py                       ← shared
    ├── server.py                    ← shared
    ├── data_loader.py               ← shared
    │
    ├── callbacks/
    │   ├── base_chart_callback.py   ← shared
    │   ├── chart_callbacks.py
    │   ├── company_profile_callbacks.py
    │   ├── ep_page_callbacks.py
    │   ├── energy_use_callbacks.py
    │   ├── pue_wue_page_callbacks.py
    │   ├── reporting_callbacks.py
    │   ├── water_projections_page_callbacks.py
    │   ├── wue_callbacks.py
    │   ├── company_reporting_trends/   ← feature-specific
    │   └── global_policies/             ← feature-specific
    │
    ├── figures/
    │   ├── styles.py                ← shared
    │   ├── *_chart.py, *_barchart.py, *_heatmap.py
    │   └── global_policies/         ← feature-specific
    │
    ├── components/                  # shared except filters/* (feature-specific)
    │   └── filters/
    │       ├── company_reporting_trends/   ← feature-specific
    │       ├── global_policies/             ← feature-specific
    │       └── *.py
    │
    ├── helpers/                     ← shared
    ├── layouts/                     ← shared
    │
    ├── pages/
    │   ├── *_page.py
    │   ├── company_reporting_trends/   ← feature-specific
    │   └── global_policies/             ← feature-specific
    │
    └── static_pages/                # per-section (feature-specific)
        ├── companies/, energy_projections/, pue_wue/
```

### Quick reference

| Area | Purpose |
|------|--------|
| `src/app.py` | Dash app entry and routing |
| `src/data_loader.py` | Dataset loading, processing and caching |
| `src/callbacks/` | Backend logic for filters and figures |
| `src/figures/` | Plotly figure creation |
| `src/components/` | Layout and filter UI building blocks |
| `src/pages/` | Page layouts and composition |
| `menu_structure.yaml` | Navigation / menu definition |
| `data/` | Excel/CSV inputs and derived caches |

## Code Change Process Flow

1. **Create a pull request** — Open a PR with a clear description of the planned work. Check that others are not already changing the same files; if you need to change shared files, notify teammates first.

2. **Create a new branch** — From the target branch (e.g. `main`), create and switch to a new branch:
   ```bash
   git checkout -b <branch-name>
   ```

3. **When collaborating: optional — request Admin to add feature to central files** — If your feature needs changes in `app.py`, `data_loader.py`, or `menu_structure.yaml`, ask an Admin (or designated person) to add the minimal registration (imports, route, menu entry, data loader) and push to the branch. Then you can work only on feature-specific files (pages, callbacks, figures) and avoid conflicts on shared files.

4. **Update code** — Implement your changes; follow the existing project structure when adding or modifying files.

5. **Commit, push, request review** — When done, commit with a clear message, push the branch, and request a code review.
   - **Commit message format**: `<feat> Brief summary` with a body listing the main changes.
   ```bash
   git add .
   git commit    # editor opens for message; in Vim use :wq to save and exit
   git push -u origin <branch-name>
   ```
   **Note:** Commit frequently so your work is not lost.

6. **Notify reviewer** — Ensure the assigned reviewer is notified to perform the code review.

7. **Merge** — If approved, the approver merges the PR and notifies the author. Use the **Squash and merge** option to combine commits; update the merge commit message. This keeps history clean and easier for collaborators to follow.

8. **Clean up** — After merge, delete the branch remotely (e.g. in the PR UI) and locally:
   ```bash
   git checkout main && git pull && git branch -d <branch-name>
   ```

9. **Update local main** — Ensure your local `main` is up to date and remove references to deleted remote branches:
   ```bash
   git checkout main && git pull
   git remote prune origin
   ```

**Helpful git commands**

- **Revert to the previous commit** — Discards all uncommitted changes and resets the working tree to the last commit:
  ```bash
  git reset --hard HEAD
  ```

- **View status** — `git status`

- **View differences** — `git diff <file-path>`

- **View history** — `git log`
