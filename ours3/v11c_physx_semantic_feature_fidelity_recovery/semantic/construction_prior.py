from pathlib import Path
import yaml

def load_priors(path):
    return yaml.safe_load(Path(path).read_text())

def prior_for(role, priors):
    return dict(priors.get(role) or priors['UNKNOWN'])
