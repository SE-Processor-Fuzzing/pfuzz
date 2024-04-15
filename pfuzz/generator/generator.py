import os
import random
import subprocess
from pathlib import Path
from typing import Dict

import pfuzz.constants


class Generator:
    def __init__(self, template_config: Dict[str, range]) -> None:
        self.template_config = template_config

    def generate_config(self, config: Dict[str, str]) -> None:
        for flag in self.template_config.keys():
            if random.randint(0, 1):
                config[flag] = str(random.choice(self.template_config[flag]))

    def generate(self, config: Dict[str, str], c_name: str, out_name: str) -> None:
        if not config:
            self.generate_config(config)

        out_dir = Path(__file__).resolve().parent / pfuzz.constants.OUT_DIR
        if not out_dir.is_dir():
            out_dir.mkdir(parents=True)
        os.chdir(out_dir)

        run_process = ["csmith"]
        for flag in config.keys():
            run_process.append(flag)
            run_process.append(config[flag])

        gen_proc = subprocess.run(run_process, capture_output=True, text=True)
        with open(c_name, "w") as f:
            f.write(gen_proc.stdout)

        subprocess.run(
            [
                "riscv64-linux-gnu-gcc",
                "--static",
                "-O0",
                "-I/usr/local/include",
                c_name,
                "-o",
                out_name,
            ],
            capture_output=True,
        )
