from pathlib import Path, PurePosixPath
import hashlib, json, os, tempfile, zipfile
import yaml

OUTPUT = Path('/kaggle/working') if Path('/kaggle/working').is_dir() else Path.cwd() / 'local_output'
OUTPUT.mkdir(parents=True, exist_ok=True)
AGENT_DIR = OUTPUT / 'agent_bundle'
AGENT_DIR.mkdir(exist_ok=True)
print('Output:', OUTPUT)
