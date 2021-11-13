"""
Tablatures aren't standardized...
This stuff is going to break for sure at some point, and fixing it without 
regressions is going to be challenging
"""
import unittest
from src.tablature import Tablature

class TablatureTest(unittest.TestCase):
    """Tablature testing"""
    
    def test_line_is_string(self,):
        """Guesswork to find tablature lines"""
        tablature_lines = [
            "g-------------------------------------------------------------------------------------",
            "a------4-5-7----7-5-4-5-4-2-0-----7-4---4-5-7-4-----------2-4-5-4---4---4-5-7---------",
            "A|-----------------------------------------------------8\-|"
        ]
        for line in tablature_lines:
            self.assertTrue(Tablature.line_is_string(line))

        random_lines = [
            "",
            "bla bla bla",
            "add-some-dashes",
        ]
        for line in random_lines:
            self.assertFalse(Tablature.line_is_string(line))

    def test_line_frets(self,):
        """Test line frets extraction"""
        frets = Tablature.get_line_frets("g---6-7-9-16--14-13--777777--")
        self.assertEqual(7, len(frets))
        # (char pos, value)
        self.assertEqual(6, frets[4])
        self.assertEqual(7, frets[6])
        self.assertEqual(9, frets[8])
        self.assertEqual(16, frets[10])
        self.assertEqual(14, frets[14])
        self.assertEqual(13, frets[17])
        # Multiple times same number must not be repeated
        self.assertEqual(7, frets[21]) # 777777

    def test_broken_tablatures(self,):
        """Weird tablatures stuff"""

        tab = Tablature("tests/inconsistent_tablature.txt")
        tab.load_file()
        with self.assertRaises(Tablature.InconsistentTablature):
            tab.parse()

        tab = Tablature("tests/failed_instrument_guesswork.txt")
        tab.load_file()
        tab.parse()
        with self.assertRaises(Tablature.InstrumentGuessworkFailed):
            tab.midi_notes()
            
    def test_tab_style_01(self):
        """Tablature style 01"""
        tab = Tablature("tests/tab_style1.txt")
        tab.load_file()
        tab.parse()

        # It's a bass tab
        self.assertEqual(4, tab.strings_count)

        # There are 3 tab lines groups
        self.assertEqual(3, len(tab.extracted_frets))

        