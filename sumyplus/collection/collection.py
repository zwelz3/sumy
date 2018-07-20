#
#
#
#
import os
import json
import subprocess
#
from .metadoc import create_all_metadocs, build_supermetadocs
#
from shutil import copy, rmtree
#
import sumyplus
from sumyplus.parsers.html import HtmlParser
from sumyplus.models.tf import TfDocumentModel
from sumyplus.models.dom import Paragraph, ObjectDocumentModel
from sumyplus.collection.topic_model import Query


def get_items(path, flist, dlist, lvl=0):
    """Scans a path and returns the items that were discovered at the path.
       Recursively searches so be careful calling on massive directories."""
    for item in os.listdir(path):
        pitem = os.path.join(path, item)
        if os.path.isdir(pitem):
            dlist[pitem] = lvl + 1
            print(f"\nDiscovered directory '{item}'")
            flist, dlist = get_items(pitem, flist, dlist, lvl + 1)
        elif pitem.split('.')[-1] in Collection.supported_exts:
            flist.add(pitem)
            print(f"-> Discovered file '{item}'")

    return flist, dlist


def create_html(filepath, poppler_exe):
    """Create HTML file at location {filepath}
    TODO replace with sumy pdf parser"""
    wfilepath = "\""+filepath+"\""
    process_call = ' '.join([poppler_exe,'-c -s -noframes',wfilepath])
    flag = subprocess.call(process_call)
    assert not bool(flag), "Process failed to execute successfully"
    path_ext = filepath.split('\\')[-1].split('.')[0]+'.html'
    basepath = os.path.dirname(filepath)
    return '\\'.join([basepath, path_ext])


def remove_stopwords(counter, stopwords):
    """Removes stopwords from counter object
    TODO move to sump pdf parser"""
    stopwords_toRemove = frozenset.intersection(stopwords, frozenset(counter))
    for word in stopwords_toRemove:
        _ = counter.pop(word)
    return counter


def get_metawords(threshold, document):
    """Uses the term frequency document model to return a limited number of words and their count."""
    metawords = {}
    for word, count in document._terms.most_common():
        nfreq = document.normalized_term_frequency(word)
        if  nfreq > threshold and count > 1:
            # print(word, nfreq)
            metawords[word] = count
        else:
            return metawords
    return metawords


# TODO resolve issues
def parse_collection(flist, summarizer, token, term_frequency_threshold):
    poppler_path = os.path.join(sumyplus.__path__[0], "poppler-lite\\")
    pdftohtml_exe = "\"" + poppler_path + "pdftohtml.exe" + "\""
    print('Using poppler executable for pdf parsing, ', pdftohtml_exe, '\n')
    for f_ind, filepath in enumerate(flist):
        f_extension = filepath.split('.')[-1]
        # redundant check for now TODO remove
        supported_exts = set(['pdf', 'html', 'txt'])  # TODO replace with class attribute
        if f_extension in supported_exts:
            # These need to be parsed
            print(f'Parsing {f_ind+1}/{len(flist)}: ', filepath)
            if f_extension == 'pdf':
                print(' -- PDFs are converted to HTML prior to parsing in order to retain formatting.')
                path_ext = filepath.split('\\')[-1].split('.')[0] + '_tmp'
                basepath = os.path.dirname(filepath)
                tmpdir = '\\'.join([basepath, path_ext])
                print('    - Creating temporary directory:\t', tmpdir)
                os.makedirs(tmpdir)
                assert os.path.isdir(tmpdir)
                copypath = copy(filepath, tmpdir)
                # Create HTML file
                html_file = create_html(copypath, pdftohtml_exe)
                # Parse HTML file into document
                parser = HtmlParser.from_file(html_file, None, token)
                # Create naive summary for metadata document
                metasummary = ' '.join([str(sentence) for sentence in summarizer(parser.document, 10)])
                # print("\nNaive document summary: \n", metasummary)
                # Create term frequency document
                tfDoc = TfDocumentModel(parser.document.words, token)
                # Remove stopwords
                # print("\nRemoving stopwords:")
                # print("# words before: ", len(tfDoc._terms))
                tfDoc._terms = remove_stopwords(tfDoc._terms, summarizer.stop_words)
                # print("# words after: ", len(tfDoc._terms))
                # print("\nNaive term frequency threshold: ", term_frequency_threshold)
                # Get words for metadata document
                metawords = get_metawords(term_frequency_threshold, tfDoc)
                # print("\nWords for metadata document: \n", metawords)
                # Write results to metadata document
                mdoc_path = '\\'.join([os.path.dirname(filepath), filepath.split('\\')[-1].split('.')[0] + '.mdoc'])
                print("    - Updating metadata file: ", mdoc_path)
                with open(mdoc_path, 'r') as mdoc:
                    payload = json.load(mdoc)

                # add to payload
                payload["summary"] = [metasummary]
                payload["keywords"] = metawords

                # write payload
                os.remove(mdoc_path)
                with open(mdoc_path, 'w') as mdoc:
                    json.dump(payload, mdoc, indent=2)
                # remove temporary directory
                print('    - Removing temporary directory:\t', tmpdir)
                rmtree(tmpdir)


