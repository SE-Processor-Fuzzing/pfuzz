[![Build status][status-shield]][status-url]
[![MIT License][license-shield]][license-url]

# pfuzz

Simulated processor fuzzing tool.

## Table of contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Licenses](#licenses)

## Getting Started

### Prerequisites

- [Python 3.10+ with pip 19.0+](https://wiki.python.org/moin/BeginnersGuide/Download)
- [pipx](https://pypa.github.io/pipx/#install-pipx)

### Installation

Open the terminal and follow these steps:

1. Clone the repository:

    ```shell
    git clone git@github.com:SE-Processor-Fuzzing/pfuzz.git
    ```

2. Navigate to the project root:

    ```shell
    cd pfuzz
    ```

3. Install `Poetry` in an isolated environment with:

    ```shell
    pipx install poetry
    ```

4. Set `Poetry` configuration:
    
    **Note**: This command will make sure that poetry creates virtual environments within the project's root folder.

    ```shell
    poetry config virtualenvs.in-project true
    ```

4. Install all required dependencies:

    **Note**: Running the command will automatically create a virtual environment and install all dependencies in an isolated manner. For details see Poetry [documentation](https://python-poetry.org/docs/cli/#install).

    - For running the tool:
        ```shell
        poetry install
        ```
    - For development:
        ```shell
        poetry install --with dev
        ```

<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[license-shield]: https://img.shields.io/github/license/SE-Processor-Fuzzing/pfuzz.svg?style=for-the-badge&color=blue
[license-url]: LICENSE
[status-shield]: https://img.shields.io/github/actions/workflow/status/SE-Processor-Fuzzing/pfuzz/.github/workflows/ci.yml?branch=main&event=push&style=for-the-badge
[status-url]: https://github.com/SE-Processor-Fuzzing/pfuzz/blob/main/.github/workflows/ci.yml