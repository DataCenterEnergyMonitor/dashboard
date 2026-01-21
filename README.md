Installation Instructions:

create environment
```
conda env create -f environment.yml
```

activate environment
```
conda activate dcmonitor
```

register kernel
```
python -m ipykernel install --user --name dcmonitor --display-name "dcmonitor"
```

Build steps:

1. Update cache file with coordinates of the global policy locations when global_policies dataset is updated.

```
python scripts/update_geocoding_cache.py
```