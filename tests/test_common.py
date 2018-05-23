import unittest
import bedrock.collection as collection
import pandas as pd


class TestBalance(unittest.TestCase):
    def test_balance_df(self):
        sentences = ['a a', 'b', 'c c c', 'd d d d', 'e e', 'f']
        targets = [0, 1, 2, 0, 1, 0]
        df = pd.DataFrame(
            {
                'sentence': sentences,
                'target': targets
            }
        )

        df_balanced = collection.balance_df(df, target_field='target')

        expected = pd.DataFrame(
            {
                'sentence': ['a a', 'b', 'c c c', 'd d d d', 'e e', 'f', 'e e', 'c c c', 'c c c'],
                'target': [0, 1, 2, 0, 1, 0, 1, 2, 2]
            }
        )

        actual = df_balanced

        self.assertEqual(expected, actual)
