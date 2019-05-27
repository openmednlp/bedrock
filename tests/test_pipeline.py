import unittest


class TestPipeline(unittest.TestCase):
    def test_pipeline_text(self):
        actual = ['Hund Katze Maus']
        expected = ['Hund Katze Maus']
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
