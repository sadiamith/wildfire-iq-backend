import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)

class FIRMSService:
    """Service to fetch wildfire data from NASA FIRMS API"""

    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv"

    # Alberta bounding box coordinates
    ALBERTA_BOUNDS = {
        "north": 60.0,
        "south": 48.0,
        "east": -110.0,
        "west": -120.0,
    }

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.FIRMS_API_KEY

    def fetch_active_fires(self, days_back=1):
        """
        Fetch active fires from FIRMS for Alberta region 

        Args:
            days_back (int): Number of days of historical data to fetch. Default is 1 day.

        Returns:
            list: List of fire data dictionaries.
        
        """

        if not self.api_key:
            logger.error("FIRMS API key is not set.")
            return []
        
        # build request URL for Canada
        url = self._build_url(days_back)

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            # Parse CSV response
            fires = self._parse_csv_response(response.text)

            # filter to Alberta only
            alberta_fires = self._filter_alberta_fires(fires)

            logger.info(f"Fetched {len(alberta_fires)} fires in Alberta")

            return alberta_fires
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching FIRMS data: {e}")

    
    def _build_url(self, days_back):

        """Build FIRMS API request URL."""
        # Format: /api/country/csv/{api_key}/{source}/{country}/{days}
        source = 'VIIRS_SNPP_NRT' # Near real time VIIRS data
        country = 'CAN' # Canada country code
        days = min(days_back, 10) # API max is 10 days

        url = f"{self.BASE_URL}/{self.api_key}/{source}/{country}/{days}"

        return url
    
    def _parse_csv_response(self, csv_text):
        """Parse CSV response from FIRMS API."""
        fires = []
        lines = csv_text.strip().split('\n')
        
        if len(lines) < 2:
            return fires
        
        # Parse header
        headers = lines[0].split(',')
        
        # Parse data rows
        for line in lines[1:]:
            values = line.split(',')
            if len(values) == len(headers):
                fire_dict = dict(zip(headers, values))
                fires.append(fire_dict)
        
        return fires
    
    def _filter_alberta_fires(self, fires):
        """Filter fires to only those within Alberta bounds."""
        alberta_fires = []
        
        for fire in fires:
            try:
                lat = float(fire.get('latitude', 0))
                lon = float(fire.get('longitude', 0))
                
                # Check if within Alberta bounds
                if (self.ALBERTA_BOUNDS['south'] <= lat <= self.ALBERTA_BOUNDS['north'] and
                    self.ALBERTA_BOUNDS['west'] <= lon <= self.ALBERTA_BOUNDS['east']):
                    alberta_fires.append(fire)
                    
            except (ValueError, TypeError):
                continue
        
        return alberta_fires
    
    def transform_to_wildfire_model(self, firms_data):
        """
        Transform FIRMS data to match our Wildfire model fields.
        
        FIRMS fields include:
        - latitude, longitude
        - bright_ti4 (brightness temperature)
        - scan, track (fire pixel size)
        - acq_date, acq_time (acquisition date/time)
        - confidence (detection confidence)
        """
        try:
            # Calculate approximate size in hectares
            # VIIRS pixel is approximately 375m x 375m = 0.14 hectares
            pixel_size_hectares = 0.14
            scan = float(firms_data.get('scan', 1))
            track = float(firms_data.get('track', 1))
            estimated_size = pixel_size_hectares * scan * track
            
            # Parse acquisition datetime
            acq_date = firms_data.get('acq_date', '')
            acq_time = firms_data.get('acq_time', '0000')
            
            # Format: YYYY-MM-DD and HHMM
            detected_datetime = datetime.strptime(
                f"{acq_date} {acq_time}", 
                "%Y-%m-%d %H%M"
            )
            detected_datetime = timezone.make_aware(detected_datetime, timezone.utc)
            
            # Generate unique fire ID
            fire_id = f"FIRMS-{acq_date}-{firms_data.get('latitude')[:6]}-{firms_data.get('longitude')[:7]}"
            
            return {
                'fire_id': fire_id,
                'fire_name': f"Fire near {float(firms_data.get('latitude')):.2f}N {abs(float(firms_data.get('longitude'))):.2f}W",
                'latitude': float(firms_data.get('latitude')),
                'longitude': float(firms_data.get('longitude')),
                'size_hectares': round(estimated_size, 2),
                'status': 'ACTIVE',  # FIRMS only shows active fires
                'detected_date': detected_datetime,
                'data_source': 'NASA_FIRMS',
                'cause': 'Unknown',
                'location_description': f"Confidence: {firms_data.get('confidence', 'nominal')}"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error transforming FIRMS data: {e}")
            return []