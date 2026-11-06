# DocChat

DocChat is a Python chatbot that uses the Groq API to generate responses to user messages.

## What It Does

- Conversations through the terminal
- Remembers previous messages in a conversation
- Supports four tools: calculate, ls, cat, and grep
- Allows users to execute tools manually using slash commands, such as /calculate and /ls
- Allows the language model to call tools automatically when needed
- Includes path-security checks to prevent unauthorized file access
- Can be installed and launched from the terminal using the chat command

## Installation

Install the required dependencies and the package:

    python3 -m pip install -r requirements.txt
    python3 -m pip install .

## Example Sessions

### Homepage (`test_projects/lab-homepage`)

This project is a personal soccer-focused website featuring a homepage, blog, games page, and contact page.

```text
cd test_projects/lab-homepage
chat
chat> /ls .
['./README.md', './argentinacaboverde.webp', './blog.html', './contact.html', './englandargentina.jpg', './englandnorway.webp', './francespain.jpeg', './games.html', './index.html', './me.jpg', './mesoccer.jpeg', './mexicoengland.jpeg', './style.css', './submission.toml', './usabosnia.jpeg']
chat> What is this project about, and what are its main pages?
The project appears to be a small personal website or portfolio focused on football (soccer) and personal media. The key pages are:
- index.html – the main landing page.
- blog.html – a page for blog posts or articles.
- contact.html – a contact form or contact information.
- games.html – a page that showcases games or game-related content.
The project also includes a style.css file, submission.toml, and several image files.
```

This project demonstrates how DocChat can inspect a website project and explain its organization.

### Markdown Compiler (`test_projects/markdown-compiler`)

This project converts Markdown documents into HTML, supporting formatting, links, images, paragraphs, and code blocks. It also supports optional CSS styling and HTML minification.

```text
cd test_projects/markdown-compiler
chat
chat> /ls .
['./README.md', './example', './markdown_compiler', './pyproject.toml', './requirements.txt']
chat> What does this project do, and how does its Markdown compiler work?
The compiler works in a few stages:

1. Line-by-line transformations: helper functions convert Markdown syntax into HTML tags, including headings, bold, italics, strikethrough, inline code, links, and images.

2. Paragraph and code-block handling: compile_lines adds paragraph tags and handles multiline code blocks using <p> and <pre> tags.

3. HTML wrapper and optional CSS: markdown_to_html places the converted content inside an HTML document and optionally adds external stylesheets.

4. Minification and file output: minify removes redundant whitespace, while convert_file reads a Markdown file and writes the resulting HTML file.

In short, the compiler transforms Markdown formatting into HTML, adds document structure, and produces a finished HTML file.
```

This demonstration shows how DocChat can inspect a software project and explain its implementation, including the stages of its Markdown-to-HTML conversion.

### eBay Scraper (`test_projects/ebay-scraper`)

This project is a Python web scraper that collects eBay product listings, extracts relevant information, and organizes the results into JSON files.

```text
cd test_projects/ebay-scraper
chat
chat> /ls .
['./README.md', './ebay-dl.py', './flower seeds.json', './headphones.json', './laptop.json']
chat> What does this project do, and how does it collect and organize product information?
The project is a Python web scraper that pulls product listings from eBay and stores the results in JSON files.

The ebay-dl.py script:
1. Takes a search term and a directory of HTML practice pages.
2. Requests and parses search result pages using requests and Beautiful Soup.
3. Extracts product names, prices, status, shipping costs, free returns, and items sold.
4. Aggregates the listings into a single list.
5. Writes the results to a JSON file named after the search term.

The repository includes static practice HTML pages because live eBay requests return a 403 error. The three example JSON files contain 30 listings each.
```

This demonstration shows how DocChat can explain a web-scraping project, including its data extraction process and JSON output.