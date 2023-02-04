
import glob
import json
import subprocess
import re
import os
import itertools

fp = '.'
extensions = ['pdf', 'png', 'jpg', 'jpeg']  # missing uppercase but idc


def extract_loop(n: int):
    done = glob.glob(f'{fp}/*.json')
    files = list(itertools.chain.from_iterable([glob.glob(f'{fp}/*.{ext}') for ext in extensions]))

    replace_ext = lambda x: x.replace('.pdf', '.json').replace('.png', '.json').replace('.jpg', '.json').replace('.jpeg', '.json')
    commands = [f'''./OCR en false true "{file}" "{replace_ext(file)}"''' for file in files]
    commands = [command for command, file in zip(commands, files) if replace_ext(file) not in done]

    print(f'Running {len(commands)} commands')
    for j in range(max(int(len(commands)/n), 1)):
        print(f'Processing batch {j + 1} of {int(len(commands)/n)}')
        procs = [subprocess.Popen(i, shell=True) for i in commands[j * n: min((j + 1) * n, len(commands))]]
        for p in procs:
            p.wait()
        print(f'Batch complete. Error count: {sum([p.returncode for p in procs])}')


def json_info(regex: re.Pattern, dedup: bool = False) -> None:
    json_files = glob.glob(f'{fp}/*.json')
    token_set = set()
    for json_file in json_files:
        with open(json_file, 'r') as f:
            t = json.load(f)
            if 'text' in t:
                for line in t['text'].split('\n'):
                    tokens = re.findall(regex, line)
                    for token in tokens:
                        if not dedup:
                            print(json_file + ": " + token)
                        token_set.add(token)
    if dedup:
        print('\n'.join(token_set))


def main():
    # n = 16  # num par proc
    n = os.cpu_count() * 2
    extract_loop(n)

    email_re = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    # ip_re = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    json_info(email_re, dedup=True)


if __name__ == '__main__':
    main()
