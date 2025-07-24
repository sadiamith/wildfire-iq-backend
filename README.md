# 🔥 Alberta Wildfire & Abandoned Wells Tracker - Backend

A comprehensive Django REST API that monitors active wildfires and tracks abandoned oil & gas wells in Alberta, Canada. This system provides real-time fire detection data from NASA FIRMS and correlates it with the locations of 238,158 abandoned wells to assess environmental risks.

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2.11-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Railway](https://img.shields.io/badge/Deployed%20on-Railway-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **Real-time Wildfire Tracking**: Integrates with NASA FIRMS API to fetch active fire data
- **Abandoned Wells Database**: Comprehensive database of 238,158 abandoned oil & gas wells in Alberta
- **Risk Assessment**: Predictive modeling to assess fire risk based on proximity to abandoned wells
- **Automated Data Updates**: Celery-based scheduled tasks for regular data synchronization
- **RESTful API**: Clean, well-documented API endpoints for frontend consumption
- **Geospatial Queries**: Efficient spatial queries for wells within fire proximity
- **Statistical Analysis**: Real-time statistics on fires and wells by region, type, and licensee

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                     │
│   Next.js Frontend  │────▶│   Django Backend    │
│   (Vercel)          │     │   (Railway)         │
│                     │     │                     │
└─────────────────────┘     └──────────┬──────────┘
                                       │
                            ┌──────────┴──────────┐
                            │                     │
                    ┌───────▼────────┐   ┌───────▼────────┐
                    │  PostgreSQL    │   │  Redis         │
                    │  Database      │   │  (Celery)      │
                    └────────────────┘   └────────────────┘
                            │
                    ┌───────┴────────────────────┐
                    │                            │
            ┌───────▼────────┐          ┌───────▼────────┐
            │  NASA FIRMS    │          │  Alberta Energy │
            │  API           │          │  Regulator Data │
            └────────────────┘          └────────────────┘
```

## 🚀 Tech Stack

- **Framework**: Django 4.2.11 + Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Task Queue**: Celery + Redis
- **Geospatial**: GeoPandas, Shapely, PyProj
- **Deployment**: Railway (Backend), Vercel (Frontend)
- **CORS**: django-cors-headers
- **Environment**: python-decouple

## 📍 API Endpoints

### Wildfire Endpoints
```
GET /api/v1/fires/active/              # List all active fires
GET /api/v1/fires/historical/          # Historical fire data
GET /api/v1/fires/<id>/                # Fire details
GET /api/v1/stats/today/               # Today's statistics
POST /api/v1/predict-risk/             # Risk prediction
```

### Abandoned Wells Endpoints
```
GET /api/v1/energy-wells/              # List wells (with bounds filtering)
GET /api/v1/energy-wells/stats/        # Wells statistics
GET /api/v1/energy-wells/clusters/     # Clustered view for map
```

### Example Responses

#### Active Fires Response
```json
[
  {
    "id": 1,
    "unique_id": "FIRMS-2025-07-23-55.546--112.78",
    "latitude": 55.546,
    "longitude": -112.78,
    "bright_ti4": 317.8,
    "confidence": "nominal",
    "fire_size": 25.4,
    "status": "ACTIVE",
    "detection_time": "2025-07-23T12:00:00Z"
  }
]
```

#### Wells Statistics Response
```json
{
  "total_wells": 238158,
  "wells_in_view": 0,
  "top_licensees": [
    {
      "licensee": "CANADIAN NATURAL RESOURCES",
      "count": 45231
    }
  ],
  "wells_by_type": {
    "Oil": 145234,
    "Gas": 89234,
    "Other": 3690
  },
  "last_updated": "2025-07-23T17:51:08.451610Z"
}
```

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 15+ (for production)
- Redis (for Celery)
- GDAL libraries (for geospatial operations)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/wildfire-iq-backend.git
cd wildfire-iq-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install system dependencies** (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev libgeos-dev libproj-dev
```

4. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**
```bash
# Create .env file
cat > .env << EOL
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FIRMS_API_KEY=your-nasa-firms-api-key
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
EOL
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Import initial data**
```bash
# Fetch fire data
python manage.py fetch_firms_data --days 7

# Import abandoned wells (download shapefile first)
wget https://www.aer.ca/data/wells/ABNDWells_SHP.zip
python manage.py import_abandoned_wells ABNDWells_SHP.zip
```

8. **Run development server**
```bash
python manage.py runserver
```

## 🌍 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Yes |
| `FIRMS_API_KEY` | NASA FIRMS API key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes (production) |
| `REDIS_URL` | Redis connection string | Yes (for Celery) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed origins | Yes |

## 📊 Data Sources

### NASA FIRMS (Fire Information for Resource Management System)
- **API**: https://firms.modaps.eosdis.nasa.gov/api/
- **Update Frequency**: Near real-time (within 3 hours of satellite observation)
- **Coverage**: MODIS and VIIRS satellite data
- **Documentation**: [FIRMS API Documentation](https://firms.modaps.eosdis.nasa.gov/api/area/)

### Alberta Energy Regulator - Abandoned Wells
- **Source**: [AER Abandoned Wells Dataset](https://www.aer.ca/data/wells/ABNDWells_SHP.zip)
- **Format**: Shapefile (.shp)
- **Records**: 238,158 abandoned wells
- **Fields**: Well ID, Licensee, Location, Type, Status, etc.

## 🚀 Deployment

### Railway Deployment

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login and initialize**
```bash
railway login
railway init
```

3. **Set environment variables**
```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
railway variables set FIRMS_API_KEY=your-api-key
```

4. **Deploy**
```bash
railway up
```

### Dockerfile Configuration
The project includes a production-ready Dockerfile that:
- Installs GDAL and geospatial dependencies
- Configures PostgreSQL client
- Runs migrations on startup
- Imports initial data if database is empty
- Starts Gunicorn with optimal settings

## 📈 Performance Considerations

- **Database Indexing**: Spatial indexes on latitude/longitude fields for efficient geospatial queries
- **Pagination**: API responses are paginated to handle large datasets
- **Caching**: Consider implementing Redis caching for frequently accessed endpoints
- **Connection Pooling**: PostgreSQL connection pooling for production
- **Async Tasks**: Long-running imports handled by Celery

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test fires

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 API Documentation

API documentation is available at:
- Development: http://localhost:8000/api/docs/
- Production: https://your-backend-url.railway.app/api/docs/

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NASA FIRMS for providing real-time fire data
- Alberta Energy Regulator for abandoned wells dataset
- The Django and GeoPandas communities

## 📞 Contact

- Project Link: [https://github.com/sadiamith/wildfire-iq-backend](https://github.com/sadiamith/wildfire-iq-backend)
- Frontend Repository: [https://github.com/sadiamith/wildfire-iq-frontend](https://github.com/sadiamith/wildfire-iq-frontend)

---

**Live Demo**: [https://wildfire-iq-frontend.vercel.app](https://wildfire-iq-frontend.vercel.app)
