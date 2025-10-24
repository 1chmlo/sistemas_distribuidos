from flask import Flask, render_template, jsonify
import pandas as pd
import os
import glob
from datetime import datetime
import json

app = Flask(__name__)

def get_latest_execution():
    """Encuentra la ejecución más reciente en los resultados"""
    results_path = "/app/input"
    if not os.path.exists(results_path):
        return None
    
    execution_dirs = glob.glob(os.path.join(results_path, "ejecucion_*"))
    if not execution_dirs:
        return None
    
    # Ordenar por nombre (que incluye timestamp) y tomar el más reciente
    execution_dirs.sort()
    return execution_dirs[-1]

def load_csv_data(csv_path):
    """Carga un archivo CSV y lo convierte a formato JSON para gráficos"""
    try:
        if not os.path.exists(csv_path):
            return None
        df = pd.read_csv(csv_path)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading {csv_path}: {e}")
        return None

def get_execution_info(execution_path):
    """Extrae información de la ejecución desde el nombre del directorio"""
    execution_name = os.path.basename(execution_path)
    # Formato: ejecucion_YYYYMMDD_HHMMSS
    try:
        date_str = execution_name.replace('ejecucion_', '')
        date_part = date_str[:8]  # YYYYMMDD
        time_part = date_str[9:15]  # HHMMSS
        
        formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
        formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
        
        return {
            'name': execution_name,
            'date': formatted_date,
            'time': formatted_time,
            'datetime': f"{formatted_date} {formatted_time}"
        }
    except:
        return {
            'name': execution_name,
            'date': 'Desconocida',
            'time': 'Desconocida',
            'datetime': 'Desconocida'
        }

@app.route('/')
def dashboard():
    """Página principal del dashboard"""
    latest_execution = get_latest_execution()
    
    if not latest_execution:
        return render_template('error.html', message="No se encontraron ejecuciones de resultados")
    
    execution_info = get_execution_info(latest_execution)
    
    # Cargar datos de los CSV principales
    data = {}
    csv_files = {
        'atascos_ciudad': 'atascos_por_ciudad.csv',
        'horas_pico': 'horas_pico.csv',
        'tipos_alerta': 'tipos_alerta_frecuencia.csv',
        'atascos_largos': 'atascos_largos.csv',
        'calles_accidentes': 'calles_con_mas_accidentes.csv',
        'calles_alertas': 'calles_con_mas_alertas.csv',
        'comunas_accidentes': 'comunas_con_mas_accidentes.csv',
        'comunas_alertas': 'comunas_con_mas_alertas.csv'
    }
    
    for key, filename in csv_files.items():
        csv_path = os.path.join(latest_execution, filename)
        csv_data = load_csv_data(csv_path)
        if csv_data:
            # Procesar datos específicos según el tipo
            if key == 'atascos_largos':
                # Para atascos largos, tomar solo los top 20 más largos
                try:
                    csv_data = sorted(csv_data, key=lambda x: int(x.get('length', 0)), reverse=True)[:20]
                except (ValueError, TypeError):
                    csv_data = csv_data[:20]  # Si hay error en la conversión, tomar los primeros 20
            elif key == 'calles_accidentes':
                # Para calles con accidentes, tomar solo top 15
                csv_data = csv_data[:15]
            elif key == 'comunas_alertas':
                # Para comunas con alertas, tomar solo top 15
                csv_data = csv_data[:15]
        data[key] = csv_data
    
    return render_template('dashboard.html', 
                         execution_info=execution_info,
                         data=data)

@app.route('/api/data/<data_type>')
def api_data(data_type):
    """API endpoint para obtener datos específicos"""
    latest_execution = get_latest_execution()
    
    if not latest_execution:
        return jsonify({'error': 'No execution found'}), 404
    
    csv_mapping = {
        'atascos_ciudad': 'atascos_por_ciudad.csv',
        'horas_pico': 'horas_pico.csv',
        'tipos_alerta': 'tipos_alerta_frecuencia.csv',
        'atascos_largos': 'atascos_largos.csv',
        'calles_accidentes': 'calles_con_mas_accidentes.csv',
        'calles_alertas': 'calles_con_mas_alertas.csv',
        'comunas_accidentes': 'comunas_con_mas_accidentes.csv',
        'comunas_alertas': 'comunas_con_mas_alertas.csv'
    }
    
    if data_type not in csv_mapping:
        return jsonify({'error': 'Invalid data type'}), 400
    
    csv_path = os.path.join(latest_execution, csv_mapping[data_type])
    data = load_csv_data(csv_path)
    
    if data is None:
        return jsonify({'error': 'Data not found'}), 404
    
    return jsonify(data)

@app.route('/health')
def health():
    """Endpoint de salud para verificar que el servicio está funcionando"""
    return jsonify({'status': 'healthy', 'service': 'm11-web'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)