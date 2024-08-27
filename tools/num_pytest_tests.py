"""All I want is the number of tests pytest ran."""  # noqa: INP001

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2004 John Robbins
###############################################################################

# This is the absolutely dumbest reason I've ever written code. Ye ol' pytest
# does not make it simple to get something as simple as the number of tests
# run.
#
# Run pytest with the '--junit-xml=.test-results.xml' command line option to
# create the XML file. Yes, I should be some cool XML crap here, but I just
# want a single number.
#
# To execute this script:
# python ./tools/num_pytest_tests.py .test-results.xml
from __future__ import annotations

import re
import sys
from pathlib import Path

if len(sys.argv) == 0:
    print("Error: missing required pytest xml file.")
    sys.exit(1)

PATTERN = r'tests="(\d+)"'

# Yeah, drag the whole thing into memory.
raw_data = Path(sys.argv[1]).read_text(encoding="utf-8")

if matches := re.search(PATTERN, raw_data):
    print(matches.group(1))
    sys.exit(0)
else:
    print(f"No tests= found in {sys.argv[1]}")
    sys.exit(2)
