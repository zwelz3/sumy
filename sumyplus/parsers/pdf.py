import subprocess
import os
import sumyplus

from .html import HtmlParser

sumypath = sumyplus.__path__[0]
popplerpath = sumypath+"\\poppler-lite\\"
pdftohtml_exe = popplerpath+"pdftohtml.exe"

args = "-s"


class PdfParser(object):
    """Parser of text from PDF format into DOM."""

    def __init__(self, pdf_file, tokenizer):
        super(PdfParser, self).__init__()

        self.pdf_file = pdf_file
        self.html_filename = pdf_file.split('.')[0] + '-html.html'
        self.tokenizer = tokenizer
        #
        process_call = self.create_process()
        self.pdf2html(process_call)

    def create_process(self):
        return ' '.join([pdftohtml_exe, args, self.pdf_file])

    def pdf2html(self, process_call):
        if os.path.isfile(self.html_filename):
            os.remove(self.html_filename)
        flag = subprocess.call(process_call, shell=False)
        assert not bool(flag), "Process failed to execute successfully"

    def create_htmlparser(self):
        return HtmlParser.from_file(self.html_filename, None, self.tokenizer)
