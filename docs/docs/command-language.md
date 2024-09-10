---
title: tbp Command Language
nav_order: 4
layout: default
permalink: tbp-command-language
---
<!-- markdownlint-disable-next-line -->
# tbp Command Language
{:.no_toc}

1. TOC
{:toc}

---

## Overview

At the Tiny BASIC in Python (tbp) prompt, `tbp:>`, you can enter any statements and expression from the [Tiny BASIC language](tb-language) as well as those from the tbp command language, which this page documents. If a command starts with `%`, it is unique to tbp. I chose that symbol because it's an invalid character in the Tiny BASIC language, other than in a string, but most important it looks like a bug splatted on your monitor.[^1]

Note that the tbp command language is case-insensitive, and unlike the Tiny BASIC language, requires spaces.

## Information and State Commands

### Help: `%help`, `%?`

To see the full help, use `%help`. That output will include links to the documentation and the project. The short help, `%?` shows just the commands for quick reference.

### Quit: `%q`

Immediately quits tbp and returns you to your shell.

### Linting: `%lint`

Writing Tiny BASIC code is a little error-prone because of the required line numbers, lack of editor support, and so on. If anyone wants to write a tbp extension for [Visual Studio Code](https://code.visualstudio.com), be my guest. Pull requests are open! [^2]

Originally, I had some of these linter checks in the interpreter itself, but I pulled it out to a separate [file](https://github.com/John-Robbins/tbp/blob/main/src/tbp/linter.py) to make it easier to develop. Also, the [interpreter](https://github.com/John-Robbins/tbp/blob/main/src/tbp/interpreter.py) was already a very large file on its own.

This is not the most capable linter, but it has saved me a huge amount of time. There are currently four checks the `%lint` command performs.

#### Missing `END`

The `END` statement is important that it be the last statement executed by your program as it resets the state of the interpreter. This check simply looks to see if `END` is in your program but does not confirm the execution path to ensure it is called.

#### Using `CLEAR`

As the `CLEAR` statement reset the entire state of the interpreter, including removing the program from memory, you don't want to call this in your program. Unless you are crazy, but to each their own.

#### `GOTO`/`GOSUB` Target Invalid

It is so easy to mess up your `GOTO`/`GOSUB` targets. You're writing your magnum opus in Tiny BASIC, and you realize that the line numbers of the procedure you are working on is growing and about to bump into another procedure's line numbers. You rearrange everything, but you forgot to update the original `GOTO`/`GOSUB` calls. When you run your program, either you get the following error, or worse, your program is branching into the middle of places unknown, and you have random execution.

```text
Runtime Error: Error #046: GOTO subroutine does not exist '40'.
20 GOTO 40
---^
```

The linter looks at all hard coded `GOTO`/`GOSUB` targets and confirms those lines are in the program. By hard coded, that means a physically typed in integer such as `GOSUB 1250`. If the linter sees a branch statement that use expressions, it skips it. This lint check has saved me many hours of mistakes!

#### Potentially Uninitialized Variable Usage

There are two ways to initialize variables in Tiny BASIC, the [`LET`](tb-language#let---assignment) assignment statement or the [`INPUT`](tb-language#input---asking-the-user) statement asking the user of a value. With that in mind, I had the idea to start at the first line of the program and do the following:

1. If a `LET` or `INPUT` statement initialized a variable, store the variable in an initialized list.
2. If an expression uses a variable, and it was in the initialized list, consider it a good initialization.
3. If the variable wasn't in the initialized list, put it into a potentially uninitialized list.
4. At the end of the linting, look at the potentially uninitialized list and remove any variables that are in the initialized list.
5. Report any remaining variables in the potentially uninitialized list as errors.

#### `%lint strict` Deeper Uninitialized Variable Checking

The steps above are not the smartest algorithm, but sufficient to find dumb mistakes but not have a lot of false positives. Pondering a little more, I thought it would be good to skip step 4 in some situations.

If, for example, at the beginning of the Tiny BASIC program the code jumps down to a faraway location, initializes the variable, and branches back to the beginning. The earlier parts of the program are assuming the code properly initialized the variable, but what if the initialization didn't occur?

Assuming that variable initialization is a top-down process, if you run `%lint strict`, that's the behavior you'll get from the linter.

In the following example, you see that the default run of `%lint` see's that somewhere in the program initialized the variable `B`. The `%lint strict` is, well, stricter in that it sees `B` referenced on line 20, but there was no initialization prior to that.

```text
tbp:>list
10 GOSUB 50
20 PRINT "The random number is ";B;"."
30 END
50 LET B=RND(1000)
60 RETURN
tbp:>%lint
tbp:>REM The linter saw B was initialized somewhere.
tbp:>%lint strict
LINT #04: Potentially uninitialized variable 'B'.
20 PRINT "The random number is ";B;"."
---------------------------------^
```

Ideally, the next step would be to build an engine that would walk the program looking for the execution flow to find if the program initializes a variable during a run. That's something I do want to look at.

#### `%lint` Command Error Messages

| Linter Error Messages |
|-----------------------|
| LINT #01: Missing END statement in the program. |
| LINT #02: CLEAR must never be in a program. |
| LINT #03: GOTO/GOSUB target not in program: '%d'.|
| LINT #04: Potentially uninitialized variable '%s'.|

### Loading Files: `%loadfile` | `%lf`

Loads the specified file from disk. You must surround the filename by quote characters, which helps with filenames with spaces in them. After confirming the filename is valid, and the file exists, tbp resets the interpreter state to the equivalent to start up.

When loading a file, tbp assumes all lines in the file are [Tiny BASIC language](tb-language) statements, so any tbp command language commands will be reported as an error.

```text
tbp:>%lf "./examples/srps.tbp"
tbp:>
```

If the `run_on_load` option is true, the loaded file will automatically execute a [`RUN`](tb-language#run---execute-the-program-in-memory) statement. The default for `run_on_load` is false.

Obviously, you cannot use the `%loadfile` command if stopped at a breakpoint.[^3]

On macOS and Linux, tbp properly handles `~` expansion in the `%loadfile` command.

### Saving Files: `%savefile` | `%sf`

After developing your fantastic Tiny BASIC program, you can save it to disk for posterity. The filename parameter must be surrounded by quote characters.

On macOS and Linux, tbp properly handles `~` expansion in the `%savefile` command.

### Options: `%opt`

There are three options you can set to enhance your usage of tbp diagnostic logging, automatically running on file loading, and showing execution time for each line. If you don't include the third parameter, you will see the state of the current options.

The option command uses the following format:

```text
%opt required_option (true | false | <none>)
```

Note that instead of requiring you to type out `true` or `false`, they can be abbreviated to `t` or `f`.

Executing just the `%opt required_option` will show you the current state of that option.

#### Logging: `%opt log`

Controls diagnostic logging for tbp and helps with testing and debugging. The output can get overwhelming, but it is interesting to see the scanning, parsing, and execution states.

When scanning and parsing, the following shows the output for processing a Tiny BASIC source line.

```text
Scanning: `300 IF J = 1 THEN GOTO 682
`
[LINE_NUMBER (300,0)][IF (300,4)][IDENTIFIER (300,7)][EQUAL (300,9)][NUMBER (300,11)][THEN (300,13)][GOTO (300,18)][NUMBER (300,23)][CRLF (300,26)]
Parsing:
[Line# 300][IF ([Var J] [=] 1) [THEN [GOTO 682]]]
Interpreter state: State.FILE_STATE
`
```

The first line shows the source line about to be processed. The first part of the output shows the lexical scanner result. A token, `[IF (300,4)]` shows the token scanned followed by the line the token is on (i.e., the line number), which is 300 in this case. The second number is the column for the token, which is used in error reporting.

The parsing section shows the breakdown of the language items, or the abstract syntax tree representation. Finally, it shows the current state of the state machine inside the tree walking interpreter. The interpreter states are in the table below.

| State | Description |
|-------|-------------|
|`LINE_STATE` | The user is typing lines in directly at the tbp prompt.|
|`FILE_STATE` | When reading a file from disk into memory. |
|`RUNNING_STATE`| Executing a program. |
|`BREAK_STATE`| Stopped at a breakpoint.|
|`ERROR_FILE_STATE` | When reading lines out of a file, but had an earlier error so tbp continues parsing and reporting additional errors, but don't execute any code after finishing the file.|

When running a program in memory, the logging output shows you each line as it is executed. In the example below, you can see that the [`GOTO`](tb-language#goto---jump-to-line) was executed moving the instruction pointer from line 900 to line 180.

```text
Executing: `850 LET I = I + 1`
Executing: `900 IF I <= N THEN GOTO 180`
Executing: `180 LET J = C * (N - I)`
Executing: `200 IF J = 0 THEN GOTO 265`
```

#### Run Program on Load: `%opt run_on_load`

The default for tbp is to return to the tbp prompt after loading a file. If you would like tbp to automatically run your loaded programs, enter the following command. You will have to set this on each run or use the tbp command line start up command line option of [`--commands`](getting-started#run-commands-at-start).

```text
tbp:>%opt run_on_load t
tbp:>%opt run_on_load
Option: run_on_load is True.
tbp:>
```

#### Showing Line Execution Time: `opt time`

To see how many milliseconds it took for each line to execute, turn this option on.

```text
tbp:>%opt time t
tbp:>run
[800] = 0.0031 ms
[850] = 0.00405 ms
[900] = 0.00286 ms
[180] = 0.00691 ms
[200] = 0.00286 ms
[265] = 0.00215 ms
[270] = 0.00095 ms
[290] = 0.00215 ms
```

## The Tiny BASIC in Python Debugger

The tbp debugger is a full-featured debugger that allows breakpoints on lines, stepping, variable display, and call stack display. What more could a developer want? For this section, I will be debugging the [`pas.tbp`](https://github.com/John-Robbins/tbp/blob/main/examples/pas.tbp) program, which you can find in the tbp examples folder, if you would like to practice as you read along.

### Setting and Listing Breakpoints: `%bp` | `%break`

To start a debugging session, start by setting a breakpoint on the line number where you want to stop. In the example below, I wanted to set breakpoints on several lines of a loaded program.

```text
tbp:>list 180,220
180 LET J = C * (N - I)
200 IF J = 0 THEN GOTO 265
205 PRINT " ";
220 LET J = J - 1
tbp:>%bp 200
tbp:>list 620,645
620 IF X <> 0 THEN GOTO 612
640 LET Y = (C * 2) - Z
642 GOTO 675
645 PRINT " ";
tbp:>%bp 640
tbp:>
```

You can see the breakpoints you have set by entering the breakpoint command with no parameter.

```text
tbp:>%bp
Breakpoints set on:
200 IF J = 0 THEN GOTO 265
640 LET Y = (C * 2) - Z
```

### Deleting Breakpoints: `%d` | `%delete`

If you have a breakpoint set you want to clear, the `%d` command will do that for you. In the example below, I set a third breakpoint on line 605 that I want to clear with `%d 605`.

```text
tbp:>%bp
Breakpoints set on:
200 IF J = 0 THEN GOTO 265
605 REM Digit count
640 LET Y = (C * 2) - Z
tbp:>%d 605
tbp:>%bp
Breakpoints set on:
200 IF J = 0 THEN GOTO 265
640 LET Y = (C * 2) - Z
tbp:>
```

It might look odd to see a breakpoint set on a comment line, but tbp treats all lines as executable in the program. When it sees the [`REM`](tb-language#rem---remarkcomment) statement, tbp does nothing with the line.

If you want to clear all the breakpoints set, use the `%d *` command.

### Running Under the Debugger

With the breakpoints set, it is very simple to start the debugger. You do it like you would any program with the Tiny BASIC [`RUN`](tb-language#run---execute-the-program-in-memory) statement.

```text
tbp:>%bp
Breakpoints set on:
200 IF J = 0 THEN GOTO 265
640 LET Y = (C * 2) - Z
tbp:>RUN
Breakpoint: 200
[200 IF J = 0 THEN GOTO 265]
DEBUG(200):>
```

When you hit a breakpoint, tbp displays the line in square brackets and changes the prompt to show you are in the debugger with `DEBUG` and the line number of the breakpoint. In this case, the prompt is `DEBUG(200):>`.

### Show Variables: `%v` | `%vars`

You can look at all the *initialized* variables with the `%v` command. In fact, the `%v` command is so useful it is available even when you are not debugging. It is so much more convenient than typing `PR A,B,C,D` over and over.

```text
tbp:>RUN
Breakpoint: 200
[200 IF J = 0 THEN GOTO 265]
DEBUG(200):>%v
C=3         I=1         J=27        N=10        S=256
DEBUG(200):>
```

### Step: `%s` | `%step`

With the breakpoint on line 200 there is a `IF` and if `J = 0` a [`GOTO`](tb-language#goto---jump-to-line) occurs. As you can see above, currently, `J = 27`. The `%s` command is smart enough to step you to the correct line, which in this case is the next line after line 200.

```text
DEBUG(200):>%s
[205 PRINT " ";]
DEBUG(205):>
```

### Continuing Execution: `%c` | `%continue`

To continue full execution from a breakpoint you **must** use the `%c` command. This was a design decision as the intent of the [`RUN`](tb-language#run---execute-the-program-in-memory) statement is to start the program and I felt it would be confusing to have different meanings to the command.

```text
DEBUG(205):>RUN
CLE #16: Use %c to continue from a breakpoint instead of RUN.
DEBUG(205):>%c
Breakpoint: 200
[200 IF J = 0 THEN GOTO 265]
DEBUG(200):>%vars
C=3         I=1         J=26        N=10        S=256
DEBUG(200):>
```

### Seeing the Call Stack: `%bt` | `%backtrace`

While Tiny BASIC is not a language you are going use to write a recursive descent parser, it does support calling procedures with [`GOSUB`](tb-language#gosubreturn---call-toreturn-from-a-procedure) and [`RETURN`](tb-language#gosubreturn---call-toreturn-from-a-procedure). Using the [`deep.tbp`](https://github.com/John-Robbins/tbp/blob/main/examples/deep.tbp) test program here's an example of its output.

```text
DEBUG(200):>%bt
-- Call Stack --
330 RETURN
430 RETURN
530 RETURN
630 RETURN
730 RETURN
830 RETURN
930 RETURN
40 END
DEBUG(200):>
```

### Exiting the Debugger: `%e` | `%exit`

If you want to stop debugging and end program execution while at a debugger prompt, use the `%e` command to return to the normal tbp prompt.

```text
DEBUG(420):>%exit
tbp:>
```

### Debugging Tips and Tricks

When stopped at the debugger prompt, if you want to change a variable, use the regular Tiny BASIC assignment statement.

```text
[600 LET N = N / I]
DEBUG(600):>%v
I=3         K=0         N=10023     S=256
DEBUG(600):>K=10
DEBUG(600):>%v
I=3         K=10        N=10023     S=256
DEBUG(600):>
```

At the normal tbp prompt (`tbp:>`), you delete a line simply by entering its number and pressing enter. While debugging, you can change any lines you would like to fix coding errors.

```text
[600 LET N = N / I]
DEBUG(600):>600 LET N = (N*2) / (I-1)
DEBUG(600):>LIST 600
600 LET N = (N*2) / (I-1)
DEBUG(600):>
```

It is also a good habit while debugging, to save your program with the `%savefile` command to ensure you don't lose your hard work.

With the tbp debugger, you have been given great power. Use it wisely.[^4]

## Error Codes from the tbp Command Language

| Command Language Error Messages |
|---------------------------------|
| CLE #01: Invalid or unknown command : '%s'. |
| CLE #02: Missing required filename or missing quote delimiters for %savefile/%openfile.|
| CLE #03: No program in memory to save. |
| CLE #04: Required option is missing. |
| CLE #05: `%break` and `%delete` commands require line numbers as parameters: '%s' |
| CLE #06: Line does not exist in the program: '%d'. |
| CLE #07: No breakpoint set on the line: '%d'.|
| CLE #08: %s only works when debugging. |
| CLE #09: Deleting program lines while debugging disabled. |
| CLE #10: Branch target does not exist '%d'. |
| CLE #11: RETURN call stack is empty. |
| CLE #12: Filename is invalid '%s'. |
| CLE #13: File does not exist '%s'. |
| CLE #14: Breakpoint already set on '%d'. |
| CLE #15: %loadfile disabled while debugging. |
| CLE #16: Use %c to continue from a breakpoint instead of RUN. |

---
[^1]: Well, that made me laugh and that's all that matters.
[^2]: Please don't. It's already goofy that I've spent so much time on tbp. You don't need to board the obsessive train I am on.
[^3]: Universal levels of chaos would ensue if tbp let you load files, thus completely changing the world in the middle of a debugging session! I'm doing my part to prevent singularity from occurring. Yes, I am a hero.
[^4]: Or go nuts and see what you can get away with. :joy_cat:
