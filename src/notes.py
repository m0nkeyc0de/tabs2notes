"""
Here we handle notes
"""
import re

# Global definitions
MIDI_NOTES_COUNT = 128
SCALE_SIZE = 12

# MIDI notes names is a mess, with negative (!) octave numbers but id depends...
# Middle C (~264Hz) is always note 60 --> C5 in our setup
# https://www.midi.org/forum/830-midi-octave-and-note-numbering-standard

RE_NOTE_ENG = r"^[A-G][b#]?(10|[0-9])$" # English
RE_NOTE_DEU = r"^(A|H|[C-G])(is|es)?(10|[0-9])$" # German
RE_NOTE_LAT = r"^(Do|Re|Mi|Fa|Sol|La|Si)[b#]?(10|[0-9])$" # Latin

# Integer regex
RE_INT = r"[0-9]+"

# Notes sequence of a scale, with international support (just for fun)
# Indexes of languages in the sequence
IDX_ENG = 0
IDX_DEU = 1
IDX_LAT = 2

NOTES_SEQUENCE = (
    ('C', 'C', 'Do', ),
    ('C#', 'Cis', 'Do#', ),
    ('D', 'D', 'Re', ),
    ('D#', 'Dis', 'Re#', ),
    ('E', 'E', 'Mi', ),
    ('F', 'F', 'Fa', ),
    ('F#', 'Fis', 'Fa#', ),
    ('G', 'G', 'Sol', ),
    ('G#', 'Gis', 'Sol#', ),
    ('A', 'A', 'La', ),
    ('A#', 'Ais', 'La#', ),
    ('B', 'H', 'Si', ),
)

# Map language index with corresponding regex
NOTES_LANGUAGES = (
    (IDX_ENG, RE_NOTE_ENG),
    (IDX_DEU, RE_NOTE_DEU),
    (IDX_LAT, RE_NOTE_LAT),
)

class MusicNote():
    """All the notes stuff is in there"""
    ENGLISH = IDX_ENG
    GERMAN = IDX_DEU
    LATIN = IDX_LAT
    
    # Helpers
    @staticmethod
    def midi_to_name(midi_idx, lang_idx=IDX_ENG):
        """Get note name from midi index"""
        MusicNote.validate_midi_index(midi_idx)
        MusicNote.validate_lang(lang_idx)
        note_idx = midi_idx % SCALE_SIZE
        note_octave = midi_idx // SCALE_SIZE
        return f"{NOTES_SEQUENCE[note_idx][lang_idx]}{note_octave}"

    @staticmethod
    def name_to_midi(note_name):
        """Get the MIDI index from a note"""
        MusicNote.validate_name(note_name)

        # Find the matching language
        for lang_idx, lang_re in NOTES_LANGUAGES:
            if re.match(lang_re, note_name):
                # Extract octave number and raw note name
                note_octave = int(re.findall(RE_INT, note_name)[0])
                raw_note = re.sub(RE_INT, '', note_name)
                
                # Get note position in the scale
                note_idx = 0
                for entry in NOTES_SEQUENCE:
                    if entry[lang_idx] == raw_note:
                        midi_idx = note_octave * SCALE_SIZE + note_idx
                        # Check it's valid
                        try:
                            MusicNote.validate_midi_index(midi_idx)
                        except ValueError:
                            raise ValueError(f"{note_name} is not in MIDI range")
                        else:
                            return midi_idx
                    
                    note_idx +=1

                # If we arrive here, something is wrong in the NOTE_SEQUENCE
                raise RuntimeError(f"Note '{raw_note}' not found in NOTE_SEQUENCE with lang_idx '{lang_idx}'")

        # If we arrive here note wasn't matched to any language
        # The validate_name function should be avoiding this scenario
        raise RuntimeError(f"Note '{note_name}' couldn't be matched to a language.")


    # Validators
    @staticmethod
    def validate_name(note_name):
        """Is this a correct note name ?"""
        if not isinstance(note_name, str):
            raise TypeError("Note name must be a string")

        for lang_idx, lang_re in NOTES_LANGUAGES:
            if re.match(lang_re, note_name):
                return # It matches to known note, we're fine
        
        raise ValueError(f"Invalid note name '{note_name}'")


    @staticmethod
    def validate_midi_index(idx):
        """Validate that index value is correct"""
        if not isinstance(idx, int):
            raise TypeError("Note index must be an int")
        
        if idx < 0 or idx >= MIDI_NOTES_COUNT:
            raise ValueError(f"Invalid note MIDI index '{idx}'. Must be from 0 to {MIDI_NOTES_COUNT-1}")
    
    @staticmethod
    def validate_lang(lang_idx):
        """Ensure we're using a defined language index"""
        if not isinstance(lang_idx, int):
            raise TypeError("Language index must be an int")

        for index, _ in NOTES_LANGUAGES:
            if index == lang_idx:
                return 

        raise ValueError(f"Language '{lang_idx}' is not defined")

