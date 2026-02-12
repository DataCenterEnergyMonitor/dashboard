## Installation

1. Create the conda environment:
   ```bash
   conda env create -f environment.yml
   ```

2. Activate the environment:
   ```bash
   conda activate dcewm
   ```

3. (Optional) Register the Jupyter kernel for notebooks:
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

```
dashboard/
├── Dockerfile
├── README.md
├── environment.yml
├── menu_structure.yaml
│
├── assets/
│   ├── *.png, *.svg          # Logos, icons
│   ├── styles.css
│   ├── previews/             # Page preview images
│   └── static_pages/         # Rendered HTML (companies, energy_projections, pue_wue, index)
│
├── data/
│   ├── *.xlsx, *.csv         # Main datasets
│   ├── dependencies/         # location_coords_cache.csv, metadata.json, geojson
│   └── archive/              # Historical dataset snapshots
│
├── scripts/
│   └── update_geocoding_cache.py
│
└── src/
    ├── app.py
    ├── server.py
    ├── data_loader.py
    │
    ├── callbacks/                    # Dash callbacks by feature
    │   ├── base_chart_callback.py
    │   ├── chart_callbacks.py
    │   ├── company_profile_callbacks.py
    │   ├── energy_projections_page_callbacks.py
    │   ├── energy_use_callbacks.py
    │   ├── pue_wue_page_callbacks.py
    │   ├── reporting_callbacks.py
    │   ├── water_projections_page_callbacks.py
    │   ├── wue_callbacks.py
    │   ├── company_reporting_trends/  # Company reporting section callbacks
    │   └── global_policies/           # Global policies section callbacks
    │
    ├── charts/                        # Plotly chart builders
    │   ├── styles.py
    │   ├── *_chart.py, *_barchart.py, *_heatmap.py  # PUE, WUE, energy, reporting, etc.
    │   └── global_policies/           # Global policies section figures 
    │
    ├── components/                    # Reusable UI (navbar, footer, filter_panel, etc.)
    │   ├── filters/                   # Feature-specific filter UIs
    │   │   ├── company_reporting_trends/  # Company reporting section filters
    │   │   ├── global_policies/           # Global policies section filters
    │   │   ├── energy_projections_filters.py
    │   │   ├── pue_wue_filters*.py
    │   │   └── water_projections_filters.py
    │   
    │
    ├── helpers/                      # geocode_locations, geojson_cache, export_json_for_quarto
    ├── layouts/                      # base_layout, data_page_layout
    │
    ├── pages/                         # Page modules (one per route)
    │   ├── *_page.py                  # about, companies, company_profile, contact, etc.
    │   ├── company_reporting_trends/  # rt_main_page, rt_tab1–5
    │   └── global_policies/           # gp_main_page, gp_tab1–4
    │
    └── static_pages/                  # Quarto source (qmd, params, _quarto.yml, references.bib)
        ├── companies/, energy_projections/, pue_wue/
```

### Quick reference

| Area | Purpose |
|------|--------|
| `src/app.py` | Dash app entry and routing |
| `src/data_loader.py` | Dataset loading, processing and caching |
| `src/callbacks/` | Backend logic for filters and charts |
| `src/charts/` | Plotly figure creation |
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

3. **Update code** — Implement your changes; follow the existing project structure when adding or modifying files.

4. **Commit, push, request review** — When done, commit with a clear message, push the branch, and request a code review.
   - **Commit message format**: `<feat> Brief summary` with a body listing the main changes.
   ```bash
   git add .
   git commit    # editor opens for message; in Vim use :wq to save and exit
   git push -u origin <branch-name>
   ```
   **Note:** Commit frequently so your work is not lost.

5. **Notify reviewer** — Ensure the assigned reviewer is notified to perform the code review.

6. **Merge** — If approved, the approver merges the PR and notifies the author. Use the **Squash and merge** option to combine commits; update the merge commit message. This keeps history clean and easier for collaborators to follow.

7. **Clean up** — After merge, delete the branch remotely (e.g. in the PR UI) and locally:
   ```bash
   git checkout main && git pull && git branch -d <branch-name>
   ```

8. **Update local main** — Ensure your local `main` is up to date and remove references to deleted remote branches:
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
