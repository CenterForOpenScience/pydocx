#pydocx
	pydocx is a parser that breaks down the elements of
	a docxfile so that the file can be converted into 
	the markup language of your choice. 

#Usage
	We have written the Docx2Html class, which inherits
	DocxParser and renders the docx document in HTML.
	However, if you wanted to convert to markdown 
	instead of HTML, you would simply create your own
	class (i.e., Docx2Markdown), inherit DoxcParser, 
	and write methods to display the elements 
	of the file appropriately for Markdown.
	
	ex. class Docx2Markdown(DocxParser):
			def linebreak(self):
				return '\n'
	
	all methods that you would want to override are
	included in the DocxParser class. 
	
	ex. class DocxParser(self):
			@property
    		def escape(self):
        		return ''
    
    
	
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