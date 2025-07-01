from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from datetime import datetime
import pandas as pd
import os
import glob

def export_mongo_to_elasticsearch():
    """Exporta directamente desde MongoDB a Elasticsearch usando bulk operations"""
    
    # Conectar a MongoDB
    try:
        mongo_client = MongoClient('mongodb://admin:admin123@mongo:27017/')
        db = mongo_client['trafico_rm']
        mongo_client.admin.command('ping')
    except Exception as e:
        return False
    
    # Conectar a Elasticsearch
    try:
        es = Elasticsearch("http://elasticsearch:9200")
        if not es.ping():
            raise Exception("No se pudo conectar a Elasticsearch")
    except Exception as e:
        return False
    
    # Función auxiliar para preparar documentos
    def prepare_docs_for_bulk(collection, index_name):
        """Prepara documentos para bulk insert"""
        for doc in collection.find({}):
            # Extraer el _id y eliminarlo del documento
            doc_id = str(doc.pop('_id'))
            
            yield {
                "_index": index_name,
                "_id": doc_id,
                "_source": doc
            }
    
    # Exportar alertas
    try:
        alertas_collection = db['alertas']
        
        # Usar bulk helper
        bulk(
            es,
            prepare_docs_for_bulk(alertas_collection, "alertas"),
            chunk_size=1000,  # Procesar en lotes de 1000
            request_timeout=60
        )
        
    except Exception as e:
        pass
    
    # Exportar atascos
    try:
        atascos_collection = db['atascos']
        
        # Usar bulk helper
        bulk(
            es,
            prepare_docs_for_bulk(atascos_collection, "atascos"),
            chunk_size=1000,  # Procesar en lotes de 1000
            request_timeout=60
        )
        
    except Exception as e:
        pass
    
    # Cerrar conexiones
    mongo_client.close()
    print("Exportación de MongoDB a Elasticsearch completada.")
    return True

def export_csv_to_elasticsearch():
    """Exporta archivos CSV procesados a Elasticsearch"""
    
    # Conectar a Elasticsearch
    try:
        es = Elasticsearch("http://elasticsearch:9200")
        if not es.ping():
            raise Exception("No se pudo conectar a Elasticsearch")
    except Exception as e:
        return False
    
    # Encontrar la carpeta de ejecución más reciente
    try:
        results_path = "/app/input"  # Carpeta montada desde m8-processing/results
        
        # Buscar carpetas que empiecen con "ejecucion_"
        ejecucion_folders = glob.glob(os.path.join(results_path, "ejecucion_*"))
        
        if not ejecucion_folders:
            return False
        
        # Ordenar por nombre (incluye timestamp, así que funciona)
        latest_folder = max(ejecucion_folders)
        
    except Exception as e:
        return False
    
    # Buscar todos los archivos CSV en la carpeta
    try:
        csv_files = glob.glob(os.path.join(latest_folder, "*.csv"))
        
        if not csv_files:
            return False
        
    except Exception as e:
        return False
    
    # Función para preparar documentos CSV para bulk
    def prepare_csv_for_bulk(csv_file_path):
        """Convierte CSV a documentos para Elasticsearch"""
        try:
            # Leer CSV
            df = pd.read_csv(csv_file_path)
            
            # Obtener nombre del archivo sin extensión
            file_name = os.path.splitext(os.path.basename(csv_file_path))[0]
            
            # Crear índice específico para cada tipo de análisis
            index_name = f"analisis_{file_name}"
            
            # Convertir cada fila a documento
            for idx, row in df.iterrows():
                doc = row.to_dict()
                
                # Agregar metadatos
                doc['archivo_origen'] = file_name
                doc['fecha_procesamiento'] = datetime.now().isoformat()
                doc['fila_numero'] = idx + 1
                
                # Usar combinación de archivo y fila como ID único
                doc_id = f"{file_name}_{idx}"
                
                yield {
                    "_index": index_name,
                    "_id": doc_id,
                    "_source": doc
                }
                
        except Exception as e:
            return
    
    # Procesar cada archivo CSV
    for csv_file in csv_files:
        try:
            # Usar bulk helper
            bulk(
                es,
                prepare_csv_for_bulk(csv_file),
                chunk_size=1000,
                request_timeout=60
            )
            
        except Exception as e:
            pass
    
    print("Exportación de CSV a Elasticsearch completada.")
    
    return True

if __name__ == "__main__":
    # Va a mongo y exporta a elasticsearch
    export_mongo_to_elasticsearch()
    
    # Va a los csv de insights y exporta a elasticsearch
    export_csv_to_elasticsearch()