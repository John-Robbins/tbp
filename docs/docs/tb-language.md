---
title: Tiny BASIC Language
nav_order: 3
layout: default
mathjax: true
permalink: tb-language
---
<!-- markdownlint-disable-next-line -->
# Tiny BASIC Language
{:.no_toc}

1. TOC
{:toc}

---

## Overview

This document describes the dialect for the Tiny BASIC language implemented by Tiny BASIC in Python (tbp). As BASIC itself is barely older than I am, evolution has created many BASIC dialects.[^1] For this project, my lodestar is the true Tiny BASIC from the [January 1976](https://archive.org/details/dr_dobbs_journal_vol_01/page/n89/mode/2up) issue of Dr. Dobb’s Journal of Computer Calisthenics & Orthodontia, which is **wild** reading after almost 50 years of breakneck computer innovation.

Tiny Basic is, well, tiny! Compared to something like [Python's language reference](https://docs.python.org/3/reference/index.html), Tiny BASIC is 12 statements, two functions, and 26 succulent variables. Even that small, Tiny BASIC can still produce some fantastic programs, some of which you can see in the project's [examples](https://github.com/John-Robbins/tbp/tree/main/examples) folder. In this documentation, I want to cover salient points on how tbp implements the language. The original documentation of Dr. Tom Pittman's version is [The TINY BASIC User Manuel](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/TBuserMan.htm) and is worth looking at for a deeper background. It is also interesting to learn about all the contortions necessary to smash a full interpreter into 4 kilobytes of memory.

In tbp, I've mostly tried to stay to the size limitations of the original. Integers are 16-bit, so that's a number range of -32,768 to +32,767. Another limitation I've kept is "spaces are optional." Back in 1976, Tiny BASIC cared deeply about space and one of the ways the accomplished that was removing spaces in your programs. Thus, in Tiny BASIC, spaces are optional. By stripping out spaces, you could save considerable amounts of space. Pun intended! In the project [examples](https://github.com/John-Robbins/tbp/tree/main/examples) folder, you can find two Tic-Tac-Toe programs. The [readable one](https://github.com/John-Robbins/tbp/blob/main/examples/tic-tac-toe.tbp) has spaces, but [ttt-c.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/ttt-c.tbp) is the compressed version with spaces removed.

Why did they care about space so much back then? Tom Pittman uploaded a Tiny BASIC [programming manual](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/ProgTB/ProgTB0.htm) for the [Netronics ELF](https://en.wikipedia.org/wiki/ELF_II), whose base model came with 256 bytes of RAM.[^2] Read that number in the last sentence slowly.

Below is an example of a valid Tiny BASIC source code line.

```text
641IFI>1IFI<9IFI=I/2*2+1GOTO633
```

As spaces are optional, the line below is also valid in the language and tbp stores it exactly as typed.

```text
2   4   4   5   0    i F   V   / X     *2     *    Q >0  G    o  T  o   4   6  1  0
```

If you looked closely at the second example, you might have noticed that Tiny BASIC is case-insensitive as well. You may not want to write code using either of the above as examples. Talk about a maintenance hell! [^3]

## Direct Execution vs. A Statement vs. Command Language

You can execute Tiny BASIC statements in two ways. At the tbp prompt, `tbp:>`, you can directly execute a statement like [`RUN`](#run---execute-the-program-in-memory), which is more like a command. If the line begins with a number, it's considered a program line and tbp stores it in memory for later execution.

If a statement starts with `%`, that is a [tbp command language](tbp-command-language) statement. Those are what you can use for executing the [debugger](tbp-command-language#the-tiny-basic-in-python-debugger), running the [linter](tbp-command-language#linting-lint), and setting various options in tbp. You can read more about those command in the Command Language section.

## Expressions

Tiny BASIC supports your standard mathematical operators, as well as parenthesis for grouping. In the expressions you can use numerical values and your 26 global variables, `A`...`Z`.

Some examples of expressions are below.

```text
A * (I - J) / J
(I-I/4096*4096)/256
```

The functions, `RND` and `USR` can also appear in expressions. See the discussion of those in the [Functions](#functions) section below.

One very important difference between the original Tiny BASIC and the tbp implementation is that in tbp, it checks all variable access at runtime and if you did not initialize a variable, it's reported as a runtime error and your program terminates. The example below shows this checking.

```text
tbp:>10 INPUT A
tbp:>20 PRINT B
tbp:>30 END
tbp:>run
[A]? 10
Runtime Error: Error #336: Accessing uninitialized variable 'B'.
20 PRINT B
---------^
tbp:>
```

Additionally, the [`%lint`](tbp-command-language#linting-lint) command language command can check for uninitialized variable usage before you run the program.

## Statements

### `REM` - Remark/Comment

Documenting your code is crucial, and the `REM` statement is your tool. You can use `REM` as a direct execution statement if you want to leave notes to yourself at the tbp prompt. In your program, putting a line number in front of a comment and that comment will stay with the program even when saved and loaded from files.

In the original implementation of Tiny BASIC, when it loaded a line into memory, the interpreter would look to see if a line started with a number. If it did, the interpreter loaded the line into memory and didn't parse it until it executed. If a [`GOTO`](#goto---jump-to-line) jumped over that line, it never gets parsed. If you look at some original programs from the 1970s, there are lines like the following.

```text
130 .  0 IS EMPTY, 1 IS X. 3 TS O
140 I HAS CURRENT POSITION
150 G IS PEEK ROUTINE ADDRESS
160 P IS POKE ROUTINE ADDRESS
```

In tbp, I made the decision to parse lines when entered before storing them memory. Therefore, the above lines are syntax errors in tbp instead of runtime errors.

### `LET` - Assignment

There are two valid Tiny BASIC ways to perform assignments:

```text
100 LET A = A * (I - J) / J
110 A = A * (I - J) / J
```

The `LET` is optional for assignment, but I think it is good practice to include it as it makes it more obvious what the statement is doing.

While you are debugging in tbp, you can use either form as direct execution statements to change variable values for testing and analysis as shown below.

```text
tbp:>A=420
tbp:>Z=999
```

### `INPUT` - Asking the User

There are no fancy dialogs or prompts to get user input in Tiny BASIC, only `INPUT`.

```text
INPUT A
INPUT X, Y, Z
```

After the `INPUT` statement, you specify the variables you want filled in by the user. The only values allowed are integers. However, you can build expressions as input so at a `INPUT` prompt, you could enter `(A*2/(X+3))`. The result of that expression evaluation becomes the value for the specified `INPUT` variable.

The original Tiny BASIC simply shows a `?` when asking for input. In tbp, I show the variable the program is asking for because I found it helpful for debugging Tiny BASIC programs. In most cases you will see a single character in brackets like the following where I'm running the [prime-decomp.tbp](https://github.com/John-Robbins/tbp/blob/main/examples/prime-decomp.tbp) program. The `[N]?` says the program is asking you for the `N` variable.

```text
Prime Decomposition!
Enter a number: [N]?
```

In the direct execution example below, I wanted to get input for the `A`, `B`, and `C` variables. The prompt shows asking for the three variables, `[A,B,C]`. After pressing ENTER after each entry, you see the input prompt showing, on the left side of the prompt, which variable you are filling. At the end, I execute the [`%vars`](tbp-command-language#looking-at-variables-v--vars) (show variables) command language command to show the result of the initialized variables.

```text
tbp:>input a,b,c
[A,B,C]? 10
[B,C]? 20
[C]? 30
tbp:>%vars
A=10        B=20        C=30
```

When entering multiple variables, you can separate them with commas as shown below.

```text
tbp:>INPUT A,B,C
[A,B,C]? 5,10,15
tbp:>%vars
A=5         B=10        C=15
```

You do not have to enter everything at once. The example below also shows using expressions are part of the entry.

```text
tbp:>INPUT A,B,C
[A,B,C]? 1,2
[C]? (A+100)*B
tbp:>%vars
A=1         B=2         C=202
```

Some of you might be wondering what if I enter more data than `INPUT` is asking for?

```text
tbp:>INPUT A,B,C
[A,B,C]? 2,4,6,8,10
WARN #001: More input given than variables requested by INPUT.
```

I treat that as a warning. The original Tiny BASIC had a scheme where it stored the extra entry for the next `INPUT` command, but I never saw an example where any program used it, so did not implement that feature.

### `PRINT` - Output

It might be nice show data to the user of your awesome Tiny BASIC program and that's your `PRINT` statement, which you can abbreviate to `PR` for space savings. This is the one statement that can work with string data. You may pass any sort of mix of strings, expressions, or the two print separators,`,` and `;`.

```text
tbp:>PRINT A
2
tbp:>PR (A*B)*(C*D)
384
```

The default is to print the output followed by a carriage return/line feed as shown above. The print separators give you some control over the placement of the output. The `;` separator tells `PRINT` statement to leave no spaces between the expressions when printing it.

```text
tbp:>%vars
A=2         B=4         C=6         D=8
tbp:>PRINT A;B;C;D
2468
tbp:>PRINT "(A*B)*(C*D)=";(A*B)*(C*D)
(A*B)*(C*D)=384
```

The `;` separator is useful when asking for user input as the `INPUT` statement will appear on the same line.

```text
tbp:>10 PRINT "How old are you?";
tbp:>20 INPUT P
tbp:>30 END
tbp:>RUN
How old are you?[P]? 29
tbp:>
```

The `,` print separator justifies the output in columns of eight characters wide.

```text
tbp:>PRINT A,B,C,D
2       4       6       8
```

Finally, a little quiz. What does the following statement do?

```text
PRI
```

It's not a syntax error. It's equivalent to `PRINT I`.

### `GOTO` - Jump to Line

While you might not know of the [paper](https://homepages.cwi.nl/~storm/teaching/reader/Dijkstra68.pdf), you have heard of Edgar Dijkstra's famous quote, "Go To Statement Considered Harmful". [^4]

The parameter can be a number, a variable, or a full expression, used to calculate locations at runtime. In tbp, the `GOTO` statement does nothing when directly executed.

```text
tbp:>10 GOTO 30
tbp:>20 PRINT "Hiding in plain sight!"
tbp:>30 END
tbp:>run
tbp:>
```

The [`%lint`](tbp-command-language#linting-lint) command built into tbp will check the program in memory for `GOTO` statements with hard coded expressions, `GOTO 125`, whose line number does not exist in the program.

### `GOSUB`/`RETURN` - Call to/Return from a Procedure

Much like `GOTO`, a `GOSUB` jumps to a line, as given by an expression, variable, or hard coded number, but also pushes the next line on the call stack. Once the procedure finishes, it's `RETURN` statement will transfer control to the item popped off the top of the stack.

```text
tbp:>10 GOSUB 50
tbp:>20 PRINT "...my old friend!"
tbp:>30 END
tbp:>50 PRINT "Hello again..."
tbp:>60 RETURN
tbp:>run
Hello again...
...my old friend!
tbp:>
```

If there's no item on the call stack, `RETURN` reports an error.

```text
tbp:>LIST
10 GOSUB 50
20 PRINT "...my old friend!"
30 RETURN
50 PRINT "Hello again..."
60 RETURN
tbp:>RUN
Hello again...
...my old friend!
Runtime Error: Error #133: RETURN called with an empty call stack.
30 RETURN
---^
tbp:>
```

The [`%lint`](tbp-command-language#linting-lint) command built into tbp will check the program in memory for `GOSUB` statements with hard coded expressions, `GOSUB 999`, whose line number does not exist in the program.

### `IF` - Conditional Statement

The `IF` statement form is worth showing as `THEN` is optional.

```text
IF expression rel_op expression THEN statement
IF expression rel_op expression statement
```

|Relational Operator| Meaning|
|-------------------|--------|
| `=` | Equality|
| `<` | Less than|
| `>` | Greater than |
| `<=`| Less than or equal |
| `>=`| Greater than or equal|
| `<>` | Not equal|
| `><`| Not equal|

Below are examples of valid `IF` statements.

```text
IF A > 3 THEN PRINT "A > 3"
IF N/P*P=N GOTO 350
IF M * N > Q IF V <> (B/W) GOSUB 9540
```

The last example is equivalent to the following in Python.

```python
if ((M * N) > Q) and (V != (B/W)):
    call_9540()
```

### `END` - End and Clean Up

The `END` statement must be the last statement executed by your program as that tells the interpreter the program finished. That way the interpreter cleans up the call stack, runtime state, memory, and any one-shot breakpoints (used by the [`%step`](tbp-command-language#step-s--step) command language command) You may have multiple `END` statements in your program as needed.

The [`%lint`](tbp-command-language#linting-lint) command built into tbp will ensure you have at least one `END` statement in your program but does not ensure it executes.

### `RUN` - Execute the Program in Memory

In addition to executing the program in memory, starting at the first line, you can use `RUN` to pass values to the [`INPUT`](#input---asking-the-user) statements in the program much command line arguments in your operating system’s shell.

```text
tbp:>10 INPUT A,B
tbp:>20 PRINT "A=";A
tbp:>30 PRINT "B=";B
tbp:>40 END
tbp:>run
[A,B]? 1
[B]? 2
A=1
B=2
tbp:>run,11,22
A=11
B=22
tbp:>run 33,44
A=33
B=44
tbp:>
```

In the latter two `RUN` commands above, you see the parameter passing the statement supports. As the original Tiny BASIC supported the comma first approach, I did in tbp as well. One difference in tbp is that I don't support using `RUN` parameters when used inside a program. In tbp, it will report a warning about the parameters and ignore them.

### `CLEAR` - Clear and Reset the Interpreter

After executing a `CLEAR`, the entire program, its state, one-shot breakpoints, and call stacks return to the default state. Like the original Tiny BASIC, tbp **does not** reset any variables.

The [`%lint`](tbp-command-language#linting-lint) command built into tbp will check the program in memory for `CLEAR` statements in a program, because you just don't want to do that.[^5]

### `LIST` - Display the Program in Memory

A `LIST` statement by itself lists the entire program.

```text
tbp:>10 GOSUB 50
tbp:>20 PRINT "...my old friend!"
tbp:>30 RETURN
tbp:>50 PRINT "Hello again..."
tbp:>60 RETURN
tbp:>list
10 GOSUB 50
20 PRINT "...my old friend!"
30 RETURN
50 PRINT "Hello again..."
60 RETURN
tbp:>
```

To see a single line, pass that line as a parameter.

```text
tbp:>list 30
30 RETURN
tbp:>
```

If the line parameter does not exist, `LIST` shows the program from the next higher line to the end.

```text
tbp:>list 25
30 RETURN
50 PRINT "Hello again..."
60 RETURN
tbp:>
```

You can also pass a second parameter to say you want to see the lines between those lines.

```text
tbp:>LIST 20,30
20 PRINT "...my old friend!"
30 RETURN
tbp:>
```

The two parameters must be in ascending order.

```text
tbp:>list 30,20
Runtime Error: Error #337: LIST parameters must be in logical order, not '30','20'.
list 30,20
^
tbp:>
```

In a final note, the parameters to the `LIST` statement can be any valid Tiny BASIC expressions. You could use `LIST` in your program to display help, for example.

## Functions

You can use the two functions supported in Tiny BASIC in any expression necessary.

### `RND` - Generate Random Number

```text
tbp:>A=RND(100)
tbp:>PR A
18
tbp:>B=RND(A*4)
tbp:>PR B
54
tbp:>
```

The parameter to `RND` is the range and the random number returned is between $$[0,n)$$.

### `USR` - Call Machine Language Subroutine

Tiny BASIC, as you can see, has limitations. To allow features like manipulating memory and talking to hardware, the `USR` function let you incorporate machine code into the environment. You can read more about how you could use the original `USR` function in the [Tiny BASIC Experimenter's Kit](http://www.ittybittycomputers.com/IttyBitty/TinyBasic/TBEK.txt).

The `USR` function depends heavily on the memory layout of Tiny BASIC. Since tbp is a tree walking interpreter, supporting the same would have been difficult and, honestly, pointless. With my goal of running as many of the original programs as I could in tbp, I implemented just enough to allow of `USR` to run the original [Adventure](https://github.com/John-Robbins/tbp/blob/main/examples/adventure.tbp), Conway's game of [Life](https://github.com/John-Robbins/tbp/blob/main/examples/life.tbp), and Tic-Tac-Toe games, but [readable](https://github.com/John-Robbins/tbp/blob/main/examples/tic-tac-toe.tbp) and [compressed](https://github.com/John-Robbins/tbp/blob/main/examples/ttt-c.tbp). In tbp, I supported the two key routines, reading a byte from memory, and writing a byte to memory. The read routine is at address 276 (0x114) and the write routine is at 280 (0x118). Those are the only two routine addresses allowed, and others cause an error.

By convention, Tiny BASIC programs used the `S` variable to hold the start of the Tiny BASIC interpreter in memory. For the Motorola 6800 CPU, that is 265 (0x100), and tbp does the same. There were different start addresses for different CPUs. Thus, `S+20` is the read byte routine, and `S+24` is routine to write a byte.

To read a byte from memory, the first parameter to `USR` is the read routine and the second is the address the user wants to read. To write a byte to memory, the first parameter is the byte write routine, the second is the address to write to, and the third is the byte to write. The following program shows writing and reading in action.

```text
tbp:>10 PRINT "Enter a number between 0 and 256";
tbp:>20 INPUT A
tbp:>30 REM Write the byte.
tbp:>40 USR(S+24, 100, A)
tbp:>50 REM Read the byte back.
tbp:>60 LET P=USR(S+20, 100)
tbp:>70 PRINT "Read ";P;" from memory address 100"
tbp:>80 END
tbp:>RUN
Enter a number between 0 and 256[A]? 222
Read 222 from memory address 100
tbp:>
```

## Error Codes and Messages

In tbp, I tried to make the reported errors as useful as possible by showing the source line and pointing to the column with the error. In the example below, I ran the program shown in the [`USR`](#usr---call-machine-language-subroutine) documentation and entered a value out of range.

```text
Enter a number between 0 and 256[A]? 299
Runtime Error: Error #362: USR write routine on supports values in AReg between 0 and 256, given '299'.
40 USR(S+24, 100, A)
------^
```

The original Tiny BASIC used error codes in the range 0-330, inclusive. I conformed to that as well, but didn't duplicate the many "`[statement] is not followed by an END`" error messages.

|Error Messages |
|----------------|
| Error #009: Line number '%d' not allowed. |
| Error #013: No program in memory to run. |
| Error #018: LET is missing a variable name but found '%s'. |
| Error #020: LET is missing an '=‘ but found '%s'. |
| Error #023: Improper syntax in LET, no right-side expression. |
| Error #037: Missing line number for 'GOTO or GOSUB'. |
| Error #046: GOTO (GOSUB) subroutine does not exist '%d'. |
| Error #104: INPUT expected a variable name but found '%s'. |
| Error #133: RETURN called with an empty call stack. |
| Error #224: Division by zero. |
| Error #293: Syntax error - unexpected expression '%s'.|
| Error #296: Syntax error - %s. |
| Error #330: IF is missing the relational operator but found '%s'. |
| Error #331: Unterminated string (started at position '%s') |
| Error #335: No END in the program. |
| Error #336: Accessing uninitialized variable '%s'. Defaulting to '%d'. |
| Error #337: LIST parameters must be in logical order, not '%d', '%d'. |
| Error #338: LIST parameters must be in the range 1 to 32767 not '%d'. |
| Error #339: Separators or colons cannot be the first item in a PRINT statement. |
| Error #345: GOSUB return address is invalid. |
| Error #347: Line number is not in the program: '%d' |
| Error #350: Aborting RUN from INPUT entry. |
| Error #351: Invalid value in INPUT: '%s'. Setting '%s'=0 as default. |
| Error #360: USR only supports read (276) or write (280) subroutines, given '%d'|
| Error #361: USR read/write routines require an address in XReg.|
| Error #362: USR write routine requires a value in AReg.|
| Error #362: USR write routine on supports values in AReg between 0 and 256, given '%d'.|

Note that you will only see "Error #347: Line number is not in the program: '%d'" when working with tbp interactively. When loading from a file, tbp ignores lines with only a line number. That allows one to use number lines with no content for spacing to separate routines and aid readability.

---
[^1]: Oh my! I just realized I'm old! 🫣
[^2]: **Bytes, people. BYTES! B.Y.T.E.S!** You've allocated arrays bigger than that on the stack before.
[^3]: Or permanent job security?
[^4]: No discussion of `GOTO` would be complete without [xkcd](https://xkcd.com/292/) because Randall Munroe has a comic for everything. (It's his superpower.) Thirty-three years after his famous letter to the editor, Dijkstra had some [ragrets](https://www.cs.utexas.edu/%7EEWD/transcriptions/EWD13xx/EWD1308.html).
[^5]: Then again, that might make debugging *very* interesting if a `CLEAR` command disappears your program. Hmm. Maybe allowing `CLEAR` inside a tbp program would be like a real-life murder mystery?
