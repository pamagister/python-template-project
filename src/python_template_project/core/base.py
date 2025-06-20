import math
import traceback
import zipfile
from datetime import datetime
from pathlib import Path

import gpxpy
from gpxpy.gpx import GPX, GPXTrackPoint, GPXWaypoint, GPXXMLSyntaxException

# Optional SRTM import with fallback
try:
    import srtm

    SRTM_AVAILABLE = True
except ImportError:
    SRTM_AVAILABLE = False
    srtm = None

NAME = "python_template_project"


class BaseGPXProcessor:
    def __init__(
        self,
        input_: str | Path | list[str],
        output=None,
        min_dist=10,
        date_format="%Y-%m-%d",
        elevation=True,
        logger=None,
    ):
        # ensure that input is converted into a list[Path]
        if isinstance(input_, str):
            self.input = [Path(input_)]
        elif isinstance(input_, Path):
            self.input = [input_]
        elif isinstance(input_, list):
            self.input = [Path(p) for p in input_ if isinstance(p, str | Path)]
        else:
            raise ValueError("Input must be a string, Path, or list of strings/Paths.")

        self.output = output
        self.min_dist = min_dist
        self.date_format = date_format
        self.include_elevation = elevation
        self.logger = logger

        # Initialize SRTM elevation data only if elevation is requested and SRTM is available
        self.elevation_data = None
        self.srtm_available = False

        if self.include_elevation:
            self._initialize_elevation_data()

    def _initialize_elevation_data(self):
        """Initialize SRTM elevation data with proper error handling."""
        if not SRTM_AVAILABLE:
            self.logger.warning(
                "SRTM library not available. "
                "Elevation data will use original GPX values or default to 0."
            )
            return

        try:
            self.logger.info("Initializing SRTM elevation data...")
            self.elevation_data = srtm.get_data()
            self.srtm_available = True
            self.logger.info("SRTM elevation data initialized successfully.")
        except AssertionError as e:
            self.logger.error(f"SRTM initialization failed with AssertionError: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            self._handle_srtm_failure("SRTM assertion failed - possibly network or firewall issue")
        except Exception as e:
            self.logger.error(f"SRTM initialization failed: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            self._handle_srtm_failure(f"SRTM initialization error: {str(e)}")

    def _handle_srtm_failure(self, error_msg: str):
        """Handle SRTM initialization failure with firewall check."""
        self.srtm_available = False
        self.elevation_data = None

        self.logger.warning(f"SRTM elevation data unavailable: {error_msg}")
        self.logger.info("Checking for network/firewall issues...")

        # Import and use firewall handler
        try:
            from firewall_handler import FirewallHandler

            firewall_handler = FirewallHandler(logger=self.logger)

            if not firewall_handler.check_network_access():
                self.logger.warning("Network access appears to be blocked.")
                firewall_handler.handle_firewall_issue()
            else:
                self.logger.info(
                    "Network access seems available. SRTM issue may be service-related."
                )

        except ImportError:
            self.logger.warning(
                "FirewallHandler not available. Continuing without network diagnostics."
            )
        except Exception as e:
            self.logger.error(f"Error during firewall check: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")

        self.logger.info(
            "Continuing in offline mode - using original elevation data from GPX files."
        )

    def _get_output_folder(self) -> Path:
        """Get the output folder path, create if not exists."""
        if self.output:
            output_path = Path(self.output)
        else:
            timestamp = datetime.now().strftime(f"{self.date_format}_%H%M")
            output_path = Path.cwd() / f"gpx_processed_{timestamp}"

        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    def _get_adjusted_elevation(self, point: GPXTrackPoint) -> int | float:
        """Get adjusted elevation from SRTM data, fallback to original elevation."""
        # If elevation is not requested, return None
        if not self.include_elevation:
            return None

        # If SRTM is available and working, try to get elevation data
        if self.srtm_available and self.elevation_data:
            try:
                srtm_elevation = self.elevation_data.get_elevation(point.latitude, point.longitude)
                if srtm_elevation is not None:
                    return round(srtm_elevation, 1)
            except Exception as e:
                self.logger.info(
                    f"Error getting SRTM elevation "
                    f"for point ({point.latitude}, {point.longitude}): {e}"
                )
                # Don't disable SRTM entirely for single point failures
                pass

        # Fallback to original elevation or 0
        original_elevation = (
            point.elevation if hasattr(point, "elevation") and point.elevation is not None else 0
        )
        return round(original_elevation, 1)

    @staticmethod
    def _calculate_distance(point1: GPXTrackPoint, point2: GPXTrackPoint) -> float:
        """Calculate distance between two GPX points in meters using Haversine formula."""
        try:
            lat1, lon1 = math.radians(point1.latitude), math.radians(point1.longitude)
            lat2, lon2 = math.radians(point2.latitude), math.radians(point2.longitude)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))

            # Earth's radius in meters
            earth_radius = 6371000
            return earth_radius * c
        except (AttributeError, TypeError, ValueError):
            # Handle cases where points might have invalid coordinates
            return 0.0

    def _optimize_track_points(
        self, track_points: list[GPXTrackPoint] | list[GPXWaypoint]
    ) -> list[GPXTrackPoint]:
        """Optimize track points by removing close points and cleaning metadata."""
        if not track_points:
            return track_points

        try:
            optimized_points = [track_points[0]]  # Always keep first point

            for point in track_points[1:]:
                # Check distance to last kept point
                if self._calculate_distance(optimized_points[-1], point) >= self.min_dist:
                    optimized_points.append(point)

            # Always keep last point if it's different from the last kept point
            if len(track_points) > 1 and optimized_points[-1] != track_points[-1]:
                optimized_points.append(track_points[-1])

            # Clean and optimize each point
            for point in optimized_points:
                try:
                    # Remove time information
                    point.time = None

                    # Round coordinates to 5 decimal places
                    if hasattr(point, "latitude") and point.latitude is not None:
                        point.latitude = round(point.latitude, 5)
                    if hasattr(point, "longitude") and point.longitude is not None:
                        point.longitude = round(point.longitude, 5)

                    # Set optimized elevation
                    point.elevation = self._get_adjusted_elevation(point)

                    # Remove unnecessary extensions and metadata
                    point.extensions = None
                    if hasattr(point, "symbol"):
                        point.symbol = None
                    if hasattr(point, "type"):
                        point.type = None
                    point.comment = None
                    point.description = None
                    point.source = None
                    point.link = None
                    point.link_text = None
                    point.link_type = None
                    point.horizontal_dilution = None
                    point.vertical_dilution = None
                    point.position_dilution = None
                    point.age_of_dgps_data = None
                    point.dgps_id = None
                except Exception as e:
                    self.logger.warning(f"Error optimizing point: {e}")
                    continue

            return optimized_points

        except Exception as e:
            self.logger.error(f"Error optimizing track points: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            return track_points  # Return original points if optimization fails

    def _get_gpx_files(self) -> list[Path]:
        """Get all GPX files from input (file, folder, or zip)."""
        gpx_files = []
        for input_path in self.input:
            try:
                if not isinstance(input_path, Path):
                    input_path = Path(input_path)
                self.logger.debug(f"Input path: {input_path.absolute()}")

                if input_path.is_file():
                    if input_path.suffix.lower() == ".gpx":
                        gpx_files.append(input_path)
                    elif input_path.suffix.lower() == ".zip":
                        gpx_files.extend(self._extract_gpx_from_zip(input_path))
                elif input_path.is_dir():
                    # Get all GPX files in directory
                    gpx_files.extend(input_path.glob("*.gpx"))

                    # Get GPX files from ZIP files in directory
                    for zip_file in input_path.glob("*.zip"):
                        gpx_files.extend(self._extract_gpx_from_zip(zip_file))
            except Exception as e:
                self.logger.error(f"Error processing input path {input_path}: {e}")
                self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
                continue

        return gpx_files

    def _extract_gpx_from_zip(self, zip_path: Path) -> list[Path]:
        """Extract GPX files from ZIP archive to temporary location."""
        gpx_files = []
        temp_dir = Path.cwd() / "temp_gpx_extract"

        try:
            temp_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.lower().endswith(".gpx"):
                        extracted_path = temp_dir / Path(file_info.filename).name
                        with open(extracted_path, "wb") as f:
                            f.write(zip_ref.read(file_info.filename))
                        gpx_files.append(extracted_path)
        except Exception as e:
            self.logger.error(f"Error extracting ZIP file {zip_path}: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")

        return gpx_files

    def _load_gpx_file(self, gpx_path: Path) -> GPX | None:
        """Load and parse GPX file."""
        try:
            with open(gpx_path, "r", encoding="utf-8") as f:
                return gpxpy.parse(f)
        except GPXXMLSyntaxException as e:
            self.logger.error(f"Error parsing GPX file {gpx_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading GPX file {gpx_path}: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            return None

    def _save_gpx_file(self, gpx: GPX, output_path: Path, original_file: Path | None = None):
        """Save GPX object to file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(gpx.to_xml())
                if original_file and original_file.exists():
                    self.logger.info(
                        f"Original gpx file size: "
                        f"{Path(original_file).stat().st_size / 1024:.2f} KB"
                    )
                self.logger.info(
                    f"Processed gpx file size: {output_path.stat().st_size / 1024:.2f} KB"
                )

        except Exception as e:
            self.logger.error(f"Error saving GPX file {output_path}: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")

    def compress_files(self):
        """Shrink the size of all given gpx files in self.input."""
        try:
            gpx_files = self._get_gpx_files()
            output_folder = self._get_output_folder()

            self.logger.info(f"Processing {len(gpx_files)} GPX files...")

            for gpx_file in gpx_files:
                try:
                    gpx = self._load_gpx_file(gpx_file)
                    if gpx is None:
                        continue

                    # process and clean waypoints
                    for waypoint in gpx.waypoints:
                        self._optimize_waypoint(waypoint)

                    # Process all tracks
                    for track in gpx.tracks:
                        for segment in track.segments:
                            segment.points = self._optimize_track_points(segment.points)

                    # Process all routes
                    for route in gpx.routes:
                        route.points = self._optimize_track_points(route.points)

                    # Clean GPX metadata
                    gpx.time = None
                    gpx.extensions = None

                    # Save compressed file
                    output_path = output_folder / f"compressed_{gpx_file.name}"
                    self._save_gpx_file(gpx, output_path, gpx_file)
                    self.logger.info(f"Compressed: {gpx_file.name} -> {output_path}")

                except Exception as e:
                    self.logger.error(f"Error processing file {gpx_file}: {e}")
                    self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in compress_files: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            raise

    def _optimize_waypoint(self, waypoint):
        """Optimize waypoint with error handling."""
        try:
            # Round coordinates and elevation
            if hasattr(waypoint, "latitude") and waypoint.latitude is not None:
                waypoint.latitude = round(waypoint.latitude, 5)
            if hasattr(waypoint, "longitude") and waypoint.longitude is not None:
                waypoint.longitude = round(waypoint.longitude, 5)

            waypoint.elevation = self._get_adjusted_elevation(waypoint)

            # Clean metadata
            waypoint.time = None
            waypoint.extensions = None
            if hasattr(waypoint, "symbol"):
                waypoint.symbol = None
            if hasattr(waypoint, "type"):
                waypoint.type = None
            waypoint.comment = None
            waypoint.description = None
            waypoint.source = None
            waypoint.link = None
            waypoint.link_text = None
            waypoint.link_type = None
            return waypoint
        except Exception as e:
            self.logger.warning(f"Error optimizing waypoint: {e}")
            return waypoint

    def merge_files(self):
        """Merge all files of self.input into one gpx file with reduced resolution."""
        try:
            gpx_files = self._get_gpx_files()
            output_folder = self._get_output_folder()

            if not gpx_files:
                self.logger.error("No GPX files found to merge.")
                return

            self.logger.info(f"Merging {len(gpx_files)} GPX files...")

            # Create new GPX object
            merged_gpx = gpxpy.gpx.GPX()
            merged_gpx.name = "Merged GPX Tracks"
            merged_gpx.description = f"Merged from {len(gpx_files)} GPX files."

            track_counter = 1

            for gpx_file in gpx_files:
                try:
                    gpx = self._load_gpx_file(gpx_file)
                    if gpx is None:
                        continue

                    # Add all waypoints from this file
                    for waypoint in gpx.waypoints:
                        waypoint = self._optimize_waypoint(waypoint)
                        waypoint.name = f"{waypoint.name}_{track_counter}"
                        merged_gpx.waypoints.append(waypoint)

                    # Add all tracks from this file
                    for track in gpx.tracks:
                        new_track = gpxpy.gpx.GPXTrack()
                        new_track.name = f"{track.name or track_counter}_{gpx_file.stem}"

                        for segment in track.segments:
                            optimized_points = self._optimize_track_points(segment.points)
                            if optimized_points:
                                new_segment = gpxpy.gpx.GPXTrackSegment()
                                new_segment.points = optimized_points
                                new_track.segments.append(new_segment)

                        if new_track.segments:
                            merged_gpx.tracks.append(new_track)
                            track_counter += 1

                    # Add all routes from this file
                    for route in gpx.routes:
                        new_route = gpxpy.gpx.GPXRoute()
                        new_route.name = f"{route.name or track_counter}_{gpx_file.stem}"
                        new_route.points = self._optimize_track_points(route.points)

                        if new_route.points:
                            merged_gpx.routes.append(new_route)
                            track_counter += 1

                except Exception as e:
                    self.logger.error(f"Error processing file {gpx_file} during merge: {e}")
                    self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
                    continue

            # Save merged file
            output_path = output_folder / "merged_tracks.gpx"
            self._save_gpx_file(merged_gpx, output_path)
            self.logger.info(f"Merged file saved: {output_path}")

        except Exception as e:
            self.logger.error(f"Error in merge_files: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            raise

    def extract_pois(self):
        """Merge every starting point of each track in all files
        into one gpx file with many pois."""
        try:
            gpx_files = self._get_gpx_files()
            output_folder = self._get_output_folder()

            if not gpx_files:
                self.logger.error("No GPX files found to extract POIs from.")
                return

            self.logger.info(f"Extracting POIs from {len(gpx_files)} GPX files...")

            # Create new GPX object for waypoints
            poi_gpx = gpxpy.gpx.GPX()
            poi_gpx.name = "Extracted Track Starting Points"
            poi_gpx.description = f"Starting points extracted from {len(gpx_files)} GPX files"

            poi_counter = 1

            for gpx_file in gpx_files:
                try:
                    gpx = self._load_gpx_file(gpx_file)
                    if gpx is None:
                        continue

                    # Extract starting points from tracks
                    for track_idx, track in enumerate(gpx.tracks):
                        for _segment_idx, segment in enumerate(track.segments):
                            if segment.points:
                                start_point = segment.points[0]

                                # Create waypoint from starting point
                                waypoint = gpxpy.gpx.GPXWaypoint(
                                    latitude=round(start_point.latitude, 5),
                                    longitude=round(start_point.longitude, 5),
                                    elevation=self._get_adjusted_elevation(start_point),
                                )

                                track_name = track.name or f"Track_{track_idx + 1}"
                                waypoint.name = f"POI_{poi_counter:03d}"
                                waypoint.description = f"Start of {track_name} from {gpx_file.name}"
                                waypoint.type = "Track Start"

                                poi_gpx.waypoints.append(waypoint)
                                poi_counter += 1

                    # Extract starting points from routes
                    for route_idx, route in enumerate(gpx.routes):
                        if route.points:
                            start_point = route.points[0]

                            # Create waypoint from starting point
                            waypoint = gpxpy.gpx.GPXWaypoint(
                                latitude=round(start_point.latitude, 5),
                                longitude=round(start_point.longitude, 5),
                                elevation=self._get_adjusted_elevation(start_point),
                            )

                            route_name = route.name or f"Route_{route_idx + 1}"
                            waypoint.name = f"POI_{poi_counter:03d}"
                            waypoint.description = f"Start of {route_name} from {gpx_file.name}"
                            waypoint.type = "Route Start"

                            poi_gpx.waypoints.append(waypoint)
                            poi_counter += 1

                except Exception as e:
                    self.logger.error(
                        f"Error processing file {gpx_file} during POI extraction: {e}"
                    )
                    self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
                    continue

            # Save POI file
            output_path = output_folder / "extracted_pois.gpx"
            self._save_gpx_file(poi_gpx, output_path)
            self.logger.info(
                f"POI file saved with {len(poi_gpx.waypoints)} waypoints: {output_path}"
            )

            # Clean up temporary files
            temp_dir = Path.cwd() / "temp_gpx_extract"
            if temp_dir.exists():
                import shutil

                shutil.rmtree(temp_dir)

        except Exception as e:
            self.logger.error(f"Error in extract_pois: {e}")
            self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            raise
