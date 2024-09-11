"""The driver that controls the tbp tree walking interpreter."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

import logging
import re
from enum import Enum, auto
from importlib.metadata import version
from secrets import randbelow
from typing import ClassVar, NamedTuple

from tbp.helpers import load_program, print_output, read_input, save_program, tbp_logger
from tbp.interpreter import Interpreter


class Driver:
    """
    The driver class for the Tiny BASIC in Python Tree Walking interpreter.

    In an effort to not make the Interpreter class thousands of line long with
    file IO, command line argument processing, and even the debugger!

    The idea is that the actual command line code won't have to do much work at
    all because this class really is the command line program. Also, this makes
    testing so much easier since we won't have to spawn a program for testing.
    """

    # Various constants used in the driver.
    _CMD_LANG_PREFIX = "%"
    # The default prompt.
    _DEFAULT_PROMPT = "tbp:>"

    class Options(NamedTuple):
        """Options container."""

        # Set to true if the user does not want to see the awesome tbp logo. 😿
        nologo: bool
        # The program to load.
        file: str
        # Any commands the user wants to execute as soon as tbp loads.
        commands: str

    class CmdResult(Enum):
        """The return types for reporting command language results."""

        # The command was handled, so continue normally.
        CONTINUE = auto()
        # The user wants to quit.
        QUIT = auto()

    def __init__(self: Driver) -> None:
        """Initialize the driver."""
        # We kind of need this.
        self._interpreter: Interpreter = Interpreter()

        # The default is to not run a program immediately after loading. The
        # user can change this with: %opt run_file_load t|f
        self._run_after_file_load: bool = False

    def party_like_it_is_1976(self: Driver, options: Options) -> int:
        """
        Entry point for the Tree Walking Interpreter.

        Args:
        ----
            options: The command line options.

        Returns:
        -------
            An integer with the exit code for the application as a whole.

        """
        # What options were requested?
        if options.nologo is False:
            self._logo_display()

        if options.file:
            # User wants to load a file. I'll use the built in %openfile
            # command to do the work.
            filename = ""
            if options.file[0] != '"':
                filename += '"'
            filename = options.file
            if options.file[-1] != '"':
                filename += '"'
            self._command_loadfile(filename)

        cmds_to_run: list[str] = []

        # Split up any commands the user wants to run.
        if options.commands:
            input_list = options.commands.split("^")
            cmds_to_run.extend(input_list)

        # Run the commands starting with the %of if present.
        for cmd in cmds_to_run:
            if self._execute_line(cmd) is False:
                return 0

        # The flag that keeps us running.
        continue_running: bool = True

        # Run away!
        while continue_running is True:
            prompt: str = self._build_prompt()
            cmd_to_do = read_input(prompt)
            continue_running = self._execute_line(cmd_to_do.strip())

        return 0

    ###########################################################################
    # Private Helper Methods
    ###########################################################################

    def _build_prompt(self: Driver) -> str:
        """Create a prompt showing the current context."""
        # This is what the prompt will be 99% of the time.
        prompt_str: str = Driver._DEFAULT_PROMPT

        if self._interpreter.at_breakpoint() is True:
            # What source line have we stopped on?
            curr_line: int = self._interpreter.current_line_number()
            prompt_str = f"DEBUG({curr_line}):>"

        return prompt_str

    def _execute_line(self: Driver, cmd: str) -> bool:
        """Run the Tiny BASIC or Command Language line."""
        # Make sure we have something.
        if not cmd:
            return True
        # If it's a command, execute it and if quit if the user wants.
        if cmd[0] == Driver._CMD_LANG_PREFIX:
            if self._process_command_language(cmd) == Driver.CmdResult.QUIT:
                return False
        elif self._interpreter.at_breakpoint() and cmd[0:3].lower() == "run":
            # We have one more check. If we are at a breakpoint and the user
            # entered the RUN statement, we don't want to do that because it
            # restarts the program. We want the user to use %c instead.
            print_output(
                "CLE #16: Use %c to continue from a breakpoint instead of RUN.\n",
            )
        else:
            # It's Tiny BASIC time!
            self._interpreter.interpret_line(cmd)

        return True

    def _load_program_and_run(self: Driver, program: str) -> None:
        """Load a program from a file and optionally run the program."""
        # Get the interpreter back to a clean state.
        self._interpreter.initialize_runtime_state()
        self._interpreter.clear_program()
        # Load the program and only optionally call RUN if it was a good load.
        if (self._interpreter.interpret_buffer(program) is True) and (
            self._run_after_file_load is True
        ):
            # Do the run!
            self._interpreter.interpret_line("RUN")

    ###########################################################################
    # Private Command Language Methods.
    ###########################################################################

    # The group names in the command language regular expression. I wanted to
    # use this in the regular expression string itself, but I'm scared of the
    # odd escape rules. At least I'll use them when doing the actual
    # processing.
    _CMD_GROUP: str = "cmd"
    _PARAM_GROUP: str = "param"
    _OPT_GROUP: str = "optval"

    # The regular expression that handles all of the command language. The '\b'
    # forces matching whole words. Without those, 'cont' matches 'c', which is
    # incorrect.
    _CMD_REGEX_STRING = r"""
