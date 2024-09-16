"""All I want is the number of tests pytest ran."""  # noqa: INP001

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

# Run pytest with the '--junit-xml=.test-results.xml' command line option to
# create the XML file. Yes, I should be some cool XML stuff here, but I just
# want a single number.
#
# To execute this script:
# python ./tools/num_pytest_tests.py .test-results.xml
from __future__ import annotations

import re
import sys
from pathlib import Path

if len(sys.argv) == 1:
    print("Error: missing required pytest xml file.")
    sys.exit(1)

PATTERN = r'tests="(?P<tests>\d+?)"'

# The information I want is in the first 202 bytes of the file so I'll read
# just that much so I don't have to drag in a potentially large file.
with Path(sys.argv[1]).open(encoding="utf-8") as f:
    raw_data = f.read(202)

if matches := re.search(PATTERN, raw_data):
    print(matches.group("tests"))
    sys.exit(0)
else:
    print("0")
    sys.exit(2)
