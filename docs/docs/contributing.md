---
title: Contributing
nav_order: 6
layout: default
permalink: contributing
---
<!-- markdownlint-disable-next-line -->
# Contributing
{:.no_toc}

1. TOC
{:toc}

---

Thank you so much for any and all contributions to Tiny BASIC in Python! As this is my first full Python project, I am sure there are many mistakes, even though I tried to follow best practices. Thank you for helping me learn!

## Before Starting

Before submitting a pull request, please help me out by doing the following.

- File an issue explaining the bug or mistake in the code.
- If the issue is not following best practices, please explain what I did wrong or include a link to a website/repository showing why I need to make the change. This is all about me learning after all, so I really appreciate the pointers.

## Setting Up Your Development Environment

All my development occurred on Python version 3.12.1, but any higher versions will work as the CI GitHub Actions are using 3.12.5.

### macOS Sonoma and Linux

*Note: I haven't tested these scripts on Linux, but they should work. Let me know if they don't.*

In the `./tools` directory are two shell scripts I used to jump set up my environment. First ensure that you don't have a virtual environment active. If you do, execute `deactivate`. In the tbp code root directory, run the following three commands in your terminal.

```bash
chmod +x ./tools/venv-setup.sh
chmod +x ./tools/dev-setup.sh
./tools/venv-setup.sh
```

Close and reopen the terminal to activate the `.tbp-venv` virtual environment. In the tbp code root directory, run the following command.

```bash
./tools/dev-setup.sh
```

This script will upgrade `pip`, install the developer tools, and make an editable install where you can develop all you want.

### Windows

Note that I don't have a Windows computer, so I am going off memory and reading Activate.ps1, with these steps. Please file a bug if these are not correct!

For Windows, you will need to do the script steps manually in the tbp code root directory at a PowerShell command prompt.

First look to see if the `VIRTUAL_ENV` environment variable exists, which indicates you have a virtual environment already active. Run the Windows equivalent to `deactivate` to disable that virtual environment.

In your PowerShell command prompt, execute the following commands to create a virtual environment for tbp.

```powershell
python3 -m venv .tbp-venv
.\.tbp-venv\bin\activate
```

You may have to shut down and restart PowerShell.

In your PowerShell command prompt, in the tbp code root directory, execute the following commands.

```powershell
python -m pip install --upgrade pip
python -m pip install .[dev]
python -m pip install --editable .
```

## Key Development Notes

<!-- markdownlint-disable-next-line -->
<span style="color:red">**UNIT TESTS AND CODE COVERAGE ARE EVERYTHING!**</span>

At the time of this writing, there are 290 unit tests and the combined operating system code coverage of 99.88% with 100% coverage for the tbp code. For any pull requests, I'll obviously be checking that any code changes have tests that execute the code. *No coverage, no merge!*

If you have a version of `make` installed, the root directory has the `Makefile` that automates a ton of work for you. Simply running `make` will do the work of running `mypy`, `ruff`, `pylint`, `coverage.py`, and `pytest`.

Here's what the output looks like on macOS. `Makefile` is your best friend when developing tbp.

```text
% make
mypy --config-file pyproject.toml src/ tests/
Success: no issues found in 29 source files
ruff check --config ./pyproject.toml src/ tests/
All checks passed!
pylint --rcfile pyproject.toml src/ tests/

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

coverage run -m pytest --maxfail=1 -console_output_style=classic --junit-xml=.test-results.xml
============================= test session starts ==============================
platform darwin -- Python 3.12.1, pytest-8.3.2, pluggy-1.5.0
rootdir: /Users/johnrobbins/Code/tbp
configfile: onsole_output_style=classic
plugins: anyio-4.4.0
collected 290 items

tests/cmd_lang_test.py ...........                                       [  3%]
tests/controlkeys_test.py .......                                        [  6%]
tests/debugger_test.py .......................                           [ 14%]
tests/driver_test.py ........................                            [ 22%]
tests/helpers_test.py ...........                                        [ 26%]
tests/interpreter_test.py .............................................. [ 42%]
...........................                                              [ 51%]
tests/lang_test.py ..                                                    [ 52%]
tests/linter_test.py ..........................                          [ 61%]
tests/memory_test.py .                                                   [ 61%]
tests/parser_test.py ................................................... [ 78%]
.................                                                        [ 84%]
tests/scanner_test.py ...................................                [ 96%]
tests/symboltable_test.py ........                                       [ 99%]
tests/tokens_test.py .                                                   [100%]

------ generated xml file: /Users/johnrobbins/Code/tbp/.test-results.xml -------
============================= 290 passed in 0.93s ==============================
coverage report --precision=2 --show-missing --sort=Cover --skip-covered
Name                        Stmts   Miss Branch BrPart   Cover   Missing
------------------------------------------------------------------------
src/tbp/helpers.py             79      4     22      1  95.05%   21-23, 231-232
src/tbp/driver.py             237      2    120      8  97.20%   87->89, 90->92, 128->112, 142->112, 180, 211, 436->exit, 466->exit
src/tbp/interpreter.py        496      2    186      6  98.83%   209->213, 359->363, 418->423, 581->exit, 603->606, 1053-1054
src/tbp/languageitems.py      170      1      8      1  98.88%   192
src/tbp/scanner.py            242      1    128      3  98.92%   211->exit, 320, 356->360
tests/controlkeys_test.py      88      0     20      1  99.07%   72->exit
src/tbp/parser.py             271      0    116      2  99.48%   357->362, 502->519
tests/interpreter_test.py     510      0     14      2  99.62%   885->exit, 904->exit
------------------------------------------------------------------------
TOTAL                        4108     10    910     24  99.32%

20 files skipped due to complete coverage.
coverage lcov
Wrote LCOV report to .coverage.lcov
```
