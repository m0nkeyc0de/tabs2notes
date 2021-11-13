"""
Tablature parsing
As there is not standardized format, it's going to break at some point...
"""
import os
import re
import collections

RE_INT = r"[0-9]+"

# Tablature line guesswork
TAB_CHAR = '-'
TAB_CHAR_MIN_OCCURENCE = 5

# MIDI values of base strings
BASS_STRINGS = (28, 33, 38, 43)
GUITAR_STRINGS = (40, 45, 50, 55, 59, 64)

# Dict keys
K_FR_IDX = 'frets_indexes'
K_FR_DET = 'frets_detail'

class Tablature():
    """Guitar tablature parsing"""

    def __init__(self, file_name):
        """Constructor"""
        self.file = [] # File content line by line
        self.file_name = file_name # File name

        # Tablature structure
        self.strings_count = 0 # how many strings in the tablature ?
        self.strings_base_notes = [] # base midi notes of the instruments strings
        self.extracted_frets = [] # notes written on the tablature

    def load_file(self,):
        """Load file content"""
        if not os.path.exists(self.file_name):
            raise ValueError(f"Tablature file '{self.file_name}' doest not exist !")

        with open(self.file_name, 'r') as f:
            self.file = f.readlines()

    def parse(self,):
        """Get tablature string count and check consitency"""

        current_line = 0

        # Variables for strings counting
        last_string_count = 0
        cur_string = 0
        last_line_was_string = False

        # Frets positions in the group
        group_frets = {}

        for line in self.file:
            current_line += 1
            line = line.strip() # cleaning

            if Tablature.line_is_string(line): # tablature line found
                if last_line_was_string: # same line group
                    cur_string += 1

                else: # new line group
                    cur_string = 1

                    # We store positions of notes in the whole group and every single note
                    # of each line. Then we create a list of tuples with the concurrent notes
                    group_frets = {
                        K_FR_IDX : set(), # where are the notes in the string group ?
                        K_FR_DET : collections.OrderedDict(), # which frets are pressed ?
                    }

                last_line_was_string = True

                # Extract notes from line
                group_frets[K_FR_DET][cur_string] = Tablature.get_line_frets(line)
                for note_idx in group_frets[K_FR_DET][cur_string]:
                    group_frets[K_FR_IDX].add(note_idx)

            else:
                if last_line_was_string: # end of line group

                    if last_string_count > 0: # it's at least the 2nd group
                        if last_string_count != cur_string: # problem
                            raise self.InconsistentTablature(f"Inconsistent string count in file (line {current_line})")

                        else: # everything's fine
                            last_string_count = cur_string

                    else: # first group
                        last_string_count = cur_string
                    
                    last_line_was_string = False
                    self.extracted_frets.append(group_frets)
                    group_frets = {}

        # Ensure last group is there
        if group_frets:
            self.extracted_frets.append(group_frets)

        # Store how many strings the instrument has
        self.strings_count = cur_string

    def midi_notes(self,):
        """Convert frets list into midi notes"""
        retval = []

        # Determine strings base notes
        # TODO use the note name at beginning of tablature line if available
        if self.strings_count == 4:
            self.strings_base_notes = list(BASS_STRINGS)

        elif self.strings_count == 6:
            self.strings_base_notes = list(GUITAR_STRINGS)

        else:
            raise self.InstrumentGuessworkFailed(f"Unable to do instrument guesswork with {self.strings_base_notes} strings")

        # Put notes in same order as tablature lines
        self.strings_base_notes.reverse()

        # Extract the real notes from frets positions
        for fret_group in self.extracted_frets:
            # All the notes of the current group
            group_midi_notes = []

            for note_idx in fret_group[K_FR_IDX]:
                # All the notes at this position in the current group
                line_midi_notes = []
                
                for string_idx in range(1, self.strings_count+1):
                    string_base_note = self.strings_base_notes[string_idx-1]

                    # Do we have a note at this position in the current line ?
                    fret = fret_group[K_FR_DET][string_idx].get(note_idx)

                    if fret: # There is a fret pressed at this position on this line                    
                        midi_note = string_base_note + fret
                        line_midi_notes.append(midi_note)

                group_midi_notes.append(line_midi_notes)

            retval.append(group_midi_notes)

        return retval

    # Helpers
    @staticmethod
    def line_is_string(line):
        """Determines if current line is a string"""
        # TODO make it less guesswork
        return line.count(TAB_CHAR) > TAB_CHAR_MIN_OCCURENCE

    class InconsistentTablature(Exception):
        """Inconsistent tablature"""
    
    class InstrumentGuessworkFailed(Exception):
        """Unable to find instrument"""

    @staticmethod
    def get_line_frets(line):
        """Extract frets from line"""
        frets = collections.OrderedDict()

        for match in re.finditer(RE_INT, line):
            note_idx = match.start()
            fret = match.group()

            # WORKAROUND when a fret is like 7777777777777
            if fret.count(fret[0]) == len(fret):
                fret = fret[0]
            
            frets[note_idx] = int(fret)
        
        return frets