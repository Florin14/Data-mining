from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
import os


# Function to read questions from the file
def read_questions(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 4):
            category = lines[i].strip()
            clue = lines[i + 1].strip()
            answer = lines[i + 2].strip()
            questions.append({"category": category, "clue": clue, "answer": answer})
    return questions


# Function to read Wikipedia pages from the folder
def read_wiki_pages(folder_path):
    wiki_pages = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            title = file.readline().strip()[2:-2]  # Extract title from [[Title]] syntax
            content = file.read()
            wiki_pages.append({"title": title, "content": content})
    return wiki_pages


# Sample data paths
questions_file = 'data/questions.txt'
wiki_subset_folder = 'data/wiki-subset'

# Read questions and wiki pages
jeopardy_questions = read_questions(questions_file)
wiki_pages = read_wiki_pages(wiki_subset_folder)

# Indexing
schema = Schema(title=TEXT(stored=True), content=TEXT)
index = create_in("index_directory", schema)
writer = index.writer()

for page in wiki_pages:
    writer.add_document(title=page["title"], content=page["content"])

writer.commit()


# Retrieval
def search(query_text, category=None):
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(query_text)
        results = searcher.search(query, limit=1)

        if results:
            return results[0]["title"]


# Example usage
for question in jeopardy_questions:
    query_text = f"{question['clue']} {question.get('category', '')}"
    retrieved_title = search(query_text, category=question.get('category'))

    print(f"Jeopardy Clue: {question['clue']}")
    print(f"Actual Answer: {question['answer']}")
    print(f"Retrieved Title: {retrieved_title}")
    print("-----------")
