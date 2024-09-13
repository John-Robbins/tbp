---
title: FAQ
nav_order: 5
layout: default
permalink: faq
---
<!-- markdownlint-disable MD026 MD025-->
<!-- markdownlint-disable-next-line -->
# Frequently Asked Questions
{:.no_toc}

1. TOC
{:toc}

---

## General Usage

- How does tbp handle `CTRL+C` and `CTRL+D` (`CTRL+Z`, ENTER on Windows)?

For tbp, the Python REPL served as a model. As a reminder, when you enter these keys, they are not entries, but generate exceptions. `CTRL+C` is [KeyBoardInterrupt](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt) and `CTRL+D` is [EOFError](https://docs.python.org/3/library/exceptions.html#EOFError).

When you are at a normal tbp prompt, `tbp:>` or a breakpoint prompt, `DEBUG(410:>`, `CTRL+C` does nothing, but `CTRL+D` will immediately terminate the application.

If a Tiny BASIC program is running, both `CTRL+C` and `CTRL+D` will break the program and reset tbp's internal state as though it was typed in or loaded.

If you are in the middle of loading a file with [%loadfile](tbp-command-language#loading-files-loadfile--lf), a `CTRL+C` will abort file loading, reset the tbp internal state, and clear any loaded program from memory.

Figuring out a way to test these keystrokes was quite the adventure. You can check out the hack by reading [controlkeys_test.py](https://github.com/John-Robbins/tbp/blob/main/tests/controlkeys_test.py).

## Tiny BASIC

- Why is `Syntax Error: Error #020: LET is missing an '=', but found '{var}'` the most common error when entering code at the tbp prompt?

   Tiny BASIC allows two forms of `LET` statements:

   ```text
   LET M = 420

   J = 240
   ```

   When you enter a statement like `oto`, the tbp scanner sees the first character, it looks to see if the entire statement is a keyword and if it isn't, the scanner assumes the `o` is the variable `O`, and the assumes it's the second form of assignment above.

- What are some good BASIC resources if I want to learn more?

  - Tom Pittman's [Tiny BASIC](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/) page has loads of content and example programs.
  - [Marco's Retrobits](https://retrobits.altervista.org/blog/) has lots of cool games he has written for other BASIC platforms such as the [Sinclair ZX Spectrum](https://en.wikipedia.org/wiki/ZX_Spectrum) computer. While many of his programs don't run in Tiny BASIC, I learned a lot from them.
  - Ronald Nicholson has a great [list](http://www.nicholson.com/rhn/basic/basic.info.html) of BASIC resources. Additionally, he developed the free, cross-platform Chipmunk BASIC interpreter.
  - [Hans Otten](http://retro.hansotten.nl) has a ton of awesome retro computing information. His [KIM-1 Simulator](http://retro.hansotten.nl/6502-sbc/kim-1-manuals-and-software/kim-1-simulator/) is one of the computers that ran the original Tiny BASIC implementations.
  - J. Alan Henning has written many nice [articles](https://troypress.com/category/programming-languages/) about BASIC. My absolute favorite article he wrote is [The Tiny BASIC Interpretive Language IL—and Onions.](https://troypress.com/the-tiny-basic-interpretive-language-il-and-onions/) He presents his intermediate language (IL) version of Tiny BASIC from the original specifications [Dennis Allison](https://en.wikipedia.org/wiki/Dennis_Allison) wrote in the [January 1976](https://archive.org/details/dr_dobbs_journal_vol_01/page/n89/mode/2up) issue of Dr. Dobb’s Journal of Computer Calisthenics & Orthodontia.
  - [Damian Walker's](http://damian.cyningstan.org.uk/posts/150/the-tiny-basic-interpreter-and-compiler-project) implementation of [Tiny BASIC](https://github.com/cyningstan/TinyBASIC). It's all in C, and he added some neat features.
  - [Rosetta Code's Tiny BASIC](https://rosettacode.org/wiki/Category:Tiny_BASIC) examples.

## Code/Development

- What is the overview of the source code files?

    | Filename | Description |
    |----------|-------------|
    |`tokens.py`| The token type returned by the scanner.|
    |`languageitems.py`|The `LanguageItem` types returned by the parser and the `Visitor` abstract class that is the base class for the interpreters.|
    | `errors.py` | The exception types thrown on syntax and runtime errors.|
    | `helpers.py`| Holds the shared logger, and the input/output functions used across the project.|
    | `memory.py`|The fake memory for the `USR` function.|
    |`scanner.py`|The lexical scanner. |
    |`symboltable.py`|The symbol table for those 26 glorious variables. |
    |`parser.py`|The token parser. |
    |`astprinter.py`| A `Visitor` derived class to print the parse results. Used for testing and logging.|
    |`linter.py` | A `Visitor` derived class that does the linting analysis.|
    |`interpreter.py`| The tree walking interpreter that takes care of execution and debugging.|
    |`driver.py` | "Drives" the `Interpreter` class and handles the tbp command language.|
    |`__main__.py`|The entry point for the command line program.|

    See [Contributing](Contributing) for how to get setup for development.
