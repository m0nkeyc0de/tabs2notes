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

# Dict keys
K_FR_IDX = 'frets_indexes'
K_FR_DET = 'frets_detail'
K_FR_BLK = 'frets_block_idx'

class Tablature():
    """Guitar tablature parsing"""

    # MIDI values of instrument strings (low to high)
    INST_BASS4 = (28, 33, 38, 43)
    INST_GUITAR6 = (40, 45, 50, 55, 59, 64)

    # Debug levels values
    DEBUG_OFF = 0
    DEBUG_NOTES = 1 # notes parsing
    DEBUG_STRUCTURE = 2 # structure parsing
    DEBUG_DETAILED = 3 # detailed 
    DEBUG_HARDCORE = 4 # everything !

    def __init__(self, file_name, inst_strings, debug=DEBUG_OFF):
        """Constructor"""
        self.file = [] # File content line by line
        self.file_name = file_name # File name
        self.strings_base_notes = inst_strings # base midi notes of the instruments strings
        self.debug = debug

        self._debug(f"__init__({file_name}, {inst_strings}, {debug})", self.DEBUG_HARDCORE)

        # Tablature structure
        self.strings_count = 0 # how many strings in the tablature
        self.strings_blocks = [] # string blocks start lines indexes (not numbers)
        self.extracted_frets = [] # notes written on the tablature

        # Analyze the file
        self._load_file()
        self._parse_file()
        self._extract_frets()

    def _load_file(self,):
        """Load file content"""
        self._debug("_load_file()", self.DEBUG_DETAILED)
        if not os.path.exists(self.file_name):
            raise ValueError(f"Tablature file '{self.file_name}' doest not exist !")

        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                self.file.append(line)

    def _parse_file(self,):
        self._debug("_parse_file()", self.DEBUG_DETAILED)
        """Parse tablature
        - Check each block has same count of strings
        - Check that strings count matches to instrument
        - Document block starts
        """
        cur_str_cnt = 0
        lst_str_cnt = 0
        lst_was_str = False

        cur_grp_start = 0

        for line_idx, file_line in enumerate(self.file):
            line_no = line_idx + 1
            self._debug(f"Line {line_no} '{file_line}'", self.DEBUG_STRUCTURE)
            self._debug(
                f"A: cur_str_cnt={cur_str_cnt} lst_str_cnt={lst_str_cnt} lst_was_str={lst_was_str}", 
                self.DEBUG_HARDCORE,
            )

            if Tablature.is_tablature_line(file_line):
                self._debug("-> tablature line", self.DEBUG_STRUCTURE)
                cur_str_cnt = (cur_str_cnt + 1) if lst_was_str else 1
                cur_grp_start = cur_grp_start if lst_was_str else line_idx
                lst_was_str = True

            elif lst_was_str: # end of line group
                self._debug("-> line after tablature block", self.DEBUG_STRUCTURE)

                # Store lines group start
                self.strings_blocks.append(cur_grp_start)
                self._debug(f"-> group start added for line index {cur_grp_start}", self.DEBUG_DETAILED)

                # Check that each block has as much strings as the previous one
                if lst_str_cnt and lst_str_cnt != cur_str_cnt:
                    raise self.InconsistentTablature(f"Inconsistent string count in file (line {line_no})")

                # Loop reset
                lst_str_cnt = cur_str_cnt
                lst_was_str = False
            
            else:
                self._debug("-> other line", self.DEBUG_STRUCTURE)
            
            self._debug(
                f"B: cur_str_cnt={cur_str_cnt} lst_str_cnt={lst_str_cnt} lst_was_str={lst_was_str}",
                self.DEBUG_HARDCORE,
            )

        # Group start for last group
        self.strings_blocks.append(cur_grp_start)
        self._debug(f"-> group start added for line index {cur_grp_start} (outside loop)", self.DEBUG_DETAILED)
        self._debug(f"Discovered strings blocks start indexes : {self.strings_blocks}", self.DEBUG_STRUCTURE)

        # Store how many strings the instrument has
        self.strings_count = lst_str_cnt

        # Check that the chosen instrument matches
        instr_strings = len(self.strings_base_notes)
        if instr_strings != self.strings_count:
            raise self.InstrumentBadStringCount(f"Wrong instrument ({instr_strings} strings instead of {self.strings_count})")
    
    def _extract_frets(self,):
        """Extract frets data based"""
        self._debug("_extract_frets()", self.DEBUG_DETAILED)

        for block_start_idx in self.strings_blocks:
            block_end_idx = block_start_idx + self.strings_count

            block_frets = {
                K_FR_IDX : set(), # Fret indexes for all group lines
                K_FR_DET : collections.OrderedDict(), # Fret indexes per line
                K_FR_BLK : block_start_idx,
            }

            for str_idx, file_line in enumerate(self.file[block_start_idx:block_end_idx]):
                str_no = str_idx + 1
                self._debug(f"String {str_no} '{file_line}'", self.DEBUG_NOTES)
                frets = Tablature.get_line_frets(file_line)
                self._debug(f"-> frets : {frets}", self.DEBUG_NOTES)

                block_frets[K_FR_DET][str_no] = frets

                # Document all pressed frets indexes from the block
                for note_idx in block_frets[K_FR_DET][str_no]:
                    block_frets[K_FR_IDX].add(note_idx)
            
            self.extracted_frets.append(block_frets)

            self._debug(f"Block {block_start_idx} frets: {block_frets[K_FR_IDX]}", self.DEBUG_NOTES)

    def midi_notes(self,):
        """Convert frets list into midi notes"""
        self._debug("_midi_notes()", self.DEBUG_DETAILED)
        retval = []

        # Put notes in same order as tablature lines
        strings_notes = list(self.strings_base_notes)
        strings_notes.reverse()

        self._debug(f"Base strings MIDI notes: {strings_notes}", self.DEBUG_NOTES)

        # Extract the real notes from frets positions
        for block_frets in self.extracted_frets:
            # All the notes of the current group
            block_midi_notes = []

            block_start_idx = block_frets[K_FR_BLK]

            for note_idx in sorted(list(block_frets[K_FR_IDX])):
                # All the notes at this position in the current group
                string_midi_notes = []
                
                for string_idx in range(1, self.strings_count+1):
                    string_base_note = strings_notes[string_idx-1]

                    # Do we have a note at this position in the current line ?
                    fret = block_frets[K_FR_DET][string_idx].get(note_idx)

                     # There is a fret pressed at this position on this line
                    if fret is not None: # fret can be 0 !    
                        midi_note = string_base_note + fret
                        string_midi_notes.append(midi_note)

                block_midi_notes.append(string_midi_notes)

            self._debug(f"Block {block_start_idx} MIDI notes: {block_midi_notes}", self.DEBUG_NOTES)
            retval.append(block_midi_notes)

        return retval

    # Static methods
    @staticmethod
    def is_tablature_line(line):
        """Determines if current line is a string"""
        # TODO make it less guesswork
        return line.count(TAB_CHAR) > TAB_CHAR_MIN_OCCURENCE

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

    # Debugging output
    def _debug(self, message, level=1):
        """Print debug message if debug enabled"""
        if self.debug >= level:
            print(f"DEBUG: {message}")

    # Exceptions
    class InconsistentTablature(Exception):
        """Inconsistent tablature"""

    class InstrumentBadStringCount(Exception):
        """Wrong instrument chosen"""
