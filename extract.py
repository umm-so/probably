
import glob
import json
import shutil
import subprocess
import re
import os
import itertools

fp = '.'
extensions = ['pdf', 'png', 'jpg', 'jpeg']  # missing uppercase but idc


def extract_loop(n: int):
    done = glob.glob(f'{fp}/*.json')
    files = list(itertools.chain.from_iterable([glob.glob(f'{fp}/*.{ext}') for ext in extensions]))

    commands = [f'''./OCR en false true "{file}" "{file + '.json'}"''' for file in files if ';' not in file and '"' not in file]
    commands = [command for command, file in zip(commands, files) if f'{file + ".json"}' not in done]

    print(f'Running {len(commands)} commands')
    for j in range(max(int(len(commands)/n), 1)):
        print(f'Processing batch {j + 1} of {int(len(commands)/n)}')
        procs = [subprocess.Popen(i, shell=True) for i in commands[j * n: min((j + 1) * n, len(commands))]]
        for p in procs:
            p.wait()
        print(f'Batch complete. Error count: {sum([p.returncode for p in procs])}')


def json_info(regex: re.Pattern, dedup: bool = False, copy_to_path: str = None) -> None:
    json_files = glob.glob(f'{fp}/*.json')
    token_set = set()
    for json_file in json_files:
        with open(json_file, 'r') as f:
            t = json.load(f)
            if 'text' in t:
                for line in t['text'].split('\n'):
                    tokens = re.findall(regex, line)
                    copy_path = f'{copy_to_path}/{os.path.basename(json_file)[:-5]}'
                    if copy_path is not None and len(tokens) and not os.path.isfile(copy_path):
                        shutil.copy(json_file[:-5], copy_path)
                    for token in tokens:
                        if not dedup:
                            print(json_file + ": " + token)
                        token_set.add(token)
    if dedup:
        print('\n'.join(token_set))


def fix_outdated_json():
    for json_file in glob.glob(f'{fp}/*.json'):
        file_ext = [os.path.isfile(json_file[:-4] + ext) for ext in extensions]

        for i, ext_correct in enumerate(file_ext):
            if ext_correct:
                os.rename(json_file, json_file[:-4] + extensions[i] + '.json')
                break


def main():
    # n = 16  # num par proc
    n = os.cpu_count() * 2
    extract_loop(n)

    email_re = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    # ip_re = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    json_info(email_re, copy_to_path="search/emails")


if __name__ == '__main__':
    main()
