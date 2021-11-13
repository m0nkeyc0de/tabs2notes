#!/usr/bin/env python
import argparse
from src.tablature import Tablature
from src.notes import MusicNote

NOTE_ENGLISH = 'english'
NOTE_LATIN = 'latin'
NOTE_GERMAN = 'german'

def init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] [FILE]",
        description="Try to read a guitar tablature and print note names",
    )
    parser.add_argument(
        "--transpose", 
        help="Transpose notes by given half-tone offset",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--naming",
        help="Note naming style",
        default=NOTE_LATIN,
        choices=[
            NOTE_LATIN,
            NOTE_ENGLISH,
            NOTE_GERMAN,
        ]
    )
    parser.add_argument('file', nargs=1)
    return parser

def main():
    parser = init_argparse()
    args = parser.parse_args()

    tab_file = args.file[0]
    transposistion = args.transpose
    note_naming = {
        NOTE_ENGLISH: MusicNote.ENGLISH,
        NOTE_LATIN: MusicNote.LATIN,
        NOTE_GERMAN: MusicNote.GERMAN,
    }.get(args.naming)

    tab = Tablature(tab_file)
    tab.load_file()
    tab.parse()
    midi_notes = tab.midi_notes()

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

        # TODO there are some extra-spaces but don't know why
        print(" ".join(line_notes))

if __name__ == "__main__":
    main()
