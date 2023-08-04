import os
import sys
import hashlib
import json

script_folder = os.path.dirname(os.path.abspath(__file__))
base_folder = os.path.dirname(script_folder)

def create_manifest():
    venv_folder = script_folder + '\\app'

    files_exclude = ['FormulaSheet.xlsx', 'manifest.json',
                     '__pycache__', 'rsconnect-python', '.git',
                     'bloom_model_new', 'bloom_score', 'images', 'utils.py']

    manifest = {
        "version": 1,
        "metadata": {
            "appmode": "python-dash",
            "entrypoint": "app:app"
        },
        "locale": "en_US.UTF-8",
        "python": {
            "version": "3.7.11",
            "package_manager": {
                "name": "pip",
                "version": "21.0.1",
                "package_file": "requirements.txt"
                }
        }
    }

    file_checksum = {}
    for f in os.listdir(venv_folder):
        if f in files_exclude:
            continue

        is_folder = os.path.isdir(os.path.join(venv_folder, f))

        if (is_folder):
            for root_dir, dirs, files in os.walk(os.path.join(venv_folder, f)):
                for f2 in files:
                    rel_d = os.path.relpath(root_dir, venv_folder)
                    with open(os.path.join(root_dir, f2), 'rb') as fp:
                        file_content = fp.read()
                        checksum = hashlib.md5(file_content).hexdigest()

                        f_path = os.path.join(rel_d, f2).replace(os.path.sep, '/')
                        file_checksum[f_path] = {'checksum': checksum}
        else:
            with open(venv_folder + '/' + f, 'rb') as fp:
                file_content = fp.read()
                checksum = hashlib.md5(file_content).hexdigest()
                file_checksum[f] = {'checksum': checksum}

    manifest['files'] = file_checksum
    print(json.dumps(manifest, indent = 4))

    json.dump(manifest, open(venv_folder + '/manifest.json', 'w'), indent = 4)

def main():
    create_manifest()

if __name__ == '__main__':
    main()