%(?P<cmd>
   help         |  \?      |
   quit         |  \bq\b   |
   loadfile     |  \blf\b  |
   opt          |
   break        |  \bbp\b  |
   backtrace    |  \bbt\b  |
   continue     |  \bc\b   |
   delete       |  \bd\b   |
   lint         |
   savefile     |  \bsf\b  |
   step         |  \bs\b   |
   vars         |  \bv\b   |
   exit         |  \be\b
 )
\s*
(?P<param>
   log          |
   time         |
   run_on_load  |
   strict       |
   \".*\"       |
   [*]          |
   [0-9]*       |
  )?
\s*
(?P<optval>
   true         | \bt\b |
   false        | \bf\b
 )?
	"""

    _CMD_REGEX = re.compile(_CMD_REGEX_STRING, re.IGNORECASE | re.VERBOSE)

    # The circularity of the tools is weird. The Ruff warning suppression has
    # to appear at the end of the line, but that makes the line too long for
    # pylint. 🤷🏾‍♀️

    # C901: https://docs.astral.sh/ruff/rules/complex-structure/
    # PLR0912: https://docs.astral.sh/ruff/rules/too-many-branches/

    # While it would be easy to disable these complexity rules, I still think
    # they are valuable as a reminder to keep an eye on the procedure. There's
    # probably some table driven way to simplify this code, but I think that
    # would veer into the maintenance hell mode. Sometimes case statements are
    # the best way to go.

    # pylint: disable=line-too-long
    def _process_command_language(self: Driver, cmd: str) -> Driver.CmdResult:  # noqa: C901, PLR0912
        """Do the '%' commands."""
        # Pull out what the user want's to do.
        if (m := self._CMD_REGEX.match(cmd)) is None:
            self._command_language_error(
                f"CLE #01: Invalid or unknown command : '{cmd}'",
            )
            return Driver.CmdResult.CONTINUE

        match m.group(Driver._CMD_GROUP).lower():
            case "q" | "quit":
                print_output(
                    "\nThank you for using tbp! Your patronage is appreciated.\n",
                )
                return Driver.CmdResult.QUIT
            case "?":
                print_output(Driver._SHORTHELP)
            case "help":
                self._logo_display()
                print_output(Driver._FULLHELP)
            case "lint":
                self._command_lint(m.group(Driver._PARAM_GROUP))
            case "savefile" | "sf":
                self._command_savefile(m.group(Driver._PARAM_GROUP))
            case "opt":
                self._command_opt(
                    m.group(Driver._PARAM_GROUP),
                    m.group(Driver._OPT_GROUP),
                )
            case "loadfile" | "lf":
                self._command_loadfile(m.group(Driver._PARAM_GROUP))
            case "vars" | "v":
                self._command_variables()
            case "break" | "bp":
                self._command_set_breakpoint(m.group(Driver._PARAM_GROUP))
            case "delete" | "d":
                self._command_delete_breakpoint(m.group(Driver._PARAM_GROUP))
            case "continue" | "c":
                self._command_stepper(Interpreter.BreakContinueType.RUN)
            case "step" | "s":
                self._command_stepper(Interpreter.BreakContinueType.STEP)
            case "backtrace" | "bt":
                self._command_stack()
            case "exit" | "e":
                self._command_exit_debugger()
            case _:  # pragma: no cover
                pass  # pragma: no cover

        return Driver.CmdResult.CONTINUE

    def _command_exit_debugger(self: Driver) -> None:
        """Exit the debugger and returns to the tbp prompt."""
        if self._interpreter.at_breakpoint() is False:
            print_output("CLE #08: %exit command only works while debugging.\n")
        else:
            # The END statement already knows how to drop out of the debugger
            # so I can use it here to do the work.
            self._interpreter.interpret_line("END")

    def _command_stack(self: Driver) -> None:
        """Show the call stack."""
        if self._interpreter.at_breakpoint() is False:
            print_output("CLE #08: %backtrace command only works while debugging.\n")
        else:
            res: str = self._interpreter.stack_string()
            print_output(res)

    def _command_stepper(
        self: Driver,
        step_type: Interpreter.BreakContinueType,
    ) -> None:
        """Execute a single step."""
        if self._interpreter.at_breakpoint() is False:
            cmd: str = "%continue"
            if step_type == Interpreter.BreakContinueType.STEP:
                cmd = "%step"
            print_output(f"CLE #08: {cmd} command only works while debugging.\n")
            return

        self._interpreter.break_continue(step_type)

    def _command_delete_breakpoint(self: Driver, param: str) -> None:
        """Delete a single or all breakpoints."""
        if param == "*":
            self._interpreter.delete_all_breakpoints()
            return
        try:
            line_num: int = int(param)
            ret_val, error = self._interpreter.delete_breakpoint(line_num)
            if ret_val is False:
                print_output(f"{error}\n")
        except ValueError:
            print_output(
                "CLE #05: %break and %delete commands require line "
                f"numbers as parameters: '{param}'.\n",
            )

    def _command_set_breakpoint(self: Driver, param: str) -> None:
        """Set or list breakpoints."""
        # No parameter, means list them.
        if not param:
            ret_str: str = self._interpreter.list_breakpoints()
            print_output(f"{ret_str}")
            return

        try:
            # We could get a "*" (or other param value) here since that's a
            # valid value in the regex.
            line_num: int = int(param)
            ret_val, error = self._interpreter.set_breakpoint(line_num)
            if ret_val is False:
                print_output(f"{error}\n")
        except ValueError:
            print_output(
                "CLE #05: %break and %delete commands require line "
                f"numbers as parameters: '{param}'.\n",
            )

    def _command_variables(self: Driver) -> None:
        """Display the initialized variables."""
        res: str = self._interpreter.variables_string()
        print_output(res)

    def _command_lint(self: Driver, param: str) -> None:
        """Lint the program in memory."""
        strict = False
        if param.lower() == "strict":
            strict = True
        self._interpreter.lint_program(strict)

    def _command_savefile(self: Driver, filename: str) -> None:
        """Save the loaded program to a file."""
        # Is the filename empty?
        if not filename:
            self._command_language_error(
                "CLE #02: Missing required filename or missing quote delimiters "
                "for %savefile/%openfile.",
            )
            return

        # Get the program from the interpreter.
        if not (program := self._interpreter.get_program()):
            self._command_language_error(
                "CLE #03: No program in memory to save.",
            )
            return

        # The quotes are for delineation and will not make the file system
        # happy.
        filename = filename.strip('"')

        save_program(filename, program)

    def _command_loadfile(self: Driver, filename: str) -> None:
        """Load a program from disk."""
        # If we are debugging, %openfile can't be used.
        if self._interpreter.at_breakpoint() is True:
            self._command_language_error("CLE #15: %loadfile disabled while debugging.")
            return
        # Is the filename empty?
        if not filename:
            self._command_language_error(
                "CLE #02: Missing required filename or missing quote delimiters "
                "for %savefile/%loadfile.",
            )
            return
        # Before blowing away any loaded program, load the file first.
        filename = filename.strip('"')

        if program := load_program(filename):
            self._load_program_and_run(program)

    # PLR0912: https://docs.astral.sh/ruff/rules/too-many-branches/
    # C901: https://docs.astral.sh/ruff/rules/complex-structure/
    def _command_opt(self: Driver, option: str, value: str) -> None:  # noqa: C901, PLR0912
        """Change run on load and timing options."""
        if not (option := option.lower()):
            self._command_language_error("CLE #04: Required option is missing.")
            return
        if value is not None:
            value = value.lower()
        if option == "log":
            log_thing: logging.Logger = tbp_logger()
            match value:
                case "t" | "true":
                    log_thing.setLevel(logging.DEBUG)
                case "f" | "false":
                    log_thing.setLevel(logging.INFO)
                case _:
                    print_output(
                        "Option: logging is "
                        f"{log_thing.getEffectiveLevel() == logging.DEBUG!s}.\n",
                    )
        elif option == "time":
            match value:
                case "t" | "true":
                    self._interpreter.time_lines = True
                case "f" | "false":
                    self._interpreter.time_lines = False
                case _:
                    print_output(f"Option: time is {self._interpreter.time_lines!s}.\n")
        elif option == "run_on_load":
            match value:
                case "t" | "true":
                    self._run_after_file_load = True
                case "f" | "false":
                    self._run_after_file_load = False
                case _:
                    print_output(
                        f"Option: run_on_load is {self._run_after_file_load!s}.\n",
                    )

    @staticmethod
    def _command_language_error(error: str) -> None:
        print_output(f"{error} (%? for help.)\n")

    ###########################################################################
    # Sexy Output Methods
    ###########################################################################

    _LOGO: str = f"""
  Tiny BASIC in Python - https://github.com/John-Robbins/tbp
   _______ ____
  |__   __|  _ \\
     | |  | |_) |_ __
     | |  |  _ <| '_ \\
     | |  | |_) | |_) |
     |_|  |____/| .__/
                | |
                |_| version {version("tbp")}
   Party like it's 1976!
