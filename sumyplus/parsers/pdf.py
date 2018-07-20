import subprocess
import os
import sumyplus

from .html import HtmlParser


class PdfParser(object):
    """Parser of text from PDF format into DOM."""
    poppler_path = os.path.join(sumyplus.__path__[0], "poppler-lite\\")
    pdftohtml_exe = "\"" + poppler_path + "pdftohtml.exe" + "\""
    args = "-s -c -noframes"

    def __init__(self, pdf_file, tokenizer):
        super(PdfParser, self).__init__()

        self.pdf_file = pdf_file
        self.html_filename = pdf_file.split('.')[0] + '.html'
        self.tokenizer = tokenizer
        #
        process_call = self.create_process()
        self.pdf2html(process_call)

    def create_process(self):
        return ' '.join([self.pdftohtml_exe, self.args, self.pdf_file])

    def pdf2html(self, process_call):
        print('Using poppler executable for pdf parsing, ', self.pdftohtml_exe, '\n')
        if os.path.isfile(self.html_filename):
            os.remove(self.html_filename)
        flag = subprocess.call(process_call, shell=False)
        assert not bool(flag), "Process failed to execute successfully"

    def create_htmlparser(self):
        return HtmlParser.from_file(self.html_filename, None, self.tokenizer)
