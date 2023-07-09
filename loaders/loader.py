import os
import glob
from dotenv import load_dotenv
from multiprocessing import Pool
from typing import List
from tqdm import tqdm

from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from constants.constants import CHROMA_SETTINGS

load_dotenv() # load environment variables

# configure environment variables
persist_directory = os.environ.get('PERSIST_DIRECTORY')
source_directory = os.environ.get('SOURCE_DIRECTORY', 'load_data')
embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME')
chunk_size = 500
chunk_overlap = 50

class emailLoader(UnstructuredEmailLoader):
  """fallback to text/plain when default does not work"""

  def load(self) -> List[Document]:
    try:
      try:
        doc = UnstructuredEmailLoader.load(self)
      except ValueError as e:
        if 'text/html content not found in email' in str(e):
          # attempt plain text
          self.unstructured_kwargs["content_source"]="text/plain"
          doc = UnstructuredEmailLoader.load(self)
        else:
          raise
    except Exception as e:
      # append file_path to exception message
      raise type(e)(f"❗️ {self.file_path}: {e}") from e
    return doc

LOADER_MAPPING = {
    "csv": (CSVLoader,{}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".eml": (emailLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # add loaders to support additional file types
}

def load_single_document(file_path: str) -> List[Document]:
  """load a single document from file_path"""
  ext = "." + file_path.rsplit(".", 1)[-1]
  if ext in LOADER_MAPPING:
    loader_class, loader_args = LOADER_MAPPING[ext]
    loader = loader_class(file_path, **loader_args)
    return loader.load()

  raise ValueError(f"❗️ Unsupported file extension: {ext}")

def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[Document]:
  """
  load all documents from the source_dir
  """
  all_files = []
  for ext in LOADER_MAPPING:
    all_files.extend(
      glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
    )

  filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]

  with Pool(processes=os.cpu_count()) as pool:
    results = []
    with tqdm(total=len(filtered_files), desc="Loading documents", ncols=80) as progress:
      for i, docs in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
        results.extend(docs)
        progress.update()
  return results

def process_documents(ignored_files: List[str] = []) -> List[Document]:
  """
  load docs and split in to chunks
  """
  print(f"🛻 Loading documents from {source_directory}")
  documents = load_documents(source_directory, ignored_files)
  if not documents:
    raise ValueError("No documents found")
    exit(0)

  print(f"🚛 Loaded {len(documents)} documents from {source_directory}")
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap) # chunking params
  texts = text_splitter.split_documents(documents)
  print(f"🔧 Split into{len(texts)} chunks based on max length of {chunk_size} tokens")
  return texts

def does_vectorstore_exist(persist_directory) -> bool:
  """
  check if vectorstore exists
  """
  if os.path.exists(os.path.join(persist_directory, 'index')):
    if os.path.exists(os.path.join(persist_directory, 'chroma-collections.parquet')) and os.path.exists(os.path.join(persist_directory, 'chroma-embeddings.parquet')):
      list_index_files = glob.glob(os.path.join(persist_directory, 'index/*.bin'))
      list_index_files += glob.glob(os.path.join(persist_directory, 'index/*.pkl'))

      # at least 3 documents are required to build a vectorstore TODO:
      if len(list_index_files) > 3:
        return True
  return False

def main():
  embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

  if does_vectorstore_exist(persist_directory):
    print(f"Appending to existing vectorstore in {persist_directory}")
    # update local vectorstore
    db = Chroma(persist_directory=persist_directory, embeddings=embeddings, client_settings=CHROMA_SETTINGS)
    collection = db.get()
    texts = process_documents([metadata['source'] for metadata in collection['metadatas']])
    print(f"🚚 Please wait while embeddings are created...")
    db.add_documents(texts)
  else:
    print(f"✨ Creating new vectorstore in {persist_directory}")
    texts = process_documents()
    print(f"🛻 Please wait while new embeddings are created...")
    db = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory, client_settings=CHROMA_SETTINGS)
  db.persist()
  db = None

  print(f"📣 Document load complete! You can now run gpt-engine to query the vectorstore for you document content")

if __name__ == "__main__":
  main()
