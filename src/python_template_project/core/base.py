import math
import zipfile
from datetime import datetime
from pathlib import Path

import gpxpy
import srtm
from gpxpy.gpx import GPX, GPXTrackPoint, GPXWaypoint, GPXXMLSyntaxException

NAME = "python_template_project"


class BaseGPXProcessor:
    def __init__(
        self,
        input_: str | Path | list[str],
        output=None,
        min_dist=10,
        date_format="%Y-%m-%d",
        logger=None,
    ):
        # ensure that input is converted into a list[Path]
        if isinstance(input_, str):
            self.input = [Path(input_)]
        elif isinstance(input_, Path):
            self.input = [input_]
        elif isinstance(input_, list):
            self.input = [Path(p) for p in input_ if isinstance(p, (str, Path))]
        else:
            raise ValueError("Input must be a string, Path, or list of strings/Paths.")

        self.output = output
        self.min_dist = min_dist
        self.date_format = date_format

        # Initialize SRTM elevation data
        self.elevation_data = srtm.get_data()
        self.logger = logger

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
        try:
            srtm_elevation = self.elevation_data.get_elevation(point.latitude, point.longitude)
            if srtm_elevation is not None:
                return round(srtm_elevation, 1)
        except Exception:
            pass

        # Fallback to original elevation or 0
        return round(point.elevation or 0, 1)

    @staticmethod
    def _calculate_distance(point1: GPXTrackPoint, point2: GPXTrackPoint) -> float:
        """Calculate distance between two GPX points in meters using Haversine formula."""
        lat1, lon1 = math.radians(point1.latitude), math.radians(point1.longitude)
        lat2, lon2 = math.radians(point2.latitude), math.radians(point2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in meters
        earth_radius = 6371000
        return earth_radius * c

    def _optimize_track_points(
        self, track_points: list[GPXTrackPoint] | list[GPXWaypoint]
    ) -> list[GPXTrackPoint]:
        """Optimize track points by removing close points and cleaning metadata."""
        if not track_points:
            return track_points

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
            # Remove time information
            point.time = None

            # Round coordinates to 5 decimal places
            point.latitude = round(point.latitude, 5)
            point.longitude = round(point.longitude, 5)

            # Set optimized elevation
            point.elevation = self._get_adjusted_elevation(point)

            # Remove unnecessary extensions and metadata
            point.extensions = None
            point.symbol = None
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

        return optimized_points

    def _get_gpx_files(self) -> list[Path]:
        """Get all GPX files from input (file, folder, or zip)."""
        gpx_files = []
        for input_path in self.input:
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

        return gpx_files

    def _extract_gpx_from_zip(self, zip_path: Path) -> list[Path]:
        """Extract GPX files from ZIP archive to temporary location."""
        gpx_files = []
        temp_dir = Path.cwd() / "temp_gpx_extract"
        temp_dir.mkdir(exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.lower().endswith(".gpx"):
                        extracted_path = temp_dir / Path(file_info.filename).name
                        with open(extracted_path, "wb") as f:
                            f.write(zip_ref.read(file_info.filename))
                        gpx_files.append(extracted_path)
        except Exception as e:
            self.logger.error(f"Error extracting ZIP file {zip_path}: {e}")

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
            return None

    def _save_gpx_file(self, gpx: GPX, output_path: Path, original_file: Path | None = None):
        """Save GPX object to file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(gpx.to_xml())
                if original_file and original_file.exists():
                    self.logger.info(
                        f"Original gpx file size: {Path(original_file).stat().st_size / 1024:.2f} KB"
                    )
                self.logger.info(
                    f"Processed gpx file size: {output_path.stat().st_size / 1024:.2f} KB"
                )

        except Exception as e:
            self.logger.error(f"Error saving GPX file {output_path}: {e}")

    def compress_files(self):
        """Shrink the size of all given gpx files in self.input."""
        gpx_files = self._get_gpx_files()
        output_folder = self._get_output_folder()

        self.logger.info(f"Processing {len(gpx_files)} GPX files...")

        for gpx_file in gpx_files:
            gpx = self._load_gpx_file(gpx_file)
            if gpx is None:
                continue

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

    def merge_files(self):
        """Merge all files of self.input into one gpx file with reduced resolution."""
        gpx_files = self._get_gpx_files()
        output_folder = self._get_output_folder()

        if not gpx_files:
            self.logger.error("No GPX files found to merge.")
            return

        self.logger.info(f"Merging {len(gpx_files)} GPX files...")

        # Create new GPX object
        merged_gpx = gpxpy.gpx.GPX()
        merged_gpx.name = "Merged GPX Tracks"
        merged_gpx.description = f"Merged from {len(gpx_files)} GPX files"

        track_counter = 1

        for gpx_file in gpx_files:
            gpx = self._load_gpx_file(gpx_file)
            if gpx is None:
                continue

            # Add all tracks from this file
            for track in gpx.tracks:
                new_track = gpxpy.gpx.GPXTrack()
                new_track.name = f"{gpx_file.stem}_{track.name or track_counter}"

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
                new_route.name = f"{gpx_file.stem}_{route.name or track_counter}"
                new_route.points = self._optimize_track_points(route.points)

                if new_route.points:
                    merged_gpx.routes.append(new_route)
                    track_counter += 1

        # Save merged file
        output_path = output_folder / "merged_tracks.gpx"
        self._save_gpx_file(merged_gpx, output_path)
        self.logger.info(f"Merged file saved: {output_path}")

    def extract_pois(self):
        """Merge every starting point of each track in all files
        into one gpx file with many pois."""

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

        # Save POI file
        output_path = output_folder / "extracted_pois.gpx"
        self._save_gpx_file(poi_gpx, output_path)
        self.logger.info(f"POI file saved with {len(poi_gpx.waypoints)} waypoints: {output_path}")

        # Clean up temporary files
        temp_dir = Path.cwd() / "temp_gpx_extract"
        if temp_dir.exists():
            import shutil

            shutil.rmtree(temp_dir)
