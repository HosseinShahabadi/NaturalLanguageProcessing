corpus = "aaaabbddbdaab"
reserved_vocab = ["S", "T", "U", "V", "W", "X", "Y", "Z"]
mapping = {}


def encode(corpus: str, reserved_vocab, mapping):
    pairs = dict()

    for index in range(0, len(corpus) - 1):
        pair = corpus[index : index + 2]

        pairs.setdefault(pair, 0)
        pairs[pair] += 1

    if len(pairs) == 0 or max(pairs.values()) <= 1:
        return corpus, reserved_vocab, mapping

    pairs = list(pairs.items())
    pairs = sorted(pairs, key=lambda x: x[1], reverse=True)

    pair, _ = pairs.pop(0)

    new_vocab = reserved_vocab.pop()
    mapping[new_vocab] = pair

    corpus = corpus.replace(pair, new_vocab)
    return corpus, reserved_vocab, mapping


for iter in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    previous_corpus = corpus
    corpus, reserved_vocab, mapping = encode(corpus, reserved_vocab, mapping)

    if corpus == previous_corpus:
        break

    print(f"new corpus: {corpus}")
