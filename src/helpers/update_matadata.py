import os
import json
import glob
from datetime import datetime

def update_metadata(data_dir="data", json_path="metadata.json"):
    """Update JSON metadata with last modified time stamps for all Excel files in data_dir."""

    # load existing metadata or initialize if missing
    try:
        with open(json_path, "r") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        metadata = {"files": [], "last_updated": None}

    # convert list of files to dict for easy lookup
    files_dict = {f["source_file"]: f for f in metadata.get("files", [])}

    # retrieve last modified time stamp for each excel file in data_dir
    for path in glob.glob(os.path.join(data_dir, "*.xlsx")):
        fname = os.path.basename(path)
        mtime = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()

        if fname in files_dict:
            # update if modified time changed
            if files_dict[fname]["last_modified"] != mtime:
                files_dict[fname]["last_modified"] = mtime
        else:
            # add new file entry
            files_dict[fname] = {"source_file": fname, "last_modified": mtime}

    metadata["files"] = list(files_dict.values())

    # calculate most recent modification time across all files
    metadata["last_updated"] = (
        max(f["last_modified"] for f in metadata["files"])
        if metadata["files"]
        else None
    )

    # write to json
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=2)