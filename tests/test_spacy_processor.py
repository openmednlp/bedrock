import unittest
from bedrock.processors.SpacyProcessor import SpacyProcessor


class TestLemmatize(unittest.TestCase):
    def test_lematize_text(self):
        p = SpacyProcessor()
        actual = p.lemmatize('Hunden Katzen Mäuse')
        expected = ['Hund Katze Maus']
        self.assertEqual(expected, actual)

    def test_lemmatize_text_as_list(self):
        p = SpacyProcessor()
        actual = p.lemmatize(['Hunden Katzen Mäuse'])
        expected = ['Hund Katze Maus']
        self.assertEqual(expected, actual)

    def test_lematize_texts(self):
        p = SpacyProcessor()
        actual = p.lemmatize(
            [
                'Hunden Katzen Mäuse',
                'Mädels Männer Frauen']
        )
        expected = [
            'Hund Katze Maus',
            'Mädel Mann Frau'
        ]
        self.assertEqual(expected, actual)


class TestSentenceTokenize(unittest.TestCase):
    def test_sentence_tokenize_text(self):
        p = SpacyProcessor()
        actual = p.sentence_tokenize('Hunden Katzen Mäuse.' * 3)
        expected = [['Hunden Katzen Mäuse.'] * 3]
        self.assertEqual(expected, actual)

    def test_sentence_tokenize_text_as_list(self):
        p = SpacyProcessor()
        actual = p.sentence_tokenize(['Hunden Katzen Mäuse.' * 3])
        expected = [['Hunden Katzen Mäuse.'] * 3]
        self.assertEqual(expected, actual)

    def test_sentence_tokenize_texts(self):
        p = SpacyProcessor()

        actual = p.sentence_tokenize(
            [
                'Hunden Katzen Mäuse.' * 3,
                'Mädels Männer Frauen.' * 3
            ]
        )

        expected = [
            ['Hunden Katzen Mäuse.'] * 3,
            ['Mädels Männer Frauen.'] * 3
        ]

        self.assertEqual(expected, actual)


class TestStem(unittest.TestCase):
    def test_stem_text(self):
        p = SpacyProcessor()
        actual = p.stem('Hunden Katzen Mäuse')
        expected = ['hund katz maus']
        self.assertEqual(expected, actual)

    def test_stem_text_as_list(self):
        p = SpacyProcessor()
        actual = p.stem(['Hunden Katzen Mäuse'])
        expected = ['hund katz maus']
        self.assertEqual(expected, actual)

    def test_stem_texts(self):
        p = SpacyProcessor()
        actual = p.stem(
            [
                'Hunden Katzen Mäuse',
                'Mädels Männer Frauen']
        )
        expected = [
            'hund katz maus',
            'madel mann frau'
        ]
        self.assertEqual(expected, actual)


class TestTokenize(unittest.TestCase):
    def test_tokenize_text(self):
        p = SpacyProcessor()
        actual = p.tokenize('a b c')
        expected = [
            ['a', 'b', 'c']
        ]
        self.assertEqual(expected, actual)

    def test_tokenize_text_as_list(self):
        p = SpacyProcessor()
        actual = p.tokenize(['a b c'])
        expected = [
            ['a', 'b', 'c']
        ]
        self.assertEqual(expected, actual)

    def test_tokenize_texts(self):
        p = SpacyProcessor()
        actual = p.tokenize(
            [
                'a b c',
                '1 2 3']
        )
        expected = [
            ['a', 'b', 'c'],
            ['1', '2', '3']
        ]
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
