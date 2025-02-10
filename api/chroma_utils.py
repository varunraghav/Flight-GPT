from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List
from langchain_core.documents import Document
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
llama_cloud_key = os.getenv("LLAMA_CLOUD_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

# Initialize text splitter and embedding function
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embedding_function = OpenAIEmbeddings(api_key=openai_key)

# Initialize Chroma vector store
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]

        urls = [url if url.startswith("http") else "https://" + url for url in urls]
        docs = []
        failed_urls = []
        airline_name = os.path.splitext(file_path)[0]
        for i, url in enumerate(urls, start=1):
            print(f"[{i}/{len(urls)}] Fetching: {url}")
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    raw_text = response.text
                    # Placeholder for parsing logic
                    title, source_url, body_text = "Sample Title", url, raw_text

                    if not body_text.strip():
                        print(f"  -> No body content found. Skipping URL.")
                        failed_urls.append(url)
                        continue

                    # Add metadata
                    metadata = {
                        "airline": airline_name,
                        "title": title or "No Title",
                        "source_url": source_url or "No Source URL",
                    }

                    # Create Document using LangChain
                    document = Document(
                        page_content=body_text,
                        metadata=metadata
                    )

                    docs.append(document)
                else:
                    print(f"  -> Failed with status code {response.status_code}")
                    failed_urls.append(url)

            except Exception as e:
                print(f"  -> Error fetching URL: {e}")
                failed_urls.append(url)
                continue


    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    return text_splitter.split_documents(docs)

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        splits = load_and_split_document(file_path)

        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id

        vectorstore.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False

def delete_doc_from_chroma(file_id: int):
    try:
        docs = vectorstore.get(where={"file_id": file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")

        vectorstore._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")

        return True
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
