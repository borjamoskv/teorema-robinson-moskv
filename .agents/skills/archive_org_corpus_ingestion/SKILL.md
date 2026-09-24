<!-- C5-REAL EXERGY CERTIFIED -->
---
name: archive_org_corpus_ingestion
description: "Resolución sistemática de metadatos, manifiestos JSON y descarga directa de formatos derivados (OCR texto plano, HOCR, PDFs, EPUB) desde la API de Internet Archive (archive.org)."
---

# Archive.org Corpus Ingestion & Metadata Resolution Skill

Este skill establece el protocolo determinista para consultar, inspeccionar y descargar obras y fuentes bibliográficas alojadas en Internet Archive (`archive.org`), optimizando el consumo de ancho de banda y tiempo al evitar scraping HTML o renderizado de navegador.

---

## 1. Patrón Canónico de Endpoints

Para cualquier identificador de Archive.org (`{identifier}`):

| Propósito | Formato URL | Método |
| :--- | :--- | :--- |
| **API de Metadatos y Manifiesto** | `https://archive.org/metadata/{identifier}` | GET (HTTP / JSON) |
| **Descarga Directa de Archivo** | `https://archive.org/download/{identifier}/{filename}` | GET (HTTP Stream) |
| **Página Web Pública (UI)** | `https://archive.org/details/{identifier}` | Navegador (Sólo si se requiere interacción humana) |

---

## 2. Flujo de Trabajo Sistemático

### Paso 1: Obtención del Manifiesto de Archivos
Consultar directamente el endpoint JSON con `read_url_content` o `curl`:
```bash
https://archive.org/metadata/{identifier}
```

La respuesta JSON contiene:
- `metadata`: Título, creador, año, idioma, colecciones, etc.
- `files`: Array con todos los archivos disponibles, sus formatos, nombres (`name`), tamaños (`size`) y digests (`md5`, `sha1`, `crc32`).
- `server` y `workable_servers`: Servidores de almacenamiento físico activos.

### Paso 2: Selección del Formato Óptimo por Caso de Uso

Filtrar el array `files` según la necesidad de la investigación:

1. **Análisis Textual, Minería Semántica y Búsqueda de Citas:**
   - Buscar formato `DjVuTXT` (`name` terminando en `_djvu.txt`) o `OCR Search Text` (`_hocr_searchtext.txt.gz`).
   - *Ventaja:* Texto plano limpio, bajo peso (<1 MB), cero sobrecoste de parsing PDF/imágenes.

2. **Auditoría de Precisión OCR y Coordenadas de Página:**
   - Buscar formato `hOCR` (`_hocr.html` o `_chocr.html.gz`) o `Page Numbers JSON` (`_page_numbers.json`).
   - *Ventaja:* Permite localizar el número de página original y el nivel de confianza de cada token.

3. **Auditoría Estructural, Esteganográfica o de Objetos PDF:**
   - Buscar formato `Text PDF` o `original` (`.pdf`).
   - *Ventaja:* Inspección de árboles de objetos, metadatos XMP y flujos de compresión.

4. **Lectura Completa Estructurada:**
   - Buscar formato `EPUB` (`.epub`).

### Paso 3: Descarga Directa y Aislamiento de Entropía

Toda descarga debe enrutarse obligatoriamente a la drop zone de cuarentena `scratch/` para cumplir con el invariante de higiene de repositorio:

```bash
mkdir -p scratch/corpus/{identifier}
curl -L -o "scratch/corpus/{identifier}/{filename}" "https://archive.org/download/{identifier}/{filename}"
```

### Paso 4: Bypass de Restricciones de Préstamo (401/403) y Extracción Cero-Anergía

1. **Detección de Lending Library DRM:**
   - Si una petición de descarga devuelve `HTTP 401 Unauthorized` o `HTTP 403 Forbidden`, el ítem está bloqueado bajo préstamo temporal (`ACS Encrypted PDF`, identificadores prefijados con `bwb_*`).
   - El agente DEBE buscar inmediatamente identificadores alternativos abiertos (ej. variantes comunitarias `reclaimed`, ediciones facsímiles abiertas o mirrors independientes).

2. **Prioridad del Formato DjVuTXT (`_djvu.txt`):**
   - Antes de descargar PDFs masivos para extraer texto, verificar si existe `_djvu.txt` en el manifiesto JSON. Permite minería semántica inmediata con un tamaño menor a 1 MB y sin sobrecoste de parsing o OCR.

3. **Extracción Local Cero-Latencia (`pdftotext`):**
   - Cuando solo se disponga del PDF descargado (vectorizado o con capa OCR), ejecutar la extracción de texto con `pdftotext` (Poppler) en local a latencia cero y coste nulo:
     ```bash
     pdftotext ruta_documento.pdf ruta_destino.txt
     ```

4. **Fallback a Repositorios Universitarios Abiertos:**
   - Si la obra está bloqueada en Archive.org, consultar repositorios abiertos institucionales o académicos autorizados (ej. dominios `.edu` como UCSB Orfalea Center o archivos de fundaciones temáticas como *Principia Cybernetica*).

---

## 3. Ejemplo Práctico: Ingesta de "Caos y Orden" (1999)

- **Identifier:** `escohotado-a.-caos-y-orden-ocr-1999`
- **Manifiesto:** `https://archive.org/metadata/escohotado-a.-caos-y-orden-ocr-1999`
- **Texto Plano OCR:** `https://archive.org/download/escohotado-a.-caos-y-orden-ocr-1999/Escohotado,%20A.%20-%20Caos%20y%20orden%20[ocr]%20[1999]_djvu.txt`
- **Destino local:** `scratch/corpus/escohotado-a.-caos-y-orden-ocr-1999/caos_y_orden_ocr.txt`
