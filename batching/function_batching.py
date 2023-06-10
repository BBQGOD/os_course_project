GPT2_URLS = []
SD_URLS = []

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.word = None

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.nodes = [self.root]

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                new_node = TrieNode()
                node.children[char] = len(self.nodes)
                self.nodes.append(new_node)
            node = self.nodes[node.children[char]]
        node.is_end_of_word = True
        node.word = word

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = self.nodes[node.children[char]]
        return node

    # def longest_common_prefix(self, words):
    #     if not words:
    #         return ""
    #     for i, char in enumerate(words[0]):
    #         for word in words[1:]:
    #             if i >= len(word) or word[i] != char:
    #                 return words[0][:i]
    #     return words[0]

    def longest_prefix(self, word):
        node = self.search(word)
        if not node:
            return ""
        words = []
        stack = [(node, "")]
        while stack:
            node, prefix = stack.pop()
            if node.is_end_of_word:
                words.append(prefix + node.word)
            for char, child_index in node.children.items():
                stack.append((self.nodes[child_index], prefix + char))
        return self.longest_common_prefix(words)
