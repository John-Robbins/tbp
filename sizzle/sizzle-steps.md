# Recording the Sizzle GIF for the README

## Install the Tools

- asciinema: [https://docs.asciinema.org](https://docs.asciinema.org).
- agg: [https://github.com/asciinema/agg](https://github.com/asciinema/agg)
- iterm2: [https://iterm2.com](https://iterm2.com)

## Note

- Do everything in iterm2 so that the block cursor shows up, which makes the typing much easier to see in the final GOF.

## Copy the Demo Script

- Copy tbp-sizzle-script.txt to ~/Library/Application Support/iTerm2/Scripts
- Change the .txt extension to .py.
- Verify the script shows up on the iterm2→Script menu.

## Preparation

- Ensure tbp is installed and ready to rock, i.e, run `make`.
- Start iterm2.
- Change to the tbp directory (in my case ~/Code/tbp).

## Recording

- In iterm2
  - I guess it's impossible to disable oh-my-zsh prompt temporarily. It's a virus.
  - Execute this:
    - `asciinema rec --title="tbp Sizzle" --cols=80 --rows=25 --overwrite ./misc/tbp-sizzle.cast`
  - Select iterm2→Scripts→tbp-sizzle-script.py to run the script.
  - When finished, `CTRL+D` to stop recording.

## Processing

- Edit `tbp-sizzle.cast` to remove the escape sequences and make the prompt `%>`
- In the initial play, show Sassy winning.
- In the change variable part, ensure Sassy's pick is `C=1` to show the cheating!

## Post Processing

- `~/Downloads/agg-x86_64-apple-darwin tbp-sizzle.cast tbp-sizzle.gif`
- Upload to [https://ezgif.com/](https://ezgif.com/) and optimize with Lossy GIT at 100.
