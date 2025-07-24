FROM python:3.10.14-slim-bookworm

# Install system dependencies for geo packages and upgrade packages to fix vulnerabilities
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    build-essential \
    postgresql-client \
    wget \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set Python path and Django settings
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=config.settings

# Skip collectstatic during build (will run at startup)
# RUN python manage.py collectstatic --noinput || true

# Create a more explicit start script
RUN echo '#!/bin/bash\n\
set -e\n\
cd /app\n\
echo "=== Running migrations ==="\n\
python manage.py migrate --noinput || echo "Migration failed but continuing"\n\
echo "=== Collecting static files ==="\n\
python manage.py collectstatic --noinput || echo "Collectstatic failed but continuing"\n\
echo "=== Checking for initial data ==="\n\
if [ $(python manage.py shell -c "from fires.models import Wildfire; print(Wildfire.objects.count())") -eq 0 ]; then\n\
    echo "=== No fires found, importing initial data ==="\n\
    python manage.py fetch_firms_data --days 3 || echo "Fire import failed"\n\
fi\n\
echo "=== Checking for wells data ==="\n\
if [ $(python manage.py shell -c "from fires.models import AbandonedWell; print(AbandonedWell.objects.count())") -eq 0 ]; then\n\
    echo "=== No wells found, importing initial data ==="\n\
    echo "Downloading wells shapefile from AER..."\n\
    wget -q https://www.aer.ca/data/wells/ABNDWells_SHP.zip -O /tmp/ABNDWells_SHP.zip || echo "Download failed"\n\
    echo "Download complete, importing wells..."\n\
    python manage.py import_abandoned_wells /tmp/ABNDWells_SHP.zip || echo "Wells import failed"\n\
    rm -f /tmp/ABNDWells_SHP.zip\n\
    echo "Wells import complete!"\n\
fi\n\
echo "=== Starting Gunicorn ==="\n\
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --log-level info' > /app/start.sh

RUN chmod +x /app/start.sh

# Explicitly set the command
CMD ["/bin/bash", "/app/start.sh"]