def reparser(mdocs, token):
    supported_exts = set(['pdf', 'html', 'txt'])  # TODO replace with class attribute
    poppler_path = os.path.join(sumyplus.__path__[0], "poppler-lite\\")
    pdftohtml_exe = "\"" + poppler_path + "pdftohtml.exe" + "\""
    print('Using poppler executable for pdf parsing, ', pdftohtml_exe, '\n')
    parsed_docs = {}
    for f_ind, metapath in enumerate(mdocs):
        with open(metapath) as mobj:
            data = json.load(mobj)
            filepath = "\\".join([data["directory"], data["filename"]])
            print(filepath)

        f_extension = filepath.split('.')[-1]
        # redundant check for now TODO remove
        if f_extension in supported_exts:
            # These need to be parsed
            print(f'Parsing {f_ind+1}/{len(mdocs)}: ', filepath)
            if f_extension == 'pdf':
                print(' -- PDFs are converted to HTML prior to parsing in order to retain formatting.')
                path_ext = filepath.split('\\')[-1].split('.')[0] + '_tmp'
                basepath = os.path.dirname(filepath)
                tmpdir = '\\'.join([basepath, path_ext])
                print('    - Creating temporary directory:\t', tmpdir)
                os.makedirs(tmpdir)
                assert os.path.isdir(tmpdir)
                copypath = copy(filepath, tmpdir)
                # Create HTML file
                html_file = create_html(copypath, pdftohtml_exe)
                # Parse HTML file into document
                parser = HtmlParser.from_file(html_file, None, token)
                parsed_docs[html_file] = parser
                # remove temporary directory
                print('    - Removing temporary directory:\t', tmpdir)
                rmtree(tmpdir)

    return parsed_docs


def create_superdoc(parsed_docs):
    """"""
    super_document_paragraphs = []
    for d_parser in parsed_docs.values():
        super_document_paragraphs.extend(list(d_parser.document.paragraphs))

    super_document = ObjectDocumentModel(super_document_paragraphs)
    return super_document


class Collection(object):
    """"""
    supported_exts = {'pdf', 'html', 'txt'}

    def __init__(self, collection_path):
        self.path = os.path.abspath(collection_path)
        assert os.path.isdir(self.path)
        # Initialize instance vars
        self.flist = set()
        self.dlist = {self.path: 0}

    def process_collection(self):
        """Populate collection file and directory lists."""
        print(f"Processing collection at path ...\\{os.path.basename(self.path)}: \n")
        self.flist, self.dlist = get_items(self.path, self.flist, self.dlist)
        print(f"\nTotal number of directories:  {len(self.dlist)}")
        print(f"Total number of files:  {len(self.flist)} \n")

    def generate_metadata(self, summarizer, token, term_frequency_threshold):
        """"""
        create_all_metadocs(self.flist)
        parse_collection(self.flist, summarizer, token, term_frequency_threshold)
        build_supermetadocs(self.dlist)

    def build_query(self):
        """"""
        return Query(self.path)

    def create_composite_document(self, keyword, token):
        """"""
        qobj = self.build_query()
        mdocs = qobj.query_metafiles(keyword)
        parsed_docs = reparser(mdocs, token)
        super_document_paragraphs = []
        for d_parser in parsed_docs.values():
            # add methods here to clean up the ObjectDocumentModel
            # Remove small sentences TODO move to function
            thresh = 6
            for paragraph in d_parser.document.paragraphs:
                min_slen = min([len(sentence.words) for sentence in paragraph.sentences])
                if min_slen > thresh:  # arbitrary length TODO replace with intelligence
                    super_document_paragraphs.append(paragraph)
                else:
                    # todo note sentece.words is only "significant" words from stemmer
                    trimmed_sentences = tuple([sentence for sentence in paragraph.sentences
                                               if len(sentence.words) > thresh])
                    new_paragraph = Paragraph(trimmed_sentences)
                    super_document_paragraphs.append(new_paragraph)

        return ObjectDocumentModel(super_document_paragraphs)

    @staticmethod
    def summarize_composite(composite_doc, summarizer, num_sentences):
        return summarizer(composite_doc, num_sentences)
