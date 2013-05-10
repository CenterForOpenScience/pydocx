#pydocx
	pydocx is a parser that breaks down the elements of
	a docxfile so that the file can be converted into 
	the markup language of your choice. 
	
#Currently Supported
	tables
		nested tables
		rowspans
		colspans
		lists in tables
	lists
		list styles
		nested lists
		list of tables
		list of pragraphs
	justification
	images
	bold 
	italics
	underline
	hyperlinks
	headings


#Usage
	We have written the Docx2Html class, which inherits
	DocxParser and renders the docx document in HTML.
	However, if you wanted to convert to markdown 
	instead of HTML, you would simply create your own
	class (i.e., Docx2Markdown), inherit DoxcParser, 
	and write methods to display the elements 
	of the file appropriately for Markdown.
	
	ex. 
	
	class Docx2Markdown(DocxParser):
		    
		def escape(self, text): important if you need to escape characters that may not
			return text			render incorrectly in your markup language
			 
		def linebreak(self):    we know that \n is the linebreak symbol for markup,
			return '\n'			so we override the linebreak method

		def paragraph(self, text): we know that a pargaph in markup is just the text
			return text + '\n'	   and \n, so we override the paragraph method
		
		def bold(self, text):	   		we know that ** denotes bold in markup, so we
			return '**' + text + '**'  	override that method
			
		etc... 
	
	all methods that you would want to override are
	included in the DocxParser class, as follows: 

	class DocxParser:
	
		@property
		def parsed(self):
			return self._parsed

		@property
		def escape(self, text):
			return text

		@abstractmethod
		def linebreak(self):
			return ''

		@abstractmethod
		def paragraph(self, text):
			return text

		@abstractmethod
		def heading(self, text, heading_level):
			return text

		@abstractmethod
		def insertion(self, text, author, date):
			return text

		@abstractmethod
		def hyperlink(self, text, href):
			return text

		@abstractmethod
		def image_handler(self, path):
			return path

		@abstractmethod
		def image(self, path, x, y):
			return self.image_handler(path)

		@abstractmethod
		def deletion(self, text, author, date):
			return text

		@abstractmethod
		def bold(self, text):
			return text

		@abstractmethod
		def italics(self, text):
			return text

		@abstractmethod
		def underline(self, text):
			return text

		@abstractmethod
		def tab(self):
			return True

		@abstractmethod
		def ordered_list(self, text):
			return text

		@abstractmethod
		def unordered_list(self, text):
			return text

		@abstractmethod
		def list_element(self, text):
			return text

		@abstractmethod
		def table(self, text):
			return text

		@abstractmethod
		def table_row(self, text):
			return text

		@abstractmethod
		def table_cell(self, text):
			return text

		@abstractmethod
		def page_break(self):
			return True

		@abstractmethod
		def indent(self, text, left='', right='', firstLine=''):
			return text

