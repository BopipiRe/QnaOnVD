import os

from modules import resource_path
from modules.service import VectorService

if __name__ == '__main__':
    service = VectorService()
    for filename in os.listdir(resource_path('doc')):
        if filename.endswith('.docx') or filename.endswith('.pdf'):
            service.generate_vector_store(os.path.join(resource_path('doc'), filename))