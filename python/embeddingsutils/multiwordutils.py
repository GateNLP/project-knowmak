# simple implementation of a multiword replacer

from collections import defaultdict

class MultiWordUtils:

    @staticmethod
    def build_trie_fromiter(iterable):
        trie = defaultdict()
        for line in iterable:
            curnode = trie
            pos = 0
            for word in line:
                pos += 1
                islast = (pos == len(line))
                tpl = curnode.get(word)
                if not tpl:
                    node = defaultdict()
                    curnode[word] = (node, islast)
                else:
                    node = tpl[0]
                    islast = islast or tpl[1]
                    curnode[word] = (node, islast)
                curnode = node
        return trie

    @staticmethod
    def build_trie_fromfile(file):
        def file_iter(file):
            with open(file, "rt", encoding="utf-8") as ins:
                for line in ins:
                    line = line.strip()
                    words = line.split()  # split on any number of any whitespace
                    yield words
        return MultiWordUtils.build_trie_fromiter(file_iter(file))

    def __init__(self, source=None):
        """Create an instance and initialise it from source being either a string which is the path to
        a file that contains one multiword expression per line, or an iterable that contains one lists
        of multi word expressions."""
        if not source:
            raise Exception("source must be a file name or a list of word lists")
        if isinstance(source, list):
            self.trie = MultiWordUtils.build_trie_fromiter(source)
        else:
            self.trie = MultiWordUtils.build_trie_fromfile(source)

    def matches(self, wordlist):
        """Returns True if wordlist matches something in the trie"""
        curnode = self.trie
        flag = False
        for word in wordlist:
            tpl = curnode.get(word)
            if not tpl:
                return False
            else:
                flag = tpl[1]
                curnode = tpl[0]
        return flag

    def longest_match(self, wordlist, position=0):
        """Return the longest list of words that match the trie in wordlist, from the given position"""
        curnode = self.trie
        match = []
        i = 0
        lastend = 0
        for word in wordlist[position:]:
            tpl = curnode.get(word)
            if not tpl:
                return match[0:lastend]
            else:
                match.append(word)
                i += 1
                if tpl[1]:
                    lastend = i
                curnode = tpl[0]
        return match[0:lastend]

    def replace_matches(self, wordlist, overlapping=False, combined=False, single=True, concat_char="_"):
        # use find_longest_match to find the longest match at each position. For now only
        # implement overlapping is False where after replacement of n words the next attempt
        # to match is made after the last matched words.
        # So for the list ["this", "is", "a", "list", "of", "words", "to", "be", "matched"], 
        # and if we have the entries
        # ["is", "a", "list"] and ["a", "list", "of", "words"] with overlapping False we 
        # would only create replacement ["this", "is_a_list", "of", "words", "to", "be", "matched"]
        # with overlapping = True we would also create 
        # ["this", "is", "a_list_of_words", "to", "be", "matched"]
        # If single is true, should return a list of replacement where each individual replacement
        # is carried out. If combined is True should return a list with a single replacement where
        # all non-overlapping replacements are carried out. If both combined and single are true,
        # should return both, but only return a single replacement if there is just one position!!
        if overlapping:
            raise Exception("overlapping=True not yet implemented")
        repl_singles = []
        repl_comb = []
        nrepl = 0
        i = 0
        while i < len(wordlist):
            lmtch = self.longest_match(wordlist, i)
            if len(lmtch) > 1:
                nrepl += 1
                concat = concat_char.join(lmtch)
                if single:
                    repl_singles.append(wordlist[0:i]+[concat]+wordlist[i+len(lmtch):])
                if combined:
                    repl_comb.append(concat)
                i += len(lmtch)
            else:
                if combined:
                    repl_comb.append(wordlist[i])
                i += 1
        if nrepl == 0:
            return []
        elif nrepl == 1:
            if single:
                return repl_singles
            else:
                return [repl_comb]
        else:
            ret = []
            if single:
                ret = ret + repl_singles
            if combined:
                ret.append(repl_comb)
            return ret

    def __repr__(self):
        return "MultiWordUtils(trie=%r)" % self.trie


if __name__ == "__main__":
    # some quick tests
    mwlist = [["this", "is", "some", "mw", "expression"], ["another", "one"], ["and", "this"], ["and", "this", "too"]]
    trie = MultiWordUtils(mwlist)
    print("trie: %r" % trie)
    assert trie.matches(["and", "this"]) is True
    assert trie.matches(["but", "this"]) is False
    assert trie.matches(["and", "this", "too"]) is True
    lm = trie.longest_match(["this", "is", "something", "and", "this", "too", "and", "this"], 0)
    assert lm == []
    lm = trie.longest_match(["this", "is", "something", "and", "this", "too", "and", "this"], 3)
    assert lm == ["and", "this", "too"]
    lm = trie.longest_match(["this", "is", "something", "and", "this", "too", "and", "this"], 6)
    assert lm == ["and", "this"]
    ret = trie.replace_matches(["this", "is", "another", "one"], single=True, combined=True)
    assert ret == [['this', 'is', 'another_one']]
    ret = trie.replace_matches(["this", "is", "another", "one", "and"], single=True, combined=True)
    assert ret == [['this', 'is', 'another_one', 'and']]
    ret = trie.replace_matches(["this", "is", "another", "one", "and", "this", "too", "see"], single=True, combined=True)
    assert ret == [['this', 'is', 'another_one', 'and', 'this', 'too', 'see'],
                   ['this', 'is', 'another', 'one', 'and_this_too', 'see'],
                   ['this', 'is', 'another_one', 'and_this_too', 'see']]

