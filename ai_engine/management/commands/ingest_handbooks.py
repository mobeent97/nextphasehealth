import os
from django.core.management.base import BaseCommand
from django.conf import settings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ai_engine.vector_service import VectorService

class Command(BaseCommand):
    help = 'Ingests PDF handbooks from the handbooks directory into the vector store.'

    def handle(self, *args, **options):
        handbooks_dir = os.path.join(settings.BASE_DIR, 'handbooks')
        
        if not os.path.exists(handbooks_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {handbooks_dir}'))
            return

        vector_service = VectorService()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        
        pdf_files = [f for f in os.listdir(handbooks_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.stdout.write(self.style.WARNING('No PDF files found in handbooks directory.'))
            return

        for filename in pdf_files:
            file_path = os.path.join(handbooks_dir, filename)
            self.stdout.write(f'Processing {filename}...')
            
            try:
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                
                # Metadata Strategy
                region = 'Unknown'
                if 'Ontario' in filename:
                    region = 'Ontario'
                elif 'USA' in filename:
                    region = 'USA'
                
                # Update metadata for all documents from this file
                for doc in documents:
                    doc.metadata['region'] = region
                    doc.metadata['source'] = filename

                chunks = text_splitter.split_documents(documents)
                
                vector_service.add_documents(chunks)
                
                self.stdout.write(self.style.SUCCESS(f'Successfully added {len(chunks)} chunks from {filename} (Region: {region})'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to process {filename}: {e}'))
