import json
import operator
import os
import string
import types
from typing import Self, Callable

import mpmath as md

class SplitTableDict():
    pass

class Ngram():
    symbols = string.ascii_lowercase

    @classmethod
    def from_file(cls, path: str, filetext_n: int = 0, divider: Callable = operator.truediv) -> Self:
        inst = cls(divider)
        inst._path_arg = path

        if filetext_n:
            inst._ngram_length = filetext_n
            def load_counts(self) -> None:
                with open(self._path_arg) as f:
                    text = f.read()
                del self._path_arg

                self._set_counts(*self.parse_counts(text, self._ngram_length))
        else:
            def load_counts(self) -> None:
                with open(self._path_arg) as f:
                    file_data = json.load(f)
                del self._path_arg
                
                self._ngram_length = len(next(file_data['count'].__iter__()))
                self._set_counts(file_data['count'], file_data['total'])

        inst._load_counts = types.MethodType(load_counts, inst)
        return inst

    @classmethod
    def from_text(cls, text: str, n: int, divider: Callable = operator.truediv) -> Self:
        inst = cls(divider)
        inst._text_arg = text
        inst._ngram_length = n

        def load_counts(self) -> None:
            self._set_counts(*self.parse_counts(self._text_arg, self._ngram_length))
            del self._text_arg

        inst._load_counts = types.MethodType(load_counts, inst)
        return inst

    @classmethod
    def from_counts(cls, counts: dict[str, int], total: int, divider: Callable = operator.truediv) -> Self:
        inst = cls(divider)
        inst._counts_arg = counts
        inst._total_arg = total
        inst._ngram_length = len(next(counts.__iter__()))

        def load_counts(self) -> None:
            self._set_counts(self._counts_arg, self._total_arg)
            del self._counts_arg
            del self._total_arg

        inst._load_counts = types.MethodType(load_counts, inst)
        return inst

    def __init__(self, divider: Callable) -> None:
        def attr_loader(loader_name: str, *attrs: str) -> Callable:
            def wrapper(inst: object):
                def recursive_attrs(inst, attrs):
                    attr = getattr(inst, attrs[0])
                    if len(attrs) == 1:
                        return attr
                    else:
                        attrs.pop(0)
                        return recursive_attrs(attr, attrs)
                    
                if not recursive_attrs(inst, list(attrs)):
                    getattr(inst, loader_name)()
                return recursive_attrs(inst, list(attrs))
            return wrapper

        self._divider = divider
        self._ngram_length = self._total = self._min_ngram = self._max_ngram = None
        self._counts, self._freqs, self._inv_freqs = SplitTableDict(), SplitTableDict(), SplitTableDict()

        cls = type(self)
        cls.ngram_length = property(attr_loader('_load_counts', '_ngram_length'))
        cls.total = property(attr_loader('_load_counts', '_total'))
        cls.min_ngram = property(attr_loader('_load_counts', '_max_ngram'))
        cls.max_ngram = property(attr_loader('_load_counts', '_min_ngram'))
        cls.counts = property(attr_loader('_load_counts', '_counts', '__dict__'))
        cls.freqs = property(attr_loader('_load_freqs', '_freqs', '__dict__'))
        cls.inv_freqs = property(attr_loader('_load_inv_freqs', '_inv_freqs', '__dict__'))

    def _parse_counts(self, text: str, n: int) -> tuple[dict[str, int], int]:
        counts = {}
        prev = []
        total = 0
        counter = 0
        for char in text:
            if (char := char.lower()) in self.symbols:
                prev.append(char)
                counter += 1
            else:
                continue

            if counter % n == 0:
                if (ngram := ''.join(prev)) in counts:
                    counts[ngram] += 1
                else:
                    counts[ngram] = 1
                total += 1

        return (counts, total)

    def _set_counts(self, counts: dict[str, int], total: int) -> None:
        self._total = total
        for ngram, count in counts.items():
            setattr(self._counts, ngram, count)

    def _load_freqs(self) -> None:
        for ngram, count in self.counts.items():
            setattr(self._freqs, ngram, self._divider(count, self.total))

    def _load_inv_freqs(self) -> None:
        total = self.total
        for ngram, count in self.counts.items():
            setattr(self._inv_freqs, ngram, self._divider(total - count, total))

    def _load_counts(self) -> None:
        pass

class Ngrams():
    lang_dir = os.path.abspath(os.path.join(__file__, '../..\\lang')) + '\\'

    def __init__(self, divider: Callable = operator.truediv):
        self.divider = divider
        self.loaded_ngrams = {}
        self.en_ngrams = self.en_monograms, self.en_bigrams, self.en_trigrams, self.en_quadgrams, self.en_quintgrams =\
            [Ngram.from_file(self.lang_dir + f'en_{i + 1}grams.json', divider=divider) for i in range(5)]
        
    def load(self, ngram: Ngram):
        self.loaded_ngrams[ngram.ngram_length] = ngram

    def ioc(self, n, use_loaded=False):
        if use_loaded: ngrams = self.loaded_ngrams[n - 1]
        else: ngrams = self.en_ngrams[n - 1]
        
        return self.divider(sum([count * (count - 1) for count in ngrams.counts.values()]), ngrams.total * (ngrams.total - 1))

    def ugrams(self, n, length, use_loaded=False):
        if use_loaded: ngrams = self.loaded_ngrams[n - 1]
        else: ngrams = self.en_ngrams[n - 1]

        exponent = length // n
        return len(ngrams.freqs) - sum([freq ** exponent for freq in ngrams.freqs.values()])
    
    def ioc_uniform(self):
        return self.divider(1, 26)

    def ugrams_uniform(self, n, length):
        a = length // n
        b = 26 ** n
        c = b ** (a - 1)
        return self.divider(b * c - (b - 1) ** a, c)