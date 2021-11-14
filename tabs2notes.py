#!/usr/bin/env python
import argparse
from src.tablature import Tablature
from src.notes import MusicNote

# Notes naming
NOTE_ENGLISH = 'english'
NOTE_LATIN = 'latin'
NOTE_GERMAN = 'german'

NOTE_CHOICES = [
    NOTE_LATIN,
    NOTE_ENGLISH,
    NOTE_GERMAN,
]

# Instrument
INST_GUITAR6 = 'guitar6'
INST_BASS4 = 'bass4'

INST_CHOICES = [
    INST_BASS4,
    INST_GUITAR6,
]

def init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] [FILE]",
        description="Convert a tablature to note names",
    )
    parser.add_argument(
        "-t", "--transpose", 
        help="Transposition option for instruments in other tonalities by given half-tone offset",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-n", "--naming",
        help="Language in which notes will be displayed",
        default=NOTE_LATIN,
        choices=NOTE_CHOICES,
    )
    parser.add_argument(
        "-i", "--instrument",
        help="Instrument the tablature is written for",
        default=INST_BASS4,
        choices=INST_CHOICES,
    )
    parser.add_argument(
        "-d", "--debug",
        help="At some point things will go wrong...",
        default=0,
        type=int,
        choices=range(0,5),
    )
    parser.add_argument('file', nargs=1)
    return parser

def main():
    """The main program"""
    # Inputs
    parser = init_argparse()
    args = parser.parse_args()

    tab_file = args.file[0]
    transposistion = args.transpose

    note_naming = {
        NOTE_ENGLISH: MusicNote.ENGLISH,
        NOTE_LATIN: MusicNote.LATIN,
        NOTE_GERMAN: MusicNote.GERMAN,
    }.get(args.naming)

    inst_strings = {
        INST_GUITAR6: Tablature.INST_GUITAR6,
        INST_BASS4: Tablature.INST_BASS4,
    }.get(args.instrument)
    debug = args.debug

    # Compute
    tab = None
    try:
        tab = Tablature(tab_file, inst_strings, debug=debug)
    except (Tablature.InstrumentBadStringCount, Tablature.InconsistentTablature) as exc:
        print(exc)
        exit(1)

    midi_notes = tab.midi_notes()

    # Output
    for line in midi_notes:
        line_notes = []

        for chords in line:
            chord_notes = []

            for note in chords:
                note += transposistion
                note_name = MusicNote.midi_to_name(note, note_naming)
                chord_notes.append(note_name)

            # TODO this way of displaying chords isn't readable
            line_notes.append("+".join(chord_notes))
            
        print(" ".join(line_notes))

if __name__ == "__main__":
    main()
