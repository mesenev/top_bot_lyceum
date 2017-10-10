from collections import Counter
from html.parser import HTMLParser
from typing import List, Tuple, Iterable, Set, Mapping, NamedTuple
import typing

void_elements = set(('area base br col embed hr '
                     'img input keygen link meta '
                     'param source track wbr').split())


class Tag(NamedTuple):
    name: str
    attrs: Mapping[str, str]
    classes: Set[str]


class Parser(HTMLParser):

    output: List[str] = None
    _tags_stack: List[Tag] = None
    _classes: typing.Counter[str] = None
    _tags: typing.Counter[str] = None

    def error(self, message):
        raise Exception(message)

    def on_feed(self):
        pass

    def on_starttag(self, t: Tag):
        pass

    def on_endtag(self, t: Tag):
        pass

    def on_data(self, t: Tag, data: str):
        pass

    def feed(self, data):
        self.output = []
        self._tags_stack = []
        self._classes = Counter()
        self._tags: typing.Counter[str] = Counter()

        self.on_feed()
        super(Parser, self).feed(data)

    def handle_starttag(self,
                        tag: str,
                        attrs: Iterable[Tuple[str, str]]):

        attrs_dict = dict(attrs)
        classes = set(attrs_dict.get('class', '').split())
        t = Tag(tag, attrs_dict, classes)

        self.on_starttag(t)

        if tag not in void_elements:
            self._tags_stack.append(t)
            self._classes.update(classes)
            self._tags[tag] += 1

    def handle_endtag(self, tag):
        if tag not in void_elements and tag == self._tags_stack[-1].name:
            t = self._tags_stack.pop()
            self._classes -= Counter(t.classes)
            self._tags -= Counter([tag])
            self.on_endtag(t)

    def handle_data(self, data: str):
        # handle_data can be called before any tags
        if self._tags_stack and data.strip():
            self.on_data(self._tags_stack[-1], data.strip())