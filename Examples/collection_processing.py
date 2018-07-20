collectionpath = "C:/Users/zwelz3/Documents/GTRI Projects/ECCT_EW_EMS/Market Research/Environment/Adversary Capabilities/Advanced Technology Weapons/"


from sumyplus.collection.collection import Collection
from sumyplus.summarizers.lex_rank import LexRankSummarizer as Summarizer
from sumyplus.nlp.stemmers import Stemmer
from sumyplus.utils import get_stop_words
from sumyplus.nlp.tokenizers import Tokenizer

LANGUAGE = "english"
stemmer = Stemmer(LANGUAGE)
summarizer = Summarizer(stemmer)
summarizer.stop_words = get_stop_words(LANGUAGE)
token = Tokenizer(LANGUAGE)

term_frequency_threshold = 0.05   # normalized term freq limit
num_sentences = 8

cobj = Collection(collectionpath)
cobj.process_collection()
cobj.generate_metadata(summarizer, token, term_frequency_threshold)

composite_document = cobj.create_composite_document("hypersonic", token)
composite_summary = cobj.summarize_composite(composite_document, summarizer, num_sentences)

for sentence in composite_summary:
	print(sentence._text)