"""

    @staticmethod
    def _logo_display() -> None:
        """Show the AWESOME logo."""
        print_output(Driver._LOGO)
        len_list = len(Driver._TAGLINES)
        rnd: int = randbelow(len_list)
        tag: str = Driver._TAGLINES[rnd]
        print_output(f"   {tag}\n\n")

    # Feel free to add more events that happened in 1976.
    _TAGLINES: ClassVar[list[str]] = [
        "Look at that cool CN tower in Toronto!",
        "'Adrian! Adrian!', screams Rocky.",
        "The Space Shuttle Flies!",
        "What do I do with a $2.00 bill?",
        "We are competing with Apple here!",
        "Wow! Nadia Comaneci can sure flip and twist!",
        "Lookin' good for the Bicentennial!",
        "Let's go to the Montreal Olympics!",
        "Congrats to Southampton FC winning the FA Cup!",
        "Germany passes Mitbestimmungsgesetz.",
        "Let's go to Innsbruck, Austria for the Winter Olympics.",
        "Watch out! The Cray-1 is coming!",
        "Star Wars Episode IV started filming. May the Force be with them.",
        "The Toronto Bluejays fly into existence.",
        "Be careful of the Jovian-Plutonian gravitational effect.",
        "Congratulations Nevill Wran on the new job.",
        "Let's go fly on the Concord!",
        "Jonny Rutherford sure enjoyed that milk.",
        "There's only one basketball league now.",
        "The north lane of the Rodovia dos Imigrantes is inaugurated.",
        "Barbara Jones gave a hell of a keynote!",
        "Sagarmath National Park is born.",
        "Cruzeiero wins the Copa Libertadores de América!",
        "Vikings 1 and 2 say hello from Mars.",
        "Did you catch the Ramones at CBGB's?",
        "Congrats 'Jags' McCartney on the new job.",
        "No more tobacco advertising in Australia.",
        "The Western Roman Empire fell 1,500 years ago (to those who celebrate.)",
        "Viktor Belenko is a hero!",
        "The Brits get The Muppets!",
        "Shavarsh Karapetyan is a total hero!",
        "Welcome Seychelles to the United Nations!",
        "Stevie Wonder's 'Songs in the Key of Life' is so, so good!",
        "Congrats on the new job, Thorbjörn Fälldin!",
        "Congrats on the new job, Hua Guofeng!",
        "James Hunt wins by one point!",
        "Diffie-Hellman key exchange cryptography is invented!",
        "Congrats on the new job, Jimmy Carter!",
        "Is that a megamouth!?!?!",
        "We are competing with Microsoft here!",
        "Congrats on the new job José López Portillo!",
        "Congrats on the new job Patrick Hillery!",
        "Congrats to Samoa for joining the United Nations!",
        "King Kong returns to the screen.",
        "Is the world prepared for the Sex Pistols?",
        "¡Felicidades a España para la transición a la democracia!",
        "Just how many jumpsuits can a population wear?",
        "The last slide rule just got manufactured by Keuffel and Esser.",
        "Nagin is sure cleaning up at the box office.",
        "Amitabh Bachchan goes against type in Kabhi Kabhie.",
    ]

    _FULLHELP: str = """

