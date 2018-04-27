from abc import ABC, abstractmethod


class Processor(ABC):
    _lang_convert = {
        'de': 'german',
        'en': 'english'
    }

    # TODO: Maybe convert to static
    def _to_list(self, text_input):
        if type(text_input) is str:
            return [text_input]
        return text_input

    # TODO: Maybe convert to static
    def viperize(self, text_input, vip_words):
        # Adds vip words to the end of the text if there is a match.
        texts = self._to_list(text_input)

        if not vip_words:
            print('Nothing to do.')
            return texts

        for text in texts:
            vip_words_found = []
            for vip_word in vip_words:
                if vip_word in text:
                    vip_words_found.append(vip_word)
            text += ' '.join(vip_words_found)
        return texts

    @abstractmethod
    def tokenize(self, text_input):
        pass

    @abstractmethod
    def lemmatize(self, text_input):
        pass

    @abstractmethod
    def stem(self, text_input):
        pass

    @abstractmethod
    def sentence_tokenize(self, text_input):
        pass

    @abstractmethod
    def remove_short(self, text_input, min_word_len):
        pass

    @abstractmethod
    def remove_stop_words(self, text_input):
        pass

    @abstractmethod
    def remove_punctuation(self, text_input):
        pass

    def replace_chars(
            self,
            text_input,
            chars_to_replace,
            replacement_char=' '):
        # Always returns list

        # Replace chars in text with another char.
        texts = self._to_list(text_input)

        if not chars_to_replace:
            return texts

        processed_texts = []
        for text in texts:
            for unwanted_char in chars_to_replace:
                text.replace(unwanted_char, replacement_char)
            processed_texts.append(text)
        return processed_texts
