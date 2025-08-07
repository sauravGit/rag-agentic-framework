import os
from unittest.mock import MagicMock, patch
from mvp.document_processor.processor import DocumentProcessor

@patch('mvp.document_processor.processor.DocumentProcessor._get_embedding_model')
def test_process_directory(mock_get_embedding_model):
    # Create a mock VectorDBClient
    mock_vector_db_client = MagicMock()

    # Create a DocumentProcessor with the mock client
    processor = DocumentProcessor(mock_vector_db_client)

    # Create a dummy directory and a dummy file
    dummy_dir = "dummy_test_dir"
    os.makedirs(dummy_dir, exist_ok=True)
    with open(os.path.join(dummy_dir, "test.txt"), "w") as f:
        f.write("This is a test document.")

    # Process the directory
    processor.process_directory(dummy_dir, "test_index")

    # Check that the index_document method was called on the mock client
    mock_vector_db_client.index_document.assert_called()

    # Clean up the dummy directory and file
    os.remove(os.path.join(dummy_dir, "test.txt"))
    os.rmdir(dummy_dir)
