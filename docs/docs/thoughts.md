---
title: Project Notes
nav_order: 6
layout: default
permalink: project-notes
---
<!-- markdownlint-disable MD026 MD025-->

<!-- markdownlint-disable-next-line -->
# Project Notes
{:.no_toc}

1. TOC
{:toc}

---

## Overview

Through the development of Tiny BASIC in Python (tbp), I kept notes on where I screwed up, got confused, loved something, explained my thinking, or got frustrated. These are not necessary to enjoy the Tiny BASIC life, but I thought they might be interesting to others.

## Code and Problem Thoughts

### My Kingdom for an EBNF Grammar Checker

The very first task I wanted to complete was to build a solid Extended Backus-Naur form (EBNF) grammar for the Tiny BASIC language by hand. The file is [tiny_basic_grammar.ebnf](https://github.com/John-Robbins/tbp/blob/main/docs/tbp/tiny_basic_grammar.ebnf) in the tbp repository. Building robust grammars for a language is hard. There are a million edge cases and surprises that are waiting around dark corners to scare you. All the compiler textbooks discuss creating grammars extensively, and you start to realize that if you screw up the grammar in the beginning, you’ve made your life terrible.

This correctness was especially important to me because I am a programming language beginner. All the compiler text books I read stressed the importance of grammar correctness, avoiding [left recursion](https://en.wikipedia.org/wiki/Left_recursion), and the like. Given how many pages these textbooks spent on defining grammars, I was looking forward to working with tools that would help me in finding all the mistakes I was making. One would think EBNF grammar validators would be a keen area of development to help language designers avoid mistakes.

Yes, I am gobsmacked that EBNF validators aren’t a dime a dozen. [^1] I found a few academic websites that offered validators for experimental LR(0) grammars and other esoteric parsers. It seems like all the textbooks on compilers leave checking and validating your grammar is an "exercise for the reader." Why is that? Is that because all these programming language researchers and experienced compiler developers can cast a side eye across an EBNF grammar and just know it’s perfect? Is writing an EBNF validator as hard as solving the Riemann hypothesis? This really is a very strange situation to me, and I'd love to know why EBNF validators aren't common.

Years ago, I'd heard of the parser generator [ANTLR]( https://www.antlr.org), but I'm dealing with a language that has 12 statements and two functions. I wanted to do this by hand to learn and while ANTLR is very cool, but extraordinary overkill for my little project. Fortunately, ANTLR has its wonderful [Lab](http://lab.antlr.org) where you can interactively play around with rules and example text to see how they parse. I used it to get a clue about how some grammar rules would work and since the ANTLR grammar is close enough to EBNF, it helped a lot.

I spent my time hand walking the grammar I built, and it all looked OK. Here's where the narrator jumps in and says in that gorgeous, succulent, deep baritone, say "And John was wrong. Completely wrong."

Somehow, through internet magic, I saw a reference someplace on a blog where the writer said they tested their grammar on [http://instaparse.mojombo.com](http://instaparse.mojombo.com). Oh, my! An EBNF checker that works! It's not perfect, but if you refresh the page and paste in your grammar in after major changes, it works well. I found many, many problems in my first attempt at the grammar under Instaparse. A huge thank you and shout out to [Mark Engleberg](https://github.com/Engelberg) for writing [instaparse](https://github.com/Engelberg/instaparse), and [Matt Huebert](https://github.com/mhuebert) for hosting it. Much later, I found another tool, [EBNF Test](https://mdkrajnak.github.io/ebnftest/) by [mdkrajnak](https://github.com/mdkrajnak) which was also extremely helpful.

Wrestling with some left recursion problems, I found there are more sites dedicated to eliminating the left recursion in your life. I like the [left_rec]((https://cyberzhg.github.io/toolbox/left_rec)) tool from [CyberZHG](https://github.com/CyberZHG) the best. [^2] Definitely, keep this grammar recursion tools handy because you'll need them.

Obviously, I don't have a complete grasp of grammar development. My plan is to work through Chapter 2 in the [Dragon Book](https://www.malaprops.com/book/9780321486813) very carefully.

### The Grade for My Scanner: C-

Bob Nystrom's jlox implementation in his book [Crafting Interpreters](http://www.craftinginterpreters.com) *highly* influenced tbp's design. [^3] His was the first implementation I fully understood, so it was obvious I should go down the same path. However, I think I should have done more thinking and designing on the scanner before jumping into the implementation. I'll own the screw-up.

In some cases, like the [Scanner._number](https://github.com/John-Robbins/tbp/blob/main/src/tbp/scanner.py#L377-L387) method, I got myself into situations where scanning for the token left the current pointer into the next lexeme, and I'd have to back up.

Another area where I did a bad job was in scanning for keywords and identifiers (those `A`-`Z` variables). Bob's language, lox, allows spaces, but not inside keywords, so his implementation could use string methods like `substring` to extract a keyword. Since I am working with a language where `GOTO` and `G   O   T   O` are identical, that added a level of complexity that I didn't appreciate at first. I decided to go with a solution that looked at a letter, say `R`, and then looked if the next characters were `UN`, `ETURN`, `ND` or `EM`. Of course, skipping any whitespace between them. In all, my [Scanner._handle_keyword_or_identifier](https://github.com/John-Robbins/tbp/blob/main/src/tbp/scanner.py#L406-L471) method is embarrassing.

With my huge amounts of unit tests, I thought I had flushed out all the problems, until a week or two ago. I was running as many Tiny BASIC programs as I could find and produce through tbp, and I ran across the following line.

```basic
150 IF X > P RETURN
```

My scanner tokenized the line in a way I didn't expect.

```text
Token.IF            : IF
Token.Identifier    : X
Token.GreaterThan   : >
Token.PRINT         : PR
Syntax error!       : ETURN
```

Recall from the [Tiny Basic Language](tb-language) that the [`PRINT`](tb-language#print---output) statement can be abbreviated as `PR`. :raised_eyebrow: :grimacing: :sob:

In the end, with too much special casing, I have a scanner that works, so that's good, but I'm not very proud of it. Remember folks, think before you type.

### The Grade for My Parser and Interpreter: B/B-

Again, if you've read [Crafting Interpreters](http://www.craftinginterpreters.com) the tbp parse and interpreter should feel very familiar. As they stand now, both are solid, but it was some work to get there for both.

The main problem with the parser was that I had declared separate expression and statement types, and it got to be a mess coordinating them while parsing. After enough pain, I rethought everything and decided to go with a single base class I called a [`LanguageItem`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L160-L202). That helped a lot, but I still feel that there's more simplification possible. For example, I have a [`Assignment`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L258-L279) type and a [`LET`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L489-L503) type, which are really the same thing.

The interpreter bothers me a little because the class is so big. I don't know if there's a way to move functionality other places, but it is doing a lot of work. It's the execution engine and debugger, which makes up a lot of the code. Something I considered was making the `LanguageItem` derived types, like for `RND` or `PRINT` have ways to do their own work. That way as the interpreter is executing through the code, it could tell the [`Print`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L451-L470) type, "Hey! Do your thing." passing in a callback if the `Print` type needed to evaluate its parameters.

Another thing that bothers me about both the `Parser` and `Interpreter` classes is that they both do output for reporting errors and general execution. It was convenient to do that, but it feels dirty to me.

### The Grade for tbp: B-

The good news is that tbp has all the functionality I set out to build. While I think there are many places, see above, where I could have done better, never underestimate the power of working code. One area I think I did well was in reporting errors. Each error shows the line of code and has the little arrow drawing to the column where the error is on the line.

```text
Runtime Error: Error #336: Accessing uninitialized variable 'D'.
30645 PRINT "Human wins=";E;" tbp-AI wins=";F;" Ties=";D
-------------------------------------------------------^
```

Another area where I thought I did well was the unit tests and code coverage. With 280-unit tests and 99% coverage overall, I flushed a ton of bugs out with the tests. Additionally, I have mypy, ruff, and pylint cranked up to their equivalent strict mode with only 13 rules disabled in pyproject.toml. I always got a little thrill running `make` and seeing all those checks and tests.

```text
% make
mypy --config-file pyproject.toml src/ tests/
Success: no issues found in 28 source files
ruff check --config ./pyproject.toml src/ tests/
All checks passed!
pylint --rcfile pyproject.toml src/ tests/

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

coverage run -m pytest --maxfail=1 -console_output_style=classic
=================== test session starts ===================
platform darwin -- Python 3.12.1, pytest-8.3.2, pluggy-1.5.0
rootdir: /Users/johnrobbins/Code/tbp
configfile: onsole_output_style=classic
plugins: anyio-4.4.0
collected 280 items

tests/cmd_lang_test.py ..........                   [  3%]
tests/debugger_test.py .....................        [ 11%]
tests/driver_test.py ........................       [ 19%]
tests/helpers_test.py ...........                   [ 23%]
tests/interpreter_test.py ......................... [ 32%]
................................................    [ 49%]
tests/lang_test.py ..                               [ 50%]
tests/linter_test.py ..........................     [ 59%]
tests/memory_test.py .                              [ 60%]
tests/parser_test.py .............................. [ 70%]
......................................              [ 84%]
tests/scanner_test.py ............................. [ 94%]
......                                              [ 96%]
tests/symboltable_test.py ........                  [ 99%]
tests/tokens_test.py .                              [100%]

=================== 280 passed in 0.95s ===================
coverage report --precision=2 --show-missing --sort=Cover
Name                        Stmts   Miss Branch BrPart   Cover   Missing
------------------------------------------------------------------------
src/tbp/helpers.py             78      6     20      1  92.86%   175-179, 223-224
src/tbp/driver.py             216      4    108      6  96.91%   86->88, 89->91, 138, 166, 311-312, 389->exit, 421->exit
src/tbp/astprinter.py         142      3     28      2  97.06%   111-112, 277
src/tbp/interpreter.py        499      5    186      7  98.25%   201->205, 356->360, 415->420, 578->exit, 600->603, 1047-1048, 1134-1136
src/tbp/parser.py             275      3    116      2  98.72%   359->364, 486-488, 509->526
src/tbp/languageitems.py      170      1      8      1  98.88%   192
src/tbp/scanner.py            242      1    128      3  98.92%   211->exit, 320, 356->360
tests/interpreter_test.py     510      0     14      2  99.62%   885->exit, 904->exit
src/tbp/__init__.py             3      0      0      0 100.00%
src/tbp/errors.py              17      0      0      0 100.00%
src/tbp/linter.py             107      0     32      0 100.00%
src/tbp/memory.py              16      0      4      0 100.00%
src/tbp/symboltable.py         30      0     16      0 100.00%
src/tbp/tokens.py              51      0      2      0 100.00%
tests/cmd_lang_test.py        101      0      0      0 100.00%
tests/debugger_test.py        177      0     42      0 100.00%
tests/driver_test.py          203      0     34      0 100.00%
tests/helpers_test.py          85      0      2      0 100.00%
tests/lang_test.py             10      0      0      0 100.00%
tests/linter_test.py          217      0     52      0 100.00%
tests/memory_test.py           11      0      4      0 100.00%
tests/parser_test.py          348      0     44      0 100.00%
tests/programs.py               4      0      0      0 100.00%
tests/scanner_test.py         430      0     18      0 100.00%
tests/symboltable_test.py      43      0     10      0 100.00%
tests/tokens_test.py            5      0      0      0 100.00%
------------------------------------------------------------------------
TOTAL                        3990     23    868     24  99.03%

1 empty file skipped.
coverage lcov
Wrote LCOV report to .coverage.lcov
```

## Python

First, some backstory: Not only is tbp my first foray into the world of programming languages, but it is also my very first Python project. A year and a half ago, I took a Numerical Analysis class and that was the first time I ever had seen Python. [^4] We used Jupyter notebooks, and I learned barely enough Python to survive the class as I was far more interested in the mathematics of Runga-Kutta methods and Fourier transforms.

A few months ago, I randomly bumped into Peter Norvig's [(How to Write a (Lisp) Interpreter (in Python))](http://norvig.com/lispy.html) and found it fascinating. Out of a growing curiosity, I got the [Dragon Book](https://www.malaprops.com/book/9780321486813), but that was a fire hose of information and theory. Coming from the software industry, I needed a book where I could get my hands dirty with an interpreter/compiler to get the feel for how the various parts fit together. Once I had something concrete to relate to, I felt I would get much more out of the big textbook. That's when I bumped into Bob Nystrom's outstanding [Crafting Interpreters](http://www.craftinginterpreters.com), which is *exactly* the book I envisioned I needed to start my learning journey.

My first inclination when I thought about doing a project about Tiny BASIC was to use C, which I can do in my sleep. However, I wanted to get into programming languages quickly, so I thought I'd do my implementation in Python. With the automatic memory management, the dynamic language, and given Python's popularity I could also finally be one of the cool kids.

Hence, a whole new problem domain and a whole new development language at the same time. I thought I'd write a bit about my time as an extremely experienced developer learning Python, and its ecosystem, as a **COMPLETE PYTHON NOVICE** in 2024. After finishing tbp, I'd only call myself a mostly novice Python developer. Python has been around a very long time, and I have the feeling that the Python community has forgotten that there are still a few people who have never used Python before. If you're feeling a little foreshadowing, I'll go ahead and tell you that my first Python experience wasn't completely positive.

### Awesome Sexy Python Tools

With a fresh installation of Visual Studio Code, and a bunch of design-ish documents, I started my journey. Being an experienced developer, I know I want a test tool, code coverage, and if there's any error checking/best practices tools, I must have them. I've used, and developed, tools like that on other languages/environments, so know how valuable they are.

Quickly I find out about [pytest](https://docs.pytest.org/en/7.1.x/contents.html), [coverage.py](https://coverage.readthedocs.io/en/latest/), [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), and [Ruff](https://github.com/astral-sh/ruff). It took a total of seven minutes to get them setup and in use, and that included me walking downstairs to get a drink and petting a cat. Instant productivity is like a drug to me. These are all pure, unadulterated sexiness dressed up as developer tools.

When I figured out how to get Pylance and Ruff set [up to eleven](https://en.wikipedia.org/wiki/Up_to_eleven) to turn on all checks, I was even more thrilled. As a brand-new Python developer having these tools was so helpful learning best practices and the ins and outs of the language.

All my code and test files were in the same directory and with pytest and coverage.py on the case, I developed over 85% of tbp just running the following three commands. Of course, I was using the pytest integration in Visual Studio Code to debug as well.

```shell
coverage run -m pytest --maxfail=1 -console_output_style=classic ./src
coverage report --show-missing --sort=Cover
coverage lcov
```

### The Python Language Itself

I was concentrating on the programming language problem, and not running into many problems with Python itself as a language as I'm not doing anything "interesting" like threading, developing decorators, or interacting with other languages. Using [The Python Tutorial](https://docs.python.org/3/tutorial/index.html) was more than sufficient to help me get into the flow of using Python. Also, watching Raymond Hettinger's [Transforming Code into Beautiful, Idiomatic Python](https://www.youtube.com/watch?v=OSGv2VnC0go) presentation was also helpful to think more Python-like, even though he gave it during the internet Jurassic period (2013).

One thing that did confuse me was that classes hate function pointers. Note that I'm calling it a function pointer, but I guess it's more like a function reference. My idea was that I would have the higher order classes that drive the interpreter provide a reference to an output function that they could use to perform necessary output. The idea being I could have different output functions depending on if I were testing, etc. For example, I wanted to have the function pointer write to a file to allow textual comparisons between runs. When I coded it up, I would get a runtime error every time I'd try to call the function pointer in one of my classes. The error was that there was an arity error in that there were too many parameters to the function. I scratched my head for quite a while until I realized that in Python it assumes any function pointer in a class is a class method and is automatically passing the self-reference. Hence, the arity errors. For the Python language, that was the only thing I found odd, but it wasn't a showstopper bug.

### Small Python Friction Points

Sharp-eyed readers might have noticed a tool missing in the [Awesome Sexy Tools](#awesome-sexy-python-tools) section: [mypy](https://www.mypy-lang.org). I am using it and, as it my wont, on full [strict mode](https://mypy.readthedocs.io/en/stable/getting_started.html#strict-mode-and-configuration). Dynamic types are all great until the real world intrudes. In all mypy helped me a lot, but I had to do more fiddling in the code to keep it quiet. The typical, albeit contrived, example is the following.

```python
# Declaration.
def foo(value: str | int) -> None:
    # Explicitly check the type.
    if isinstance(value, int):
        # Do something with the value, but you *always* must cast even
        # though you just checked.
        g_Global = g_Global + cast(value,int)
    else:
        # You'll have *always* to cast(value,str) here, too
```

I do love what mypy is doing, but I think this is a result of bolting on a good type system to an old and successful dynamic language. When I first started tbp, I had different AST types for expressions and statements, and I spent a lot of time fiddling with declarations and casting to ensure mypy was OK with the code. What mypy is trying to solve is a very hard problem. I don't know if this is something better tooling in editors could help with but mypy is 95% great but that last 5% ends up being a little work. I’m sure I’m misunderstanding something about the use of mypy.

Another small stumbling block was that while Python has easy to use [`list`](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists) and [`dict`](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) data structures, I was surprised that sorted lists and dictionaries were not part of the Python Standard Library. I wanted to keep the Tiny BASIC program in a dictionary with the key being the line number and the associated item the AST types. From the Python documentation, it looked like I could use the [OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict), but that only does insertion order. If someone has a thousand-line program in tbp, and they want to insert a line in the middle, it looks like I'd be inserting and calling [sorted](https://docs.python.org/3/library/functions.html#sorted) constantly which returns a new dictionary every time. I've done a ton of C# programming in the past and have an intimate knowledge of memory management, both native and managed, as well as garbage collection algorithms. I knew using the standard library wasn't correct or scalable for my problem domain.

Fortunately, I found [Grant Jenkins](https://github.com/grantjenks)' [Python Sorted Containers](https://grantjenks.com/docs/sortedcontainers/), which is massive overkill for what I needed, but it did allow me to focus on my problem domain instead of me spending a lot of time developing my own implementation. If you use Sorted Containers, [Hal Blackburn](https://github.com/h4l) did a great job building the necessary [type stubs](https://github.com/h4l/sortedcontainers-stubs), so you get all the mypy goodness.

The only other dependency for tbp is [pyreadline3](https://github.com/pyreadline3/pyreadline3), which is necessary to mimic the built-in Python [readline](https://docs.python.org/3/library/readline.html#module-readline) library for Windows. Using arrow keys and line editing is a must-have feature. It is weird that out of the box Python does not have common, simple line editing across all three operating systems.

### Python Struggles

If you look through this repository, you might notice that there's very little history. It looks like the code just spontaneously appeared fully and perfectly formed from my brain. Nope, not at all! The project started in a private repository that became a disaster, so had to move to a new one. Why? All because I wanted to make tbp a module.

I want to make very clear I deeply appreciate everyone who has ever worked on Python, wrote anything about Python, or answered a question on Python in any forum. I am not pointing fingers or blaming anyone. At the beginning of this [section](#python), I specifically said I started tbp as **COMPLETE PYTHON NOVICE**, but I am an experienced developer.[^5] What I want to share is what it is like in 2024 to try to learn Python. My hope is that this feedback can point out to the Python community what it's like and why I am finding it more difficult than I expected. I can't help but think that if I am struggling this much to do the basics, I can only imagine how lost someone just beginning software development would feel. All of what I say below comes from my heart with love. Most importantly, I want that brand new aspiring developer sitting at her computer be successful starting with Python and that she doesn’t give up in frustration.

One of the first things I learned on my Python journey is that there is far more "content" about Python on the internet than I could have ever imagine. Since Python has been around a while, it makes sense, but that's a weakness, not a Python strength. Several times when I first started when I had an issue, I'd find some content that would say it solved the problem, but when I tried, it wouldn't work, and I'd figure out it was for Python 2. With the avalanche of content on the internet I've found the signal-to-noise ratio is 99% noise and 1% signal. There are billions of articles on how to slice an array but finding anything useful past never-programmed-before-beginner-content is difficult. I quickly figured out that to have any hope of being successful with Python, the only content I could really trust was at [https://docs.python.org/3/](https://docs.python.org/3/). If I did venture outside that place, I made sure to search only content written in the last year or two at most.

Another key trick I employed simply trying to start learning Python pay for the [Kagi](https://kagi.com) search engine because it lets you easily [block sites](https://help.kagi.com/kagi/features/website-info-personalized-results.html#personalized-results) with low quality content from appearing in your search results. Additionally, Kagi has through its [Lenses](https://help.kagi.com/kagi/features/lenses.html) feature a fantastic way to limit searches to forums.

The best way I can sum up the state of trying to learn Python in 2024 is to reference that meme of [How to Draw an Owl](https://www.reddit.com/r/pics/comments/d3zhx/how_to_draw_an_owl/). Step one is to draw a circle, step two is to draw the rest of the owl. This is **not** a joke. Once you understand [list comprehension](https://docs.python.org/3/glossary.html#term-list-comprehension), where do you go? As you can hopefully see with tbp, I think I've developed a passable understanding of the Python language, but the next step is missing. Where's the introduction to infrastructure? Where is the walk-through content on setting up your development environment? How do imports work? Why are there seemingly millions of package installers? Which one should I use? How do I set up projects with multiple modules? Why are there so many build/packaging systems? These are the questions I still have about *after* finishing tbp.

Earlier I mentioned that I started tbp with all my code in a single directory and used pytest to run my code. That worked well, and my focus was completely on the problem domain of programming languages. As I get the scanner finished, and I am getting close to finishing the parser, I figure it's time for me to look at getting tbp set up as a module. Looking at projects on GitHub, I saw the source layout they used so moved the tbp source (`./src/tbp`) and test code (`./test`) to mimic those. That's when I got to find the unique Python joy of import problems. Visual Studio Code was happily showing me IntelliSense when I added a new test, but pytest just gave me errors whenever I tried to run tests. I spent hours trying to figure out the import problems until I gave up and put all code back in the same directory. At least I knew I could work on my problem, even though I knew I'm not being Pythonic.

A while later, I have the `Interpreter` class finished, and I really need to figure out this module and associated import problems. I'm happy to end up exposing myself as a complete idiot, but if with all my development experience, I am flailing as a novice Python developer, how must a new developer feel?

Coming from the Windows world, if I want a new project, I could fire up Visual Studio, and in the New Project dialog, I pick what I want, and poof, a project appears. This project has all the basic settings, so I can start developing. For example, if I want a project that builds a C DLL, I'm not worrying too much about the infrastructure as a new developer, and one can start focusing on the problem they want to solve. I would love to see the exact same thing with Python. It's worth mentioning that I found several project templates on GitHub and in blog posts, but whenever I tried them, I still had the same import problems.

It took me 10 frustrating hours of grinding through tons of documentation, web searches, and trial and error on top of the three months I'd already been looking for a solution. I started at the [Installing Python Modules](https://docs.python.org/3/installing/index.html) page where there's a link to [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/), which says "This tutorial walks you through how to package a simple Python project." As a Python novice, I thought this was the guide I need to get my imports working. It was not. Also, it used [Hatchling](https://packaging.python.org/en/latest/key_projects/#hatch) as what looked like the default, so I chose that.

After hours of fruitless searching and reading, I randomly ended up in the Python Packaging User Guide on the [Packaging and distributing projects](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/), which talks about Setuptools. Also, the page says it is outdated, but didn't give any links on where to go for the latest information. As a Python novice, I'm thinking packaging is build systems. Also, I'm nowhere near the point of being ready to package and distribute anything because I can't even get tests working, so I almost didn't read it. However, in the middle of that page is [Working in "development mode"](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode), and for the first time in three months I learn about `python -m pip install -e .` and "Editable Installs". Wow! I was gobsmacked.[^1] That section links to a page in the Setuptools, [Development Mode (a.k.a. “Editable Installs”)](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) with even more information.

Why was something this important buried in the Setuptools documentation instead of at docs.python.org? While I'm surely an idiot, this feels like a *really* vital part of developing Python modules that was not mentioned anywhere a new Python developer would know to look. I would love to know why this basic infrastructure content isn't a more prominent part of the getting started documentation.

Weirdly, in trying to get the proper steps written down for how to create and develop a new module with imports working, I see different behaviors. With a brand-new virtual environment, sometimes I can have an empty `__init__.py` in the `src/modname` directory. Other times I must put in `from .modname import thing1, thing2` for imports to work over in the test code. Now I see why this search, [https://www.google.com/search?q=developer+python+imports+errors+how+to+fix+site%3Astackoverflow.com](https://www.google.com/search?q=developer+python+imports+errors+how+to+fix+site%3Astackoverflow.com), has about "About 22,600,000 results (0.36 seconds)." Again, my misunderstandings about imports could be all me.

When I first ran into import problems, out of desperation I was even looking in the [CPython](https://github.com/python/cpython) source code for hints. That gave me an idea. How does one go about proposing a PEP? Can we get two new keywords: `import_that_doesn't_hate_you` and `from_that_doesn't_hate_you` that have a well-known, documented, and easily understandable process for Python imports? I'm only half joking.

Obviously, the Python community has done and will continue to do wonderful things. Python is everywhere and obviously works in a plethora of domains and operating systems. But as a complete Python novice, I seemed to spend a tremendous amount of time trying to figure out basic project setup and usage issues in Python. The Python community is working on huge and important problems given the breadth of Python usage, but there needs to be an emphasis on getting novice developers productive. I haven't even mentioned the large amount of time spent on other things like pyproject.toml settings and so on.

Please understand I'm just trying to report my story of trying to develop my first Python module as a novice Python developer in 2024. The problems might be all on me, but it felt much harder than it should have been. Python desperately needs an equivalent to Rust's glorious [Cargo Book](https://doc.rust-lang.org/cargo/).

## GitHub and GitHub Actions

While I started development before git was a gleam in Linus Torvalds' eye, I'd used git and GitHub quite a bit back in the olden days. However, in the time I've been away from the world of coding, there's been some huge changes at GitHub. Like, :sparkles:WOW:sparkles: levels of changes! As keeping with my obsessive note-taking inclination, I wrote up my thoughts and bumps with the new amazing GitHub Actions, the security, and project management features. I'll also post this in the GitHub Actions discussion area in the hopes it helps the product team. Especially as I'm a first-time user of GitHub Actions, which must make me a unicorn in today's dev world.

Just to make clear, I **love** the new to me features in GitHub! Like I mentioned in the [Python](#python) section, this feedback comes from a place of love in my heart. I want to help make GitHub better.

### Runners on All Three OS's FOR FREE?!?!?!

My original plan was to post the tbp code, and setup up just enough GitHub Pages for this documentation. I'm using [Jekyll](https://jekyllrb.com) as the site generator. [^6] The truly incredible [Just the Docs](https://just-the-docs.com) theme hand walks you through everything you need to do. When in doubt, I looked and followed what they did in their repository. Totally worth the [donation](https://opencollective.com/just-the-docs)! (I've already donated to pytest and coverage.py).

After getting my [first](https://github.com/John-Robbins/tbp/blob/5bc6d9a43a74f8c6d5ec254103dd26953a2f15f2/.github/workflows/Build%20and%20Deploy%20Site%20to%20Pages.yml) GitHub Action to build the pages, I thought I'd look a deeper to see what these things were all about. The fact that at no cost I could run all my tests on macOS, Windows, and Linux, was mind-blowing to me! What a wonderful gift to the open-source community. After I got my cross-platform tests with coverage working, I couldn't believe my 280-unit test combined code coverage was 99.92%![^7] Even more, the 2,000 minutes for Actions on personal accounts is huge. I've been pounding on my GitHub Actions for the entire first week of September, and I've used a whole 1 minute so far. I've just got to give a huge thanks to GitHub/Microsoft for giving us this support.

### Reading the Documentation

With my [Makefile](https://github.com/John-Robbins/tbp/blob/main/Makefile) that already does all the possible CI steps for tbp, I thought I'd only have to create a workflow file that called it with the right target. However, I knew I should go ahead and approach this as a great opportunity to learn more about GitHub Actions and workflows, because I know when I get to projects bigger than tbp, I'll want to use these wonderful tools.

The documentation has a [Use cases and examples](https://docs.github.com/en/actions/use-cases-and-examples) section, so I started with the [Building and testing Python](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python), because that's what I'm doing. That gave me a good idea of the particulars, but each of the sections seemed independent of each other. I wasn't sure what the relationship was because some just list steps and others list jobs. The [Prerequisites](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python#prerequisites) said I should be familiar with [Writing workflows](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python#prerequisites), I headed over there.

In the overall [documentation](https://docs.github.com/en/actions) I found the organization a little confusing. For example, the [Writing workflows](https://docs.github.com/en/actions/writing-workflows) list what I assumed was a table of contents for 27 articles about workflows that you should read in order. For example, it lists [Using workflow templates](https://docs.github.com/en/actions/writing-workflows/using-workflow-templates) followed by [Choosing when your workflow runs](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs). However, reading [Using workflow templates](https://docs.github.com/en/actions/writing-workflows/using-workflow-templates), does not have any link for the [Choosing when your workflow runs](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs), those it does have links for other parts of the documentation. My goal was to read a logical flow through learning about workflows starting from zero, but I was wandering to places that assumed I'd read something else previously.

The workflow documentation got into details quickly, when I was simply trying to get a handle on [Building and testing Python](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python). Personally, I feel it would be better to have a step-by-step tutorial of a simple calculator program. You start with the code, and you build the action step by step. The idea is that by the end the entire YAML file shows building, linting, and testing. The repository has everything in place so that PRs trigger the proper workflow and so on. That's what I ended up doing on a throw away repository to see how everything fit together. If this is something that GitHub doesn't feel is a good fit for the documentation, someone should do this in their blog as they would get a lot of traffic.

In all the documentation is pretty good, but a good walk through at the start would be great to have. The other issue is that the docs go deep fast, and I felt there's a lot of middle ground missing. I ended up with a monolithic workflow [file](https://github.com/John-Robbins/tbp/blob/b14ea797cb76c26c33005a4ce7ec768be4ec7a92/.github/workflows/Code-CI.yml) where I was installing, type checking, linting, testing, and producing code coverage on each operating system in the matrix. I knew that wasn't what I wanted in the long run but wasn't sure what the best practices were for a GitHub Action.

What I would have *loved* to have had in the docs were links to real world Python projects showing me how they tackled their workflows. The key is that these projects can't be gigantic, but smaller projects that one can learn from. After some quality time with my [search engine](https://kagi.com), I found [Ned Batchelder](https://github.com/nedbat)'s [scriv](https://github.com/nedbat/scriv) and [Arie Bovenberg](https://github.com/ariebovenberg)'s [whenever](https://github.com/ariebovenberg/whenever) to be Goldilocks size Python projects that were great resources to see real world GitHub Actions usage. Along the same lines, having a list of GitHub Actions best practices, and especially links to projects following them would be great also.

### Yet Another Misstep Looms

Or is Yesterday's Actions Mislead Later? Either way, YAML is not a configuration language that I enjoyed, but I'll deal with it. These [two](https://ruudvanasseldonk.com/2023/01/11/the-yaml-document-from-hell) different [posts](https://noyaml.com), do a good job of explaining the pain. My plan was to break up my giant job into multiple discrete jobs. For example, I didn't need to type check and lint on every operating system where one would suffice. Like all folks starting out in YAML, I have many, many commits in the edit, debug/find-stupid-error, repeat cycle. I just loved the joy of indention errors.

In the middle of learning GitHub Actions, I was surprised that there wasn't any graphical editor to help you build GitHub Actions. It feels like a tool that helps produce correct YAML limited to GitHub Actions doesn't seem like it would be at the complexity of a compiler back end. When I looked for such a tool on the Visual Studio Code Market Place, I didn't find any, but did find the [GitHub Actions](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-github-actions) extension. While it's nice to be able to run workflows from your IDE, I was more interested in the help with authoring. I don't know if I didn't have it installed correctly, or what, but the extension never reported obvious errors like indenting problems, so I uninstalled it. Fortunately, I found the cool [actionlint playground](https://rhysd.github.io/actionlint/) from [rhysd](https://github.com/rhysd), which validates your workflow files. It saved me innumerable mistakes! The ability to run workflows locally for testing would be very useful as well. I looked at the interesting [act](https://nektosact.com) project, but I only found it towards the end of my tribulations. When I work on bigger workflows, I will certainly install and use act.

Something that still has me confused about a workflow is how much you must repeat.

```yaml
jobs:
    lint-types-job:
        name: "Type & Lint Checks"
        runs-on: ubuntu-latest
        steps:
        # You have to love copying and pasting the same 11 lines into each job.
        # I tried to make these a reusable job, but GitHub Actions wants to
        # force you to ARY: Always Repeat Yourself. 😹😹
        - name: "Checkout Code"
          uses: actions/checkout@v4
        - name: Set up Python 3.12
          uses: actions/setup-python@v5
          with:
            python-version: "3.12"
            cache: 'pip'
        - name: "Install Dependencies"
          run: |
            python -m pip install --upgrade pip
            python -m pip install .[dev]
        # The unique part starts here.
        . . .

    test-cov-job:
        name: "Test & Coverage"
        needs: lint-types-job
        runs-on: ubuntu-latest
        steps:
        - name: "Checkout Code"
          uses: actions/checkout@v4
        - name: Set up Python 3.12
          uses: actions/setup-python@v5
          with:
            python-version: "3.12"
            cache: 'pip'
        - name: "Install Dependencies"
          run: |
            python -m pip install --upgrade pip
            python -m pip install .[dev]
        # The unique part starts here.
        . . .
```

In the above example, I'm repeating the exact same setup each time. Does the `test-cov-job` always have to repeat the setup? Can the job assume the project is ready to go? I never found anything definitive in the documentation and looking through many examples, it seems you must repeat the setup every time. As I mentioned in the comment above, Always Repeat Yourself feels wrong to me.

Thinking that [reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows) would be the answer, I went down that path. I wanted to encapsulate the common setup work, and pass in the `runs-on` value. Although it's been almost three years since someone asked, there's no official support for [array input type support](https://github.com/orgs/community/discussions/11692). I fumbled around with an [idea](https://github.com/orgs/community/discussions/11692#discussioncomment-3541856) I found in the actions discussions, but I could never get it to work. I gave up on reusable workflows and repeated myself because working code always wins.

After a while of trial and error, I had two workflows, one for code and one for docs. They were working great where I could run them manually on branches, and automatically on pushes to main. Life was good, and then my code workflow stopped working. My workflow worked on a Sunday and died on a Monday. Being brand new to workflows, I struggled for several hours as to why my artifact uploads no longer worked. Yeah, you know where this is going: [Upcoming breaking change: Hidden Files will be excluded by default](https://github.com/actions/upload-artifact/issues/602). Why did a breaking change not involve a major version bump? I'm old enough to remember when a [GitHub co-founder](http://tom.preston-werner.com/) first proposed [SemVer](https://semver.org/spec/v2.0.0.html), which I thought was a very good attempt at bringing sanity to version numbers. Is SemVer merely a suggestion at GitHub these days?

While I understand the [security issue](https://unit42.paloaltonetworks.com/github-repo-artifacts-leak-tokens/) that brought about this breaking change, how GitHub handled it was, honestly, abysmal. Why was there no warning about this change in the workflow run output? Why was there no prominent mention of this breaking change on the [`@actions/upload-artifact`](https://github.com/actions/upload-artifact) repository home page? I wonder what else will randomly and silently break in my workflows after this debacle? Please, you can do better.

### Protected Branches vs. GitHub Actions

Have the team working on protected branches and the team working on GitHub Actions ever talked to one another? Could you get them together, at least at a company party, so they can meet and finally communicate? :joy_cat:

The GitHub Actions documentation promotes the use of [filters](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow#using-filters) to control when various actions run. Following those guidelines, I had the following at the top of my two workflows.

```yaml
# Top of CodeCI.yml
on:
  push:
    branches: ["main"]
    paths-ignore:
    - docs/**
  pull_request:
    branches: ["main"]
    paths-ignore:
    - docs/**

# Top of DocsCI.yml
on:
  push:
    branches: ["main"]
    paths:
      - "docs/**"
```

This worked great as the right build occurred when code or documentation changed. In all, I was happy how the workflows turned out as I had control and got all the cool badges in the [README](https://github.com/John-Robbins/tbp/blob/main/README.md) file.

The next new GitHub addition I wanted to look at was the [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). Before I retired, I remember wishing we had something like this because we had to rely on manual steps and pure trust to ensure someone didn't screw up the main branch. Being able to enforce checking and pull request rules is huge help for code quality.[^8]

Heading over to the Branches setting in my repository, I set up a couple of rules for main:

- Require a pull request before merging
- Require status checks to pass before merging
- Require signed commits

For the status checks, I have the following required jobs.

- Code Jobs
  - `Type & Lint Checks` (mypy, pylint, and ruff)
  - `Tests & Coverage` (on all three operating systems)
  - `Coverage Report` (for the sweet, sweet badges)
- Docs Jobs
  - `Build Website`
  - `Deploy Website`

When I'm adding all five jobs as required, I realized my pull request status checks would never pass, thus failing the branch protections and requiring an override merge every time. For example, if I changed this documentation and pushed into main, the `Build Website` and `Deploy Website` jobs would run. However, the three code jobs would never run because the `paths-ignore` filtered them out, so they do not run and are not reported as skipped.

The docs have a section [Handling skipped but required checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks#handling-skipped-but-required-checks) but says nothing about what you need to specifically do. Down the page a little is the [Status checks with GitHub Actions and a Merge queue](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks#status-checks-with-github-actions-and-a-merge-queue) section, which looks like my way to fix this issue.

Reading the [Merging a pull request with a merge queue](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request-with-a-merge-queue) page, I didn't understand at all how a merge queue fixes the required test issue. Rereading the page carefully for the third time, I notice that merge queues are only available for organizations. It's just little ol' me with a free personal account, so no merge queues for you.

Since I'm stumped with no solution, I hit the information superhighway to see what others are doing. As small as tbp is, it's considered a monorepo because I've mixed code and documentation. One solution to break docs and code them into two separate repos, but that's just crazy talk. Bumping into a [GitHub discussion](https://github.com/orgs/community/discussions/26251), I see people have been asking about this issue for five years. :eyes: This seems like a very common situation to me, but maybe not that many repositories are relying on branch protections. I'd love to know if there's a way to find out how many are.

One [solution](https://github.com/orgs/community/discussions/26251#discussioncomment-3250964) is to create dummy jobs. In other words, in my CodeCI.yml file, create doc jobs of the same name and return success on them. That didn't seem like a good practice to follow. After weighing various options, I decided to use [@dorny](https://github.com/dorny)'s much starred [paths-filter](https://github.com/dorny/paths-filter). The action allows you to build conditions based on the file changes. Below is the job that all other jobs need that builds the conditionals used later. Sorry for the job name, but that's what I felt I was doing.

{%raw%}

```yaml
fight-github-job:
  name: "Detect File Changes"
  runs-on: ubuntu-latest
  # The permissions necessary for dorny/paths-filter@v3 on pull requests.
  permissions:
    pull-requests: read
  # The outputs for this job.
  outputs:
    # The first two outputs are what are used in subsequent jobs to determine
    # if we are looking at code or docs changes.
    code: ${{steps.filter.outputs.code}}
    docs: ${{steps.filter.outputs.docs}}
    # These two here are for debugging purposes. After much trial and error,
    # the ${FILTER_NAME}_files discussed in the dorny/paths-filter
    # documentation only works on steps. By doing this one can get the files
    # out of the job.
    code-files: ${{steps.filter.outputs.code_files}}
    docs-files: ${{steps.filter.outputs.docs_files}}
  steps:
  # Check out the code as that's needed for a push trigger.
  - name: "Checkout Code"
    uses: actions/checkout@v4
  # Now do the filtering so we can appropriately decide which jobs need to
  # be run.
  - name: "Filter Files"
    uses: dorny/paths-filter@v3
    id: filter
    with:
      # For debugging, I'm setting the outputs to build a list of files so
      # I can print them out in the jobs below.
      list-files: shell
      # For docs, I only care about all changes in the docs directory.
      # For code, I care only about the .toml file and the two code
      # directories, src and tests.
      filters: |
        docs:
          - added|modified|deleted: 'docs/**'
        code:
          - modified:'pyproject.toml'
          - added|modified|deleted: 'src/**'
          - added|modified|deleted: 'tests/**'
  - name: "Changed Code Files"
    run: |
      echo Code files: ${{steps.filter.outputs.code_files}}
  - name: "Changed Docs Files"
    run: |
      echo Docs files: ${{steps.filter.outputs.docs_files}}
```

{%endraw%}

I put all my jobs in a single [CI.yml](https://github.com/John-Robbins/tbp/blob/main/.github/workflows/CI.yml) file and each one has a conditional on it like the following.

{%raw%}

```yaml
lint-types-job:
  needs: fight-github-job
  name: "Type & Lint Checks"
  # Only run if we have changed code files.
  if: ${{needs.fight-github-job.outputs.code == 'true'}}
  . . .
test-cov-job:
  needs: [fight-github-job, lint-types-job]
  name: "Tests & Coverage"
  # Only run on changed code files.
  if: ${{needs.fight-github-job.outputs.code == 'true'}}
  runs-on: ${{ matrix.os }}
  . . .
build-website-job:
  needs: fight-github-job
  name: "Build Web Site"
  # Are there any document files that have changed?
  if: ${{needs.fight-github-job.outputs.docs == 'true'}}
  . . .
```

{%endraw%}

Now I have the best of both worlds. With skipped jobs always treated as successful in protected branches, I can require all five jobs for a PR to pass but only run the minimum set of jobs required by the changes. Ideally, GitHub would produce a fully supported solution for branch protections and required checks. However, after five years of asking, I don't think that's on the product backlog. If that's so, having the steps I outlined here to make branch protections and workflow jobs play well together would be invaluable in the documentation.

Overall, I'm loving GitHub Actions, protected branches, and the other changes! These are the kinds of features that I remember dreaming we could have back when I was working. While I hit a few bumps, which were minimal in the big scheme of life, I was very happy how my CI and project management parts in GitHub came together. If I could have only one ask it would be that the GitHub Actions documentation [Use cases and examples](https://docs.github.com/en/actions/use-cases-and-examples) section take a task based approach to the introduction. In my opinion, that wholistic approach would eliminate a lot of confusion in learning.

## What's Next for Tiny BASIC in Python?

My original goal for tbp was to do a project with Tiny BASIC in three phases with all phases having the same features.

1. A tree walking interpreter. (You are here.)
2. A virtual machine interpreter.
3. A Tiny BASIC compiler to a virtual machine.

I think tbp part 1 turned out OK, but there's plenty of room for improvement. Going into the project, I thought 60% of my problems would be on the programming languages side. I had no idea that the majority of problems would be basic infrastructure issues with Python. If I had started in C, I know I would have finished with phases 1 and a big chunk of 2 in the time it took me to get tbp done. I expected to be developing slower as I learned Python, but not this slow. Being completely truthful, Python has left a little bitterness in my mouth. I think, but don't know for sure, I've gotten over the first major Python development hurdle developing a module, but will I get over the next one as a novice Python developer? Given what I've gone through so far, I don't know whether I'll have the patience or energy to go through this again.

When I tackle phases two and three, I'll probably use another language.

---

[^1]: Gobsmacked is one of my favorite English words. It's a polite way of saying WTF.
[^2]: I have no idea who CyberZHG is, but I loved their GitHub tag line: "Knowledge is bacon. Please don't send emails." Bacon is glorious to me and I dislike email. I could be friends with CyberZHG.
[^3]: Is it weird that I think of Bob as my patron saint?
[^4]: Why a class on Numerical Analysis? I'd retired and went back to college to learn what I should have learned the first time around. In May 2024, I [graduated](https://new.unca.edu) with a double major in Mathematics and Spanish. Yay, me! :tada: My GPA was so much better the second time around, too!
[^5]: Should I attach my resume? :joy: My focus was on Windows where I worked on device drivers and developed or lead the development of error detection tools, profilers, and code coverage products at NuMega. I started and built a successful consulting company, Wintellect, where I focused on solving the kind of bugs where a company was losing millions of dollars a day. I've written [books](https://www.amazon.com/stores/John-Robbins/author/B001IXMLF0?ref=ap_rdr&isDramIntegrated=true&shoppingPortalEnabled=true) on debugging. Also, I presented at dozens of major conferences like Microsoft Tech-Ed, where I had my biggest audience ever of 5,000+ people! :scream_cat:
[^6]: Why does it seem Ruby is so hard to [install](https://www.moncefbelyamani.com/how-to-install-xcode-homebrew-git-rvm-ruby-on-mac/) on macOS? Is this normal?
[^7]: Sorry! A total [humblebrag](https://www.merriam-webster.com/dictionary/humblebrag).
[^8]: And pointing the fickle finger of blame!
