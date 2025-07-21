import os
import zipfile
import tempfile
import geopandas as gpd
from django.core.management.base import BaseCommand
from django.db import transaction
from fires.models import AbandonedWell
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import abandoned wells data from AER shapefile"

    def add_arguments(self, parser):
        parser.add_argument(
            "shapefile_path", type=str, help="Path to the ABNDWells_SHP.zip file"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing well data before importing",
        )

    def handle(self, *args, **options):
        shapefile_path = options["shapefile_path"]
        clear_existing = options["clear"]

        if not os.path.exists(shapefile_path):
            self.stdout.write(self.style.ERROR(f"File not found: {shapefile_path}"))
            return

        # Clear existing data if requested
        if clear_existing:
            deleted_count = AbandonedWell.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f"Cleared {deleted_count} existing well records")
            )

        # Extract and process shapefile
        with tempfile.TemporaryDirectory() as temp_dir:
            self.stdout.write("Extracting shapefile...")

            # Extract zip file
            with zipfile.ZipFile(shapefile_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the .shp file
            shp_file = None
            for file in os.listdir(temp_dir):
                if file.endswith(".shp"):
                    shp_file = os.path.join(temp_dir, file)
                    break

            if not shp_file:
                self.stdout.write(self.style.ERROR("No .shp file found in archive"))
                return

            # Read shapefile
            self.stdout.write("Reading shapefile...")
            gdf = gpd.read_file(shp_file)

            # Convert to WGS84 (lat/lon) if needed
            if gdf.crs and gdf.crs != "EPSG:4326":
                self.stdout.write("Converting coordinates to WGS84...")
                gdf = gdf.to_crs("EPSG:4326")

            # Process and save wells
            self.stdout.write(f"Processing {len(gdf)} wells...")
            created_count = 0
            updated_count = 0
            error_count = 0

            with transaction.atomic():
                for idx, row in gdf.iterrows():
                    try:
                        # Extract coordinates
                        geom = row.geometry
                        if geom is None:
                            error_count += 1
                            continue

                        lon = geom.x
                        lat = geom.y

                        # Map shapefile fields to model fields
                        # Adjust these based on actual shapefile columns
                        well_data = {
                            "well_id": str(row.get("WELL_ID", f"UNK-{idx}")),
                            "license_number": str(row.get("LICENCE_NO", "")),
                            "well_name": str(row.get("WELL_NAME", "")),
                            "latitude": lat,
                            "longitude": lon,
                            "well_type": str(row.get("WELL_TYPE", "")),
                            "status": "ABANDONED",
                            "licensee": str(row.get("LICENSEE", "")),
                            "surface_location": str(row.get("SURFACE_LO", "")),
                            "ground_elevation": (
                                float(row.get("GROUND_ELE", 0))
                                if row.get("GROUND_ELE")
                                else None
                            ),
                            "total_depth": (
                                float(row.get("TOTAL_DEPT", 0))
                                if row.get("TOTAL_DEPT")
                                else None
                            ),
                        }

                        # Remove empty strings
                        well_data = {k: v for k, v in well_data.items() if v != ""}

                        # Create or update well
                        well, created = AbandonedWell.objects.update_or_create(
                            well_id=well_data["well_id"], defaults=well_data
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                        if (created_count + updated_count) % 1000 == 0:
                            self.stdout.write(
                                f"Progress: {created_count + updated_count} wells processed..."
                            )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error processing well at index {idx}: {e}")

            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nImport complete:\n"
                    f"- Created: {created_count} new wells\n"
                    f"- Updated: {updated_count} existing wells\n"
                    f"- Errors: {error_count}\n"
                    f"- Total wells in database: {AbandonedWell.objects.count()}"
                )
            )

            # Print sample field names for reference
            if len(gdf) > 0:
                self.stdout.write("\nShapefile columns found:")
                for col in gdf.columns:
                    if col != "geometry":
                        self.stdout.write(f"  - {col}")
