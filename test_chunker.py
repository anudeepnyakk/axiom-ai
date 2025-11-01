import unittest
from axiom.core.basic_chunker import BasicChunker
from axiom.core.interfaces import DocumentChunk
from axiom.config.models import DocumentProcessingConfig

class TestBasicChunker(unittest.TestCase):
    def test_simple_chunking(self):
        """
        Tests that a simple text is chunked correctly without overlap.
        """
        config = DocumentProcessingConfig(chunk_size=50, chunk_overlap=0)
        chunker = BasicChunker(config)
        text = "This is a simple test sentence for the basic chunker logic."
        # The chunker expects a DocumentChunk with the full text.
        document_chunk = DocumentChunk(text=text, metadata={'source_file_path': "test_doc.txt"})
        chunks = chunker.chunk(document_chunk, "dummy_hash_1")
        
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].text, "This is a simple test sentence for the basic chunk")
        self.assertEqual(chunks[1].text, "er logic.")
        self.assertEqual(chunks[0].metadata['source_file_path'], "test_doc.txt")

    def test_chunking_with_overlap(self):
        """
        Tests that chunking with overlap works as expected.
        """
        config = DocumentProcessingConfig(chunk_size=100, chunk_overlap=20)
        chunker = BasicChunker(config)
        text = "This is a longer sentence designed to test the overlapping functionality of the chunker. The overlap should carry over some words to the next chunk for context."
        document_chunk = DocumentChunk(text=text, metadata={'source_file_path': "test_doc_overlap.txt"})
        chunks = chunker.chunk(document_chunk, "dummy_hash_2")

        self.assertEqual(len(chunks), 2)
        # The overlap is character-based, so we find the start of the second chunk
        # and see what follows.
        overlap_point = text[100-20:100]
        self.assertTrue(chunks[1].text.startswith(overlap_point))


if __name__ == '__main__':
    unittest.main()
