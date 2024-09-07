---
title: Getting Started
nav_order: 2
layout: default
permalink: getting-started
---
<!-- markdownlint-disable-next-line -->
# Getting Started

1. TOC
{:toc}

---

## Overview

This document covers getting Tiny Basic in Python (tbp) installed and options for running at the command line.

## Installation

It seemed nuts to put this up on PyPI, which is for important modules, not learning experiments. If you have the git executable for your operating system in your path, pip is happy to install directly from GitHub. Of course, you will want to have all this fun in a virtual environment so set that up first.

### Installing from GitHub

```bash
% pip install git+https://github.com/John-Robbins/tbp.git
```

### Cloning and Installing

Download the code from here as a .ZIP file. Expand that file into a directory, then execute the following.

```bash
% pip install .
```

## Starting tbp

As tbp is a command line program, once you have it installed, you can simply run it directly from your favorite command shell.

```text
% python -m tbp

  Tiny BASIC in Python - github.com/John-Robbins/tbp
   _______ ____
  |__   __|  _ \
     | |  | |_) |_ __
     | |  |  _ <| '_ \
     | |  | |_) | |_) |
     |_|  |____/| .__/
                | |
                |_| version 0.9.0.0
   Party like it's 1976!
   Look at that cool CN tower in Toronto!

tbp:>
```

## Command Line Options

You can see the command line options supported by tbp by using the `--help` command.

```text
% python -m tbp --help
usage: tbp [-h] [-c COMMANDS] [-nl] [file]

Tiny BASIC in Python - github.com/John-Robbins/tbp

positional arguments:
  file                  Optional Tiny BASIC in Python program to run

options:
  -h, --help            Show this help message and exit.
  -c COMMANDS, --commands COMMANDS
                        String of Tiny BASIC and/or command language instructions
                        to execute. Use ^ to separate individual commands.
  -nl, --nologo         Do not display the glorious tbp logo 😿

```

### File to Load

To start tbp with a program file ready to run, pass it on the command line.

```text
 % python -m tbp ./examples/rand.tbp

  Tiny BASIC in Python - github.com/John-Robbins/tbp
   _______ ____
  |__   __|  _ \
     | |  | |_) |_ __
     | |  |  _ <| '_ \
     | |  | |_) | |_) |
     |_|  |____/| .__/
                | |
                |_| version 0.9.0.0
   Party like it's 1976!
   What do I do with a $2.00 bill?

tbp:>run
69      12      83      53      59      16      62      36
7       80      13      92      93      46      32      44
36      54      71      26      58      0       56      28
29      66      5       40      86      60      83      79
43      64      48      66      68      12      0       86
19      32      71      97      81      65      34      70
35      67      80      40      76      30      39      5
36      61      6       32      44      5       88      51
tbp:>
```

### Run Commands at Start

The `--commands` option allows you to specify any Tiny BASIC language statements or tbp command language commands you want to run at startup. Separate the commands with the `^` character.

In the following example, it shows starting up with the [tbp.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/tbp.tbp) example program but using `--commands` to run the [`LIST`](tb-language#list---display-the-program-in-memory) statement followed by the [`%q`](tbp-command-language#quit-q) command.

```text
% python -m tbp ./examples/tbp.tbp --commands LIST^%q

  Tiny BASIC in Python - github.com/John-Robbins/tbp
   _______ ____
  |__   __|  _ \
     | |  | |_) |_ __
     | |  |  _ <| '_ \
     | |  | |_) | |_) |
     |_|  |____/| .__/
                | |
                |_| version 0.9.0.0
   Party like it's 1976!
   Star Wars Episode IV started filming. May the Force be with them.

10 REM Displays the ultra-sexy tbp logo.
11 REM You are welcome!
20 PR "   _______ ____"
30 PR "  |__   __|  _ \"
40 PR "     | |  | |_) |_ __"
50 PR "     | |  |  _ <| '_ \"
60 PR "     | |  | |_) | |_) |"
70 PR "     |_|  |____/| .__/"
80 PR "                | |"
90 PR "                |_|"
100 PR "   Party like it's 1976!"
110 END

Thank you for using tbp! Your patronage is appreciated.
```

### Turning Off the Startup Logo

There is no reason you should ever skip the glorious, beautiful, awe-inspiring, and sexy tbp logo. It will hurt my heart if you do, and you don't want that. Thank you for your kindness.
