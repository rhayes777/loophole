import unittest
import music


class KeySelectionTestCase(unittest.TestCase):
    def test_keys_array(self):
        self.assertTrue(music.Key.C in music.keys_array[0])
        self.assertTrue(music.Key.C not in music.keys_array[1])

    def test_positions(self):
        self.assertTrue(0 in music.Scale.all_positions(music.Scale.major, music.Key.C))
        self.assertTrue(1 not in music.Scale.all_positions(music.Scale.major, music.Key.C))
        self.assertTrue(1 in music.Scale.all_positions(music.Scale.major, music.Key.C_Sharp))


if __name__ == "__main__":
    unittest.main()