A complete Tiny BASIC interpreter and debugger.
To learn more about the Tiny BASIC language, see the documentation at
https://john-robbins.github.io/tbp/tb-language

To learn more about Tiny BASIC in Python, see the extensive documentation at
https://john-robbins.github.io/tbp/

Command Line Options
--------------------
-h | --help
    - Shows the command line option help and exits.
-c | --commands "command^command^command"
    - Executes the commands as though they were typed in by the user.
    - Use the carat character (^) to separate statements.
- nologo
    - Doesn't show the awesome logo. :(

At the tbp prompt, you can enter both Tiny BASIC code and direct execution
statements, such as RUN. For the debugger and tbp state information, use the
command language, which are commands that start with the '%' character and are
case-insensitive.

Information and State Commands
------------------------------
%help
    - This full help information.
%?
    - Short help of just the command language.
%quit | %q
    - Quit tbp.
%lint (strict)
    - Lint the program in memory for possible errors.
    - The strict option does more uninitialized checking.
%loadfile | %lf  "<filename>"
    - Clears all programs, the GOSUB stack, RUN input variables, from memory.
    - The quotes around the filename are required.
    - All Tiny BASIC statements, direct execution statements, and any command
      language statements in "<filename>" are executed as though they were
      typed in by the user.
    - If run_on_load is True, after loading and parsing the file, tbp will
      execute a RUN direct execution statement.
    - Disabled when debugging.
