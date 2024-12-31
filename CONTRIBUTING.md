# Contributing to ChromatographicPeakPicking

Thank you for your interest in contributing to the ChromatographicPeakPicking project! Contributions are welcome and appreciated. This document outlines the process for contributing to this project.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Reporting Bugs](#reporting-bugs)
4. [Suggesting Enhancements](#suggesting-enhancements)
5. [Pull Requests](#pull-requests)
6. [Development Setup](#development-setup)
7. [Style Guidelines](#style-guidelines)
8. [Testing](#testing)
9. [Contact](#contact)

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it to understand the expectations for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please report it by creating an issue on GitHub. Provide the following information:
- A clear and descriptive title.
- A detailed description of the problem.
- Steps to reproduce the issue.
- Any relevant screenshots or logs.

### Suggesting Enhancements

If you have an idea for an enhancement, please suggest it by creating an issue. Provide the following information:
- A clear and descriptive title.
- A detailed description of the enhancement.
- A rationale for why this enhancement would be useful.
- Any relevant examples or use cases.

### Pull Requests

We welcome pull requests for bug fixes, enhancements, and documentation improvements. To submit a pull request:
1. **Fork the repository** and clone it to your local machine.
2. **Create a new branch** for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3. **Make your changes** in your branch.
4. **Commit your changes** (`git commit -m 'Add your commit message'`).
5. **Push your changes** to your fork (`git push origin feature/your-feature-name`).
6. **Create a pull request** from your branch to the `main` branch of the original repository.

Please ensure your pull request:
- Includes a clear description of the changes.
- References any related issues or pull requests.
- Passes all tests and adheres to the project's coding style.

## Development Setup

To set up your development environment:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Adiaslow/ChromatographicPeakPicking.git
   cd ChromatographicPeakPicking
   ```

2. **Create a virtual environment** and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Style Guidelines

Follow these guidelines to ensure consistency in the codebase:

- **PEP 8**: Follow the Python PEP 8 style guide.
- **Docstrings**: Use reStructuredText (reST) for docstrings.
- **Type Annotations**: Use type annotations where applicable.

We recommend using tools like `flake8` and `black` to check and format your code.

## Testing

Before submitting a pull request, ensure that all tests pass. To run the tests:

1. **Install testing dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run the tests**:
   ```bash
   pytest
   ```

## Contact

If you have any questions, feel free to contact the project maintainers:

- **Robert Scott Lokey**: [slokey@ucsc.edu](mailto:slokey@ucsc.edu)
- **Grant Andrew Koch**: [gakoch@ucsc.edu](mailto:gakoch@ucsc.edu)
- **Adam Michael Murray**: [admmurra@ucsc.edu](mailto:admmurra@ucsc.edu)

Thank you for your contributions!

---
