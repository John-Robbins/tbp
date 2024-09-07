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

## My Kingdom for an EBNF Grammar Checker

The very first task I wanted to complete was to build a solid Extended Backus-Naur form (EBNF) grammar for the Tiny BASIC language by hand. The file is [tiny_basic_grammar.ebnf](https://github.com/John-Robbins/tbp/blob/main/docs/tbp/tiny_basic_grammar.ebnf) in the tbp repository. Building robust grammars for a language is hard. There are a million edge cases and surprises that are waiting around dark corners to scare you. All the compiler textbooks discuss creating grammars extensively, and you start to realize that if you screw up the grammar in the beginning, you’ve made your life terrible.

This correctness was especially important to me because I am a programming language beginner. All the compiler text books I read stressed the importance of grammar correctness, avoiding [left recursion](https://en.wikipedia.org/wiki/Left_recursion), and the like. Given how many pages these textbooks spent on defining grammars, I was looking forward to working with tools that would help me in finding all the mistakes I was making. One would think EBNF grammar validators would be a keen area of development to help language designers avoid mistakes.

Yes, I am gobsmacked that EBNF validators aren’t a dime a dozen. [^1] I found a few academic websites that offered validators for experimental LR(0) grammars and other esoteric parsers. It seems like all the textbooks on compilers leave checking and validating your grammar is an "exercise for the reader." Why is that? Is that because all these programming language researchers and experienced compiler developers can cast a side eye across an EBNF grammar and just know it’s perfect? Is writing an EBNF validator as hard as solving the Riemann hypothesis? This really is a very strange situation to me, and I'd love to know why EBNF validators aren't common.

Years ago, I'd heard of the parser generator [ANTLR]( https://www.antlr.org), but I'm dealing with a language that has 12 statements and two functions. I wanted to do this by hand to learn and while ANTLR is very cool, but extraordinary overkill for my little project. Fortunately, ANTLR has its wonderful [Lab](http://lab.antlr.org) where you can interactively play around with rules and example text to see how they parse. I used it to get a clue about how some grammar rules would work and since the ANTLR grammar is close enough to EBNF, it helped a lot.

I spent my time hand walking the grammar I built, and it all looked OK. Here's where the narrator jumps in and says in that gorgeous, succulent, deep baritone, say "And John was wrong. Completely wrong."

Somehow, through internet magic, I saw a reference someplace on a blog where the writer said they tested their grammar on [http://instaparse.mojombo.com](http://instaparse.mojombo.com). Oh, my! An EBNF checker that works! It's not perfect, but if you refresh the page and paste in your grammar in after major changes, it works well. I found many, many problems in my first attempt at the grammar under Instaparse. A huge thank you and shout out to [Mark Engleberg](https://github.com/Engelberg) for writing [instaparse](https://github.com/Engelberg/instaparse), and [Matt Huebert](https://github.com/mhuebert) for hosting it. Much later, I found another tool, [EBNF Test](https://mdkrajnak.github.io/ebnftest/) by [mdkrajnak](https://github.com/mdkrajnak) which was also extremely helpful.

Wrestling with some left recursion problems, I found there are more sites dedicated to eliminating the left recursion in your life. I like the [left_rec]((https://cyberzhg.github.io/toolbox/left_rec)) tool from [CyberZHG](https://github.com/CyberZHG) the best. [^2] Definitely, keep this grammar recursion tools handy because you'll need them.

Obviously, I don't have a complete grasp of grammar development. My plan is to work through Chapter 2 in the [Dragon Book](https://www.malaprops.com/book/9780321486813) very carefully.

## The Grade for My Scanner: C-

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

## The Grade for My Parser and Interpreter: B/B-

Again, if you've read [Crafting Interpreters](http://www.craftinginterpreters.com) the tbp parse and interpreter should feel very familiar. As they stand now, both are solid, but it was some work to get there for both.

The main problem with the parser was that I had declared separate expression and statement types, and it got to be a mess coordinating them while parsing. After enough pain, I rethought everything and decided to go with a single base class I called a [`LanguageItem`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L160-L202). That helped a lot, but I still feel that there's more simplification possible. For example, I have a [`Assignment`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L258-L279) type and a [`LET`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L489-L503) type, which are really the same thing.

The interpreter bothers me a little because the class is so big. I don't know if there's a way to move functionality other places, but it is doing a lot of work. It's the execution engine and debugger, which makes up a lot of the code. Something I considered was making the `LanguageItem` derived types, like for `RND` or `PRINT` have ways to do their own work. That way as the interpreter is executing through the code, it could tell the [`Print`](https://github.com/John-Robbins/tbp/blob/main/src/tbp/languageitems.py#L451-L470) type, "Hey! Do your thing." passing in a callback if the `Print` type needed to evaluate its parameters.

Another thing that bothers me about both the `Parser` and `Interpreter` classes is that they both do output for reporting errors and general execution. It was convenient to do that, but it feels dirty to me.

## The Grade for tbp: B-

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

Fortunately, I found Grant Jenkins' [Python Sorted Containers](https://grantjenks.com/docs/sortedcontainers/), which is massive overkill for what I needed, but it did allow me to focus on my problem domain instead of me spending a lot of time developing my own implementation. If you use Sorted Containers, Hal Blackburn did a great job building the necessary [type stubs](https://github.com/h4l/sortedcontainers-stubs), so you get all the mypy goodness.

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

### What's Next for Tiny BASIC in Python?

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
[^5]: Should I attach my resume? :joy: My focus was on Windows where I worked on device drivers and developed or lead the development of error detection tools, profilers, and code coverage products. I started and built a successful consulting company where I focused on solving bugs where a company was losing millions of dollars a day. I've written [books](https://www.amazon.com/stores/John-Robbins/author/B001IXMLF0?ref=ap_rdr&isDramIntegrated=true&shoppingPortalEnabled=true) on debugging. Also, I presented at dozens of major conferences like Microsoft Tech-Ed, where I had my biggest audience ever of 5,000+ people! :scream_cat:
