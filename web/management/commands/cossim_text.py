from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
import math

tokenizer = RegexpTokenizer(r'[a-z]+')
stopwords = set(stopwords.words("english"))


def extract_words(self, text):
    """Tokenize a string using NLTK and return a set of lowercased words."""
    content = text.lower()
    tokens = self.tokenizer.tokenize(content)
    return (w for w in tokens if w not in self.stopwords)


def cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    return Counter(extract_words(text))
