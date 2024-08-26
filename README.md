# Tiny BASIC in Python

<!-- https://github.com/ikatyang/emoji-cheat-sheet -->
<!-- markdownlint-disable MD026 -->
## Party like it's 1976!

Badges I need:

- Ancient Technology
- Continuous Integration: Pass/Fail
- Unit Tests: count
- Code Coverage: 99%

Tiny BASIC in Python (tbp) is an implementation of the [Tiny BASIC language](https://en.wikipedia.org/wiki/Tiny_BASIC) first proposed by [Dennis Allison](https://en.wikipedia.org/wiki/Dennis_Allison) in response to Bill Gate's "[An Open Letter to Hobbyists](https://en.wikipedia.org/wiki/An_Open_Letter_to_Hobbyists)." In 1976, [Dr. Tom Pittman](http://www.ittybittycomputers.com) developed his version of Tiny BASIC, which was one of many developed at that time. He has graciously posted on his [Tiny BASIC website](www.ittybittycomputers.com/IttyBitty/TinyBasic/index.htm) OCR'd copies of documentation, programs, and much more about that exciting time in computer history, which provided the inspiration for tbp.

Where the original Tiny BASIC fit into 4K of memory, tbp is, ahem, a *LOT* larger, but does have a full debugger, linter, and runs on macOS, Linux, and Windows. So, pull up your bell bottom jeans, slap an [8-track tape](https://en.wikipedia.org/wiki/8-track_cartridge) into the stereo, and see what it was like for your grandparents when they programmed computers. Let's get groovy with the good vibes!

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## :boom: Tiny BASIC in Python in Action

As powerful as [The Bionic Woman](https://en.wikipedia.org/wiki/The_Bionic_Woman) and [The Six Million Dollar Man](https://en.wikipedia.org/wiki/The_Six_Million_Dollar_Man) combined! (Play the [bionic sound effect](https://www.myinstants.com/en/instant/six-million-dollar-man/) when watching the demo below.)

![Feel the SIZZLE!](./sizzle/tbp-sizzle-optimized.gif)

**Tip**: If you get lost at the tbp prompt, `tbp:>`, type `%help` to get the in-application help.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## :sparkles: Features Galore

- Supports all 12 statements and the two functions of the original, including `USR`.
- Supports all 26 variables, `A` - `Z`. Why would anyone need more than that?
- Loading and saving programs to/from disk. Feel free to make a pull request for cassette tape support.
- A linter to help with program correctness.
  - Potential uninitialized variable usage.
  - Invalid `GOTO` and `GOSUB` address (i.e., line numbers).
  - Missing `END` in the program.
  - Using `CLEAR` in a program.
- A **full** debugger built in!
  - Breakpoints.
  - Single stepping.
  - Call stack.
  - Variable display (all 26!)
- Line timings.
- Runs all Tiny BASIC programs from the 1970s! [^1]
- More documentation than you ever wanted!

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## :computer: Installation

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

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## :book: Documentation

Everything about tbp is lovingly documented to death in the GitHub Pages for this repository: [https://John-Robbins.github.io/tbp](https://John-Robbins.github.io/tbp).

## :clap: Acknowledgements

### [Bob Nystrom](https://github.com/munificent)

His glorious [Crafting Interpreters](http://www.craftinginterpreters.com) book sparked my huge interest in programming languages. He wrote a book that perfectly threaded the needle between practical and theory and gives you the learning hooks to successfully move on to books like the [Dragon Book](https://www.malaprops.com/book/9780321486813) and [Engineering a Compiler](https://www.malaprops.com/book/9780128154120). My rating: 5,000 :star:! You will see Bob's influence all over this project. All the ugly and mistakes are all on me, not Bob.

### [Tom Pittman](http://www.ittybittycomputers.com)

He wrote a popular version of [Tiny BASIC](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/index.htm), but more importantly, uploaded old documentation and original programs that gave me the idea to focus on Tiny BASIC as a learning project.

### [Marco's Retrobits](https://retrobits.altervista.org/blog/)

Marco's [TinyBasicBlazor](https://retrobits.altervista.org/tinybasicblazor/), a WebAssembly port of Tiny BASIC, was a huge help in helping me understand lots of edge cases in Tiny BASIC behavior. His [Day of the Week](https://retrobits.altervista.org/tinybasicblazor/programs/DayOfTheWeek.txt) program helped me uncover a major bug in my code, too.

### :heart: YOU! :heart:

Thank you so much for looking at tbp. It's my first Python project so any feedback on what I can do better, or what I did wrong, is appreciated.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## :page_facing_up: Legal

Dr. Pittman holds the copyright to his implementation of Tiny BASIC:

**TinyBasic interpreter Copyright 1976 Itty Bitty Computers, used by permission.**

The license for all the code in this repository is under the [MIT license](https://github.com/John-Robbins/tbp/blob/main/LICENSE).

[^1]: Except the absolutely wild and crazy [Tiny BASIC IL assembler](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/TBasm.txt).
