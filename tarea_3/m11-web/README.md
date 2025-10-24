# M11-Web - Dashboard de Visualización

Este módulo proporciona una interfaz web para visualizar los resultados del análisis de datos de tráfico procesados por el pipeline.

## Características

- **Dashboard interactivo**: Visualiza métricas y gráficos de los datos de tráfico
- **Detección automática**: Encuentra automáticamente la ejecución más reciente
- **Gráficos responsivos**: Utiliza Chart.js para crear visualizaciones interactivas
- **Métricas clave**: Muestra resúmenes de atascos, alertas, ciudades y horas pico

## Visualizaciones Incluidas

1. **Métricas principales**: Total de atascos, alertas, ciudades afectadas y hora pico
2. **Atascos por ciudad**: Gráfico de barras con las ciudades con más atascos
3. **Tipos de alertas**: Gráfico de dona mostrando la distribución de tipos de alertas
4. **Alertas por hora**: Gráfico de líneas mostrando la actividad durante el día
5. **Comunas con más alertas**: Gráfico de barras horizontales
6. **Calles con más accidentes**: Lista rankeada de las calles más peligrosas
7. **Atascos más largos**: Lista de los atascos de mayor longitud

## Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Chart.js
- **Procesamiento de datos**: Pandas
- **Contenedorización**: Docker

## Estructura de Archivos

```
m11-web/
├── app.py                 # Aplicación Flask principal
├── Dockerfile            # Configuración del contenedor
├── requirements.txt      # Dependencias Python
├── docker-compose.yml    # Configuración específica del módulo
└── templates/
    ├── base.html         # Template base
    ├── dashboard.html    # Dashboard principal
    └── error.html        # Página de error
```

## Configuración

### Variables de Entorno

- `FLASK_ENV`: Entorno de Flask (production/development)

### Puertos

- **8080**: Puerto web para acceder al dashboard

### Volúmenes

- `../m8-processing/results:/app/input:ro`: Acceso de solo lectura a los resultados procesados

## Uso

1. El dashboard se ejecuta automáticamente después de que el módulo m8-processing complete su análisis
2. Accede al dashboard en: `http://localhost:8080`
3. La aplicación detecta automáticamente la ejecución más reciente y carga los datos

## API Endpoints

- `GET /`: Dashboard principal
- `GET /api/data/<data_type>`: API para obtener datos específicos
- `GET /health`: Endpoint de salud del servicio

## Datos Soportados

El dashboard puede visualizar los siguientes tipos de datos (archivos CSV):

- `atascos_por_ciudad.csv`
- `horas_pico.csv`
- `tipos_alerta_frecuencia.csv`
- `atascos_largos.csv`
- `calles_con_mas_accidentes.csv`
- `calles_con_mas_alertas.csv`
- `comunas_con_mas_accidentes.csv`
- `comunas_con_mas_alertas.csv`

## Integración con el Pipeline

Este módulo se integra en el pipeline de la siguiente manera:

1. **Dependencias**: Espera a que `m8-processing` complete el análisis
2. **Datos**: Lee los archivos CSV generados por m8-processing
3. **Visualización**: Presenta los datos de manera intuitiva y accesible
4. **Acceso**: Proporciona una interfaz web para stakeholders y usuarios finales

## Desarrollo

Para desarrollo local:

```bash
cd m11-web
pip install -r requirements.txt
python app.py
```

El servidor se ejecutará en `http://localhost:5000` en modo desarrollo.