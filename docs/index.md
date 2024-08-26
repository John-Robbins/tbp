---
title: Tiny BASIC in Python
nav_order: 1
layout: default
permalink: /
---
<!-- https://github.com/ikatyang/emoji-cheat-sheet -->

<!-- markdownlint-disable-->
# Tiny BASIC in Python
{:.fs-9}

{:.fs-6.fw-300}
Dress up in your best corduroy suit or patterned jumper, it's time for some disco, so put the Bee Gees latest 45 on the turn table!

OK, you really don't have to dress in the epitome of 1970s fashions, do the bump, or listen to disco, but you will enjoy programming like it's 1976! Tiny BASIC in Python (tbp) is an implementation of the [Tiny BASIC language](https://en.wikipedia.org/wiki/Tiny_BASIC) that ran on the Intel 8080, the Motorola 6800, and the MOS Technologies 6502 processors and fit into 4K of memory.

Obviously, tbp is *humongous* compared to the original, but it served as a way for [me](https://github.com/John-Robbins) to learn about the infrastructure of programming languages.

It is a full-featured programming environment for the [Tiny BASIC language](tb-language). It also includes a full [debugger](tbp-command-language#the-tiny-basic-in-python-debugger), a [linter](tbp-command-language#linting-lint), and complete documentation, which you are now reading. It's also the first project I've ever done in Python.

Any problems/confusion? Please file an [issue](https://github.com/John-Robbins/tbp/issues) in the repository. I thank you kindly in advance!

## Some Usage Hints

The links on the left of this page have detailed discussion of installation, usage, the Tiny BASIC language, and the tbp command language that controls the programming environment.

### Prompts and Command Line Editing

In tbp you will see various command line prompts.

- `tbp:>` - The normal tbp prompt where you can enter both the Tiny BASIC language and the tbp command language.
- `[A]?` - This prompt says a program is asking you for input with the [`INPUT`](tb-language#input---asking-the-user) Tiny BASIC statement.
- `DEBUG(213):>` - When you stop at a breakpoint, this prompt shows the line number you stopped on. In this case, it is line `213` in your program. See the [tbp debugger](tbp-command-language#the-tiny-basic-in-python-debugger) documentation for details about the debugger commands and help debugging.

The tbp command line uses Python's [readline](https://docs.python.org/3/library/readline.html#module-readline) module so all the normal editing, copy, paste, and arrow keys work.

## Example Programs

The [examples](https://github.com/John-Robbins/tbp/blob/main/examples) directory holds sample Tiny BASIC programs for your enjoyment. Some of these programs come from other sources and I provide links back to the original code. The original developers hold the copyrights to their work. In a few minor cases I had to slightly change the program to work under tbp, which I documented in comments at the top of the file. I appreciate and thank the others who wrote these programs and shared them. [^1]

- [adventure.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/adventure.tbp)
  - Tiny Adventure game from [The First Book of Tiny BASIC Programs](https://www.retrotechnology.com/memship/Son_of_TFBOTBAS.HTM#chapter6) by Tom Pittman. This is a complicated game so read the documentation before playing.
- [deep.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/deep.tbp)
  - A test program for the tbp debugger that generates a deep call stack.
- [eurphoria.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/eurphoria.tbp)
  - Kingdom of Euphoria game from [The First Book of Tiny BASIC Programs](https://www.retrotechnology.com/memship/Son_of_TFBOTBAS.HTM#chapter3) by Tom Pittman.
- [fib.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/fib.tbp)
  - Generates Fibonacci numbers. From the excellent [Marco's Retrobits](HTTPS://RETROBITS.ALTERVISTA.ORG).
- [fizzbuzz.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/fizzbuzz.tbp)
  - An implementation of [Fizz Buzz](https://en.wikipedia.org/wiki/Fizz_buzz) from the always fascinating [Rosetta Code](https://rosettacode.org/wiki/Rosetta_Code). The original implementation is [here](https://rosettacode.org/wiki/FizzBuzz/Basic#Tiny_BASIC). I updated the code to use line numbers.
- [fizzbuzz2.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/fizzbuzz2.tbp)
  - Another implementation of [Fizz Buzz](https://en.wikipedia.org/wiki/Fizz_buzz) from [Winston (Winny) Weinert's](https://github.com/winny-/tinybasic.rkt/blob/master/tinybasic-examples/examples/fizzbuzz.rkt) very cool implementation of Tiny BASIC in Racket.
- [gotoheck.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/gotoheck.tbp)
  - A test program for the tbp debugger that implements all sorts of `GOTO`/`GOSUB` statements.
- [life.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/life.tbp)
  - Conway's Game of Life from Tom Pittman's [Tiny BASIC](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/LifeTB.txt) site.
- [lintdemo.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/lintdemo.tbp)
  - A modified version of the Sum of Squares and Cube Digits (see below) to demonstrate tbp's `%lint` command.
- [pas.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/pas.tbp)
  - A fantastic implementation of [Pascal's Triangle](https://en.wikipedia.org/wiki/Pascal's_triangle) by [Winston (Winny) Weinert's](https://github.com/winny-/tinybasic.rkt/blob/master/tinybasic-examples/examples/pascals-triangle.rkt) for his implementation of Tiny BASIC in Racket.
- [prime-decomp.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/prime-decomp.tbp)
  - An implementation if [integer factorization](https://en.wikipedia.org/wiki/Integer_factorization) originally from [Rosetta Code](https://rosettacode.org/wiki/Prime_decomposition#Tiny_BASIC). I changed the program to make the output cooler.
- [rand.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/rand.tbp)
  - One of the examples from the [Tiny BASIC User Manual](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/TBuserMan.htm) that shows 64 random numbers.
- [sq-cu-digits.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/sq-cu-digits.tbp)
  - A program from [Rosetta Code](https://rosettacode.org/wiki/Sum_of_square_and_cube_digits_of_an_integer_are_primes#Tiny_BASIC) that finds and shows here all positive integers n less than 100 where, the sum of the digits of the square of n is prime, and the sum of the digits of the cube of n is also prime.
- [srps.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/srps.tbp)
  - My *SASSY* Rock, Paper, Scissors game. Made with Tiny BASIC AI. (Can I get funding now that I mentioned AI?)
- [tbp.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/tbp.tbp)
  - A program to print the Tiny BASIC in Python logo because you can never look at it enough.
- [tflash.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/tflash.tbp)
  - The original FLASHCARD program from [The First Book of Tiny BASIC Programs](https://www.retrotechnology.com/memship/Son_of_TFBOTBAS.HTM#chapter4)
- [tic-tac-toe.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/tic-tac-toe.tbp)
  - The original [tic-tac-toe game](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/TicTac.htm) from the January 19, 1977, issue of the Homebrew Computer Club Newsletter by Tom Pittman.
- [ttt-c.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/ttt-c.tbp)
  - The *compressed* version of the [tic-tac-toe game](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/TicTac.htm) from the January 19, 1977, issue of the Homebrew Computer Club Newsletter by Tom Pittman.


[^1]: Note that I am not a lawyer but feel it was OK to share other's work like this. If that's not a correct interpretation, let me know as soon as possible, and I will take these programs down.


