def export_json_for_quarto(json_filename="metadata.json", data_dir=None):
    """Export json attributes as YAML for Quarto to consume"""
    import json
    import yaml
    from pathlib import Path
    from datetime import datetime
    
    current_dir = Path(__file__).parent
    print(current_dir)
    
    # Construct full path
    if data_dir is None:
        data_dir = current_dir.parents[1] / "data"
    else:
        data_dir = Path(data_dir)
    
    json_path = data_dir / json_filename
    
    with open(json_path) as f:
        metadata = json.load(f)
    
    # Create structured dict
    quarto_params = {"last_updated": {}}
    
    for file_info in metadata["files"]:
        source_file = file_info["source_file"]
        file_key = source_file.replace(".xlsx", "").replace(".csv", "").replace("-", "_").lower()
        
        if file_info.get("last_modified"):
            dt = datetime.fromisoformat(file_info["last_modified"])
            quarto_params["last_updated"][file_key] = dt.strftime("%B %d, %Y at %H:%M")
        else:
            quarto_params["last_updated"][file_key] = "Not available"
    
    # Write YAML
    quarto_params_path = current_dir.parent / "static_pages" / "_quarto_params.yml"
    with open(quarto_params_path, "w") as f:
        yaml.dump(quarto_params, f, default_flow_style=False)
    
    print(f"✓ Exported {len(quarto_params['last_updated'])} timestamps for Quarto")


from pathlib import Path
from datetime import datetime
current_dir = Path(__file__).parent
print(current_dir)
print(current_dir.parents[1] / "data")
export_json_for_quarto()