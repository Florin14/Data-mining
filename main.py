import datetime
import os

from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser


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


# Indexing
schema = Schema(title=TEXT(stored=True), content=TEXT)
index = create_in("index_directory", schema)
writer = index.writer()


# Function to read Wikipedia pages from the folder

def read_wiki_pages(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Iterate over lines to extract title-content pairs
        i = 0
        while i < len(lines):
            # Find the line with the title
            while i < len(lines) and not lines[i].strip().startswith("[["):
                i += 1

            if i < len(lines):
                # Extract title from [[Title]] syntax
                title_start = lines[i].find('[[') + 2
                title_end = lines[i].find(']]', title_start)
                title = lines[i][title_start:title_end]

                # Move to the next line after the title
                i += 1

                # Extract content until the next title or end of file
                content_lines = []
                while i < len(lines) and not lines[i].strip().startswith("[["):
                    content_lines.append(lines[i].strip())
                    i += 1

                # Join content lines and store in the dictionary
                content = " ".join(content_lines)
                writer.add_document(title=title, content=content)
    writer.commit()


# Sample data paths
questions_file = 'data/questions.txt'
wiki_subset_folder = 'data/wiki-subset'

startTime = datetime.datetime.now()
# Read questions and wiki pages
jeopardy_questions = read_questions(questions_file)
wiki_pages = read_wiki_pages(wiki_subset_folder)


#we've chosen It directly measures the accuracy of the system by checking if the correct answer is ranked first in the list of retrieved results, which aligns well with the Jeopardy task where the first answer matters the most.
def calculate_precision_at_1(actual_answer, retrieved_title):
    return 1 if actual_answer == retrieved_title else 0


total_questions = len(jeopardy_questions)
total_correct = 0


# Retrieval
def search(query_text, category=None):
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(query_text)
        results = searcher.search(query, limit=1)

        if results:
            return results[0]["title"]


titles_not_retrieved = 0
# Example usage
for question in jeopardy_questions:
    query_text = f"{question['clue']} {question.get('category', '')}"
    retrieved_title = search(query_text, category=question.get('category'))

    print(f"Jeopardy Clue: {question['clue']}")
    print(f"Actual Answer: {question['answer']}")
    print(f"Retrieved Title: {retrieved_title}")

    precision_at_1 = calculate_precision_at_1(question['answer'], retrieved_title)
    total_correct += precision_at_1

    titles_not_retrieved += 1 if retrieved_title is None else 0
    print("-----------")

precision_at_1_score = total_correct / total_questions

print(f'\ntime: {datetime.datetime.now() - startTime}')
print(f'\nnumber of titles not retrieved: {titles_not_retrieved}')

# Report the result
print(f"\nPrecision at 1 (P@1): {precision_at_1_score}")