%savefile | %sf "<filename>"
    - Saves the currently loaded program to "<filename>".
    - The quotes around the filename are required.
%opt log | run_on_load | time (true | t | false | f)
    - Set or view the option setting. For all, true is on, false is off. No
      parameter shows the current state of the option.
    - %opt log
       - Controls if tbp internal diagnostic logging is shown.
    - %opt run_on_load
      - Controls if tbp does a direct execution RUN after loading a file.
    - %opt time
      - Controls if tbp displays the execution time of each line.

Debugging Commands
------------------
%bp | %break linenumber
     - Sets a breakpoint on the linenumber. No params lists breakpoints.
%d  | %delete linenumber | *
     - Deletes a breakpoint on linenumber or all with *.
%c  | continue
     - Continues execution after stopping at a breakpoint.
%s  | %step
     - Steps the next line, stepping into any GOTO or GOSUB statements.
%v  | %vars
     - Displays all the initialized variables.
%bt | %backtrace
     - Display the call stack.
%e  | %exit
     - Exit the debugger and return to tbp prompt.
"""

    _SHORTHELP: str = """
Information and State Commands
------------------------------
%help
    - Full help information.
%?
    - This help for the command language.
%quit | %q
    - Quit tbp.
%lint (strict)
    - Lint the program in memory for possible errors.
%loadfile | %of  "<filename>"
    - Clears everything and loads a file.
%savefile | %sf "<filename>"
    - Saves the loaded program to a file.
%opt (log | run_on_load | time) (true | t | false | f)
    - Set or view the option setting.

Debugging Commands
------------------
%bp | %break linenumber
     - Sets a breakpoint on the linenumber. No params lists breakpoints.
%d  | %delete linenumber | *
     - Deletes a breakpoint on linenumber or all with *.
%c  | continue
     - Continues execution after stopping at a breakpoint.
%s  | %step
     - Steps the next line, stepping into any GOTO or GOSUB statements.
%v  | %vars
     - Displays all the initialized variables.
%bt | %backtrace
     - Display the call stack.
%e  | %exit
     - Exit the debugger and return to tbp prompt.
"""
