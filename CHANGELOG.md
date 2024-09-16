# :steam_locomotive: Change Log

---

## 1.0.0 (2024-09-15)

- Added the `%exit` command language command to exit the tbp debugger. Documented [here](https://john-robbins.github.io/tbp/tbp-command-language#exiting-the-debugger-e--exit). Closes [#1](https://github.com/John-Robbins/tbp/issues/1).
- Now tbp behaves like a normal command line application when the user hits `CTRL+C` and `CTRL+D`. Documented [here](https://john-robbins.github.io/tbp/faq#general-usage). Closes [#3](https://github.com/John-Robbins/tbp/issues/3).
- Fixed the copyright on top of all Python files. For some reason I thought it was 2004. Closes [#43](https://github.com/John-Robbins/tbp/issues/43).
- Added the combined coverage report summary to the CI.yml output. That makes it easier to see what didn't have coverage. Closes [#44](https://github.com/John-Robbins/tbp/issues/44). Sorry, the below is just too sexy not to show. :joy_cat:

    ```text
    Name                        Stmts   Miss Branch BrPart   Cover   Missing

    ------------------------------------------------------------------------

    tests/controlkeys_test.py      88      0     20      1  99.07%   72->exit
    tests/interpreter_test.py     510      0     14      2  99.62%   885->exit, 904->exit
    ------------------------------------------------------------------------

    TOTAL                        2253      0    252      3  99.88%

    13 files skipped due to complete coverage.
    ```

- Added the `tiny_basic_grammar.ebnf` and `grammar_tests.txt` that I forgot to bring over from the dead repository. Closes [#45](https://github.com/John-Robbins/tbp/issues/45).
- Added better error reporting on `INPUT` entry errors and escaped syntax error strings, so characters like `\n` are displayed correctly. Closes [#46](https://github.com/John-Robbins/tbp/issues/46).
- Did a pass to eliminate any dead code. Closes [#47](https://github.com/John-Robbins/tbp/issues/47).
- Did a final editing pass on all documentation.

---

## 0.9.1 (2024-09-09)

---

- Fixed CI.yml to work around the bug in GitHub Actions where matrix jobs don't have any status of the sub jobs. See [#41](https://github.com/John-Robbins/tbp/issues/41).
- Added the [GitHub and GitHub Actions](https://john-robbins.github.io/tbp/project-notes#github-and-github-actions) section to the documentation.
- Added the pyreadline3 dependency to the [documentation](https://john-robbins.github.io/tbp/project-notes#small-python-friction-points).
- Updated the README and [Getting Started Installation](https://john-robbins.github.io/tbp/getting-started#installation) section to point to the Latest releases.
- This is basically a practice release to ensure I have the steps down. :crossed_fingers: (Thanks for your patience!)

---

## 0.9.0 (2024-09-06)

---

- The initial public release of Tiny BASIC in Python! See the [documentation](https://john-robbins.github.io/tbp/) for complete usage.
