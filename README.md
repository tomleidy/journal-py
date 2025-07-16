# Journal-py

## Overview

A command line tool to prepare a journaling template with the goal of writing 750 words per day (a la the _The Artist's Way_ by Julia Cameron) as a wrapper for iA Writer (macOS)

## Features

- Title (YYYYMMDD Weekday the nth of Month) / filename generation (title.txt), timestamping the entry start
- Word counting the template in a way that approximates iA Writer for macOS word counting
- Calculating and inserting the word count goal
- Time based journaling:
  - if you run the script at 6pm or later after already having done an entry for the day, it will setup #EveningPages with another 750 words.
  - if you haven't done an entry for the day and run the script, it will still call it #MorningPages. Additionally, it will let you do this up to 2am the following morning (because some days are like that).
- Options:
  - Pull a daily random tarot card from personal/tarot.csv for contemplation (see examples/tarot.csv for format example)
  - Pull questions/writing prompts from personal/questions-\*.txt (specifically: daily, weekly, and monthy)
  - Get question from Stoicism prompt, store progress (inspired by Ryan Holiday's _The Daily Stoic Journal_)
  - Gather current astrological information
- Command line argument parsing using argparse

## Installation

`python3 main.py`

Or, consider adding the following to your shell initialization, after adjusting the path to the script:

`alias journal='sh ~/scripts/journal/journal.sh'`

## Usage

run `journal.sh` with command line arguments you desire (if any) or, if you added the journal alias, use `journal`.

### Command-line Arguments

Please see `journal --help` for current command line arguments and explanations.

### Examples

## Dependencies

This should currently mostly run without any packages installed. Astrological functions required ephem.

`python -m venv venv`
`. venv/bin/activate`
`pip3 install -r requirements.txt`

## Development

Currently, the astrological function is inaccurate and is non-essential to the most important functions of the script. This will be fixed eventually.

I do not currently have a Windows machine anymore, so the Windows functionality, if it still exists, is greatly diminished.

## License

MPL 2.0 https://www.mozilla.org/en-US/MPL/2.0/
