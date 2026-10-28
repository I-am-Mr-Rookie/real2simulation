"""Trusted S10 handoff: validate the complete S08 spec+scene before exporting JSON."""
import argparse, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
loader = importlib.util.spec_from_file_location('experiment_validator', ROOT / 'contracts/experiment/validate_experiment.py')
validator = importlib.util.module_from_spec(loader); loader.loader.exec_module(validator)

def export(spec_path: Path, scene_path: Path) -> dict:
    experiment, scene = validator.load_json(spec_path), validator.load_json(scene_path)
    validator.validate_setup(experiment, scene, scene_path.parent)
    return {'artifact_version': 's10-validated-setup-v1', 'validation': 'validate_setup', 'producer': 'contracts/experiment/validate_experiment.py', 'spec': experiment, 'scene': scene}

def main():
    p = argparse.ArgumentParser(); p.add_argument('spec', type=Path); p.add_argument('scene', type=Path); p.add_argument('-o', '--output', type=Path); a = p.parse_args()
    text = json.dumps(export(a.spec, a.scene), sort_keys=True, separators=(',', ':')) + '\n'
    if a.output: a.output.write_text(text, encoding='utf-8')
    else: print(text)

if __name__ == '__main__': main()
