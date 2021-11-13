"""
Notes tests
"""
import unittest
import re

from src.notes import (
    MusicNote,
    IDX_ENG,
    IDX_DEU,
    IDX_LAT,
)

class MusicNoteTest(unittest.TestCase):
    """Is our MusicNote class working fine ?"""
    def test_validate_midi_index(self):
        """MIDI index"""
        # MIDI indexes are from 0 to 127
        with self.assertRaises(TypeError):
            MusicNote.validate_midi_index('bla')
        with self.assertRaises(ValueError):
            MusicNote.validate_midi_index(-1)
        with self.assertRaises(ValueError):
            MusicNote.validate_midi_index(128)

        MusicNote.validate_midi_index(0)
        MusicNote.validate_midi_index(127)
        MusicNote.validate_midi_index(50)

    def test_validate_lang(self,):
        """Language index"""
        with self.assertRaises(TypeError):
            MusicNote.validate_lang('bla')
        with self.assertRaises(ValueError):
            MusicNote.validate_lang(1000)
        
        MusicNote.validate_lang(IDX_ENG)
        MusicNote.validate_lang(IDX_DEU)
        MusicNote.validate_lang(IDX_LAT)

    def test_validate_note_name(self,):
        """Note name"""
        with self.assertRaises(TypeError):
            MusicNote.validate_name(9)

        # Crap that must fail
        for crap in ['bla', 'Sol', 'G' , 'g1', 'G1#', 'Z8', 'B-1']:
            with self.assertRaises(ValueError):
                MusicNote.validate_name(crap)

        # English notes
        for note in ['A1','B2','C3','Db3', 'E10', 'F0', 'G#2', 'B0']:
            MusicNote.validate_name(note)

        # German notes
        for note in ['A1','H2','C3','Des3', 'E10', 'F0', 'Gis2', 'H0']:
            MusicNote.validate_name(note)

        # Latin notes
        for note in ['La1','Si2','Do3','Reb3', 'Mi10', 'Fa0', 'Sol#2', 'Si0']:
            MusicNote.validate_name(note)

    def test_midi_index_to_name(self,):
        """Test midi index to name"""
        with self.assertRaises(TypeError):
            MusicNote.midi_to_name('bla')
        
        # MIDI is from 0 to 127
        for idx in [-1, 128]:
            with self.assertRaises(ValueError):
                MusicNote.midi_to_name(idx)
        
        # index, language, name
        test_data = (
            # First note
            (0, IDX_ENG, 'C0'),
            (0, IDX_DEU, 'C0'),
            (0, IDX_LAT, 'Do0'),
            # Last note
            (127, IDX_ENG, 'G10'),
            (127, IDX_DEU, 'G10'),
            (127, IDX_LAT, 'Sol10'),
            # Octaves
            (12, IDX_ENG, 'C1'),
            (24, IDX_ENG, 'C2'),
            (36, IDX_ENG, 'C3'),
            (48, IDX_ENG, 'C4'),
            (60, IDX_ENG, 'C5'),
            (72, IDX_ENG, 'C6'),
            (84, IDX_ENG, 'C7'),
            (96, IDX_ENG, 'C8'),
            (108, IDX_ENG, 'C9'),
            (120, IDX_ENG, 'C10'),
        )
        for midi_idx, lang_idx, name in test_data:
            self.assertEqual(name, MusicNote.midi_to_name(midi_idx, lang_idx))

    def test_name_to_midi(self,):
        """Note name to MIDI"""
        with self.assertRaises(TypeError):
            MusicNote.name_to_midi(8)
        
        # MIDI minumum is C0 and maximum is G10
        for crap in ['bla', 'Sol', 'G#10', 'F11']:
            with self.assertRaises(ValueError):
                MusicNote.name_to_midi(crap)

        # Name, midi index
        test_data = (
            # English
            ('C0', 0),
            ('G10', 127),
            # German
            ('H0', 11),
            ('H8', 107),
            # Latin
            ('Do0', 0),
            ('Re#4', 51),
        )
        for name, midi_idx in test_data:
            self.assertEqual(midi_idx, MusicNote.name_to_midi(name))

if __name__ == '__main__':
    unittest.main()