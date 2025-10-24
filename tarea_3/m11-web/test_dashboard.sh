#!/bin/bash

echo "🚀 Iniciando test del módulo m11-web..."

# Verificar que existe al menos una ejecución de resultados
if [ ! -d "m8-processing/results" ] || [ -z "$(ls -A m8-processing/results 2>/dev/null)" ]; then
    echo "❌ Error: No se encontraron resultados en m8-processing/results"
    echo "   Ejecuta primero el pipeline completo para generar datos"
    exit 1
fi

echo "✅ Encontrados datos de resultados en m8-processing/results"

# Obtener la ejecución más reciente
LATEST_EXECUTION=$(ls -1t m8-processing/results/ | head -n 1)
echo "📊 Ejecución más reciente: $LATEST_EXECUTION"

# Listar algunos archivos CSV principales para verificar
echo "📁 Archivos CSV disponibles:"
ls -la "m8-processing/results/$LATEST_EXECUTION"/*.csv 2>/dev/null | head -5

echo ""
echo "🌐 Ejecutando el dashboard web..."
echo "   Accede en: http://localhost:8080"
echo "   Presiona Ctrl+C para detener"

# Ejecutar el contenedor
docker run --rm \
    -v $(pwd)/m8-processing/results:/app/input:ro \
    -p 8080:5000 \
    m11-web