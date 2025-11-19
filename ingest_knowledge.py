"""
Knowledge Base Ingestion Script
Upload documents to the knowledge base from various file formats
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple
import logging
from knowledge_base import knowledge_base
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_text_file(file_path: str) -> str:
    """Read a plain text file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_pdf_file(file_path: str) -> str:
    """Read a PDF file"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return ""


def read_docx_file(file_path: str) -> str:
    """Read a DOCX file"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error reading DOCX {file_path}: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into chunks with overlap

    Args:
        text: Text to chunk
        chunk_size: Size of each chunk (default from settings)
        overlap: Overlap between chunks (default from settings)

    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def ingest_file(file_path: str) -> Tuple[int, str]:
    """
    Ingest a single file into the knowledge base

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (number of chunks added, file_path)
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return 0, str(file_path)

    # Read file based on extension
    extension = file_path.suffix.lower()

    if extension == '.txt':
        text = read_text_file(str(file_path))
    elif extension == '.pdf':
        text = read_pdf_file(str(file_path))
    elif extension == '.docx':
        text = read_docx_file(str(file_path))
    else:
        logger.warning(f"Unsupported file type: {extension}")
        return 0, str(file_path)

    if not text.strip():
        logger.warning(f"No text extracted from {file_path}")
        return 0, str(file_path)

    # Chunk the text
    chunks = chunk_text(text)

    # Create metadata for each chunk
    metadata = [{"source": str(file_path), "chunk": i} for i in range(len(chunks))]

    # Add to knowledge base
    knowledge_base.add_documents(chunks, metadata)

    logger.info(f"Ingested {file_path}: {len(chunks)} chunks")
    return len(chunks), str(file_path)


def ingest_directory(directory_path: str) -> None:
    """
    Ingest all supported files from a directory

    Args:
        directory_path: Path to the directory
    """
    directory = Path(directory_path)

    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return

    supported_extensions = ['.txt', '.pdf', '.docx']
    files = []

    for ext in supported_extensions:
        files.extend(directory.glob(f"**/*{ext}"))

    if not files:
        logger.warning(f"No supported files found in {directory_path}")
        return

    total_chunks = 0
    for file_path in files:
        chunks, _ = ingest_file(str(file_path))
        total_chunks += chunks

    logger.info(f"Total: {total_chunks} chunks from {len(files)} files")


def ingest_text(text: str, source_name: str = "manual") -> int:
    """
    Ingest raw text into the knowledge base

    Args:
        text: Text to ingest
        source_name: Name to identify the source

    Returns:
        Number of chunks added
    """
    chunks = chunk_text(text)
    metadata = [{"source": source_name, "chunk": i} for i in range(len(chunks))]
    knowledge_base.add_documents(chunks, metadata)

    logger.info(f"Ingested text: {len(chunks)} chunks")
    return len(chunks)


def main():
    """Main CLI for ingestion"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ingest_knowledge.py <file_path>          # Ingest a single file")
        print("  python ingest_knowledge.py --dir <directory>    # Ingest all files in directory")
        print("  python ingest_knowledge.py --text <text>        # Ingest raw text")
        print("  python ingest_knowledge.py --clear              # Clear knowledge base")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--clear":
        knowledge_base.clear()
        print("Knowledge base cleared")
    elif command == "--dir" and len(sys.argv) > 2:
        ingest_directory(sys.argv[2])
        print(f"Knowledge base now has {knowledge_base.count()} documents")
    elif command == "--text" and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        chunks = ingest_text(text)
        print(f"Added {chunks} chunks. Knowledge base now has {knowledge_base.count()} documents")
    else:
        # Assume it's a file path
        chunks, path = ingest_file(command)
        print(f"Added {chunks} chunks from {path}")
        print(f"Knowledge base now has {knowledge_base.count()} documents")


if __name__ == "__main__":
    main()
