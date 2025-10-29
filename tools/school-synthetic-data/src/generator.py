"""
Data Generator Orchestrator

Main coordinator for synthetic data generation.
"""
import logging
from typing import List, Optional, Dict, Any
from faker import Faker
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from .cache import EntityCache
from .client import SchoolAPIClient
from .generators import *

logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Main orchestrator for synthetic data generation

    Manages:
    - Generation order (respects dependencies)
    - Progress reporting
    - Error recovery
    - Cache management
    """

    def __init__(self, config: Dict[str, Any], client: SchoolAPIClient, cache: EntityCache):
        """
        Initialize data generator

        Args:
            config: Configuration dictionary
            client: API client instance
            cache: Entity cache instance
        """
        self.config = config
        self.client = client
        self.cache = cache
        self.faker = Faker()
        self.console = Console()

        # Initialize generators
        self.generators = {
            "school": SchoolGenerator(client, cache, self.faker, config),
            "user_admin": UserGenerator(client, cache, self.faker, config),
            "user_teacher": UserGenerator(client, cache, self.faker, config),
            "user_student": UserGenerator(client, cache, self.faker, config),
            "user_parent": UserGenerator(client, cache, self.faker, config),
            "teacher": TeacherGenerator(client, cache, self.faker, config),
            "parent": ParentGenerator(client, cache, self.faker, config),
            "student": StudentGenerator(client, cache, self.faker, config),
            "parent_student": ParentStudentGenerator(client, cache, self.faker, config),
            "subject": SubjectGenerator(client, cache, self.faker, config),
            "room": RoomGenerator(client, cache, self.faker, config),
            "class": ClassGenerator(client, cache, self.faker, config),
            "student_class": StudentClassGenerator(client, cache, self.faker, config),
            "lesson": LessonGenerator(client, cache, self.faker, config),
            "assessment": AssessmentGenerator(client, cache, self.faker, config),
            "attendance": AttendanceGenerator(client, cache, self.faker, config),
            "event": EventGenerator(client, cache, self.faker, config),
            "activity": ActivityGenerator(client, cache, self.faker, config),
            "vendor": VendorGenerator(client, cache, self.faker, config),
            "merit": MeritGenerator(client, cache, self.faker, config),
        }

    def generate_all(self, features: Optional[List[str]] = None) -> None:
        """
        Generate all data in correct dependency order

        Args:
            features: List of features to generate (None = all)
        """
        # Generation order (respects dependencies)
        generation_order = [
            ("school", "School"),
            ("user_admin", "Administrator Users"),
            ("user_teacher", "Teacher Users"),
            ("user_student", "Student Users"),
            ("user_parent", "Parent Users"),
            ("teacher", "Teacher Profiles"),
            ("parent", "Parent Profiles"),
            ("student", "Student Profiles"),
            ("parent_student", "Parent-Student Relationships"),
            ("subject", "Subjects"),
            ("room", "Rooms"),
            ("class", "Classes"),
            ("student_class", "Student-Class Enrollments"),
            ("lesson", "Lessons"),
            ("assessment", "Assessments"),
            ("attendance", "Attendance Records"),
            ("event", "Events"),
            ("activity", "Activities"),
            ("vendor", "Vendors"),
            ("merit", "Merits"),
        ]

        # Filter by requested features if specified
        if features:
            generation_order = [
                (key, name) for key, name in generation_order
                if any(f in key for f in features)
            ]

        self.console.print("\n[bold cyan]🚀 Starting Green School Data Generator[/bold cyan]\n")

        total_steps = len(generation_order)
        completed = 0
        failed = []

        for i, (feature_key, feature_name) in enumerate(generation_order, 1):
            self.console.print(f"[bold blue][{i}/{total_steps}] Generating {feature_name}...[/bold blue]")

            try:
                generator = self.generators[feature_key]

                # Special handling for user generators (need persona parameter)
                if feature_key.startswith("user_"):
                    persona = feature_key.split("_")[1]
                    # Map admin to administrator for correct persona
                    if persona == "admin":
                        persona = "administrator"
                    entities = generator.generate(count=0, persona=persona)
                else:
                    entities = generator.generate(count=0)

                self.console.print(f"   [green]✓[/green] Generated {len(entities)} {feature_name}\n")
                completed += 1

            except Exception as e:
                error_msg = f"Error generating {feature_name}: {str(e)}"
                self.console.print(f"   [red]✗[/red] {error_msg}\n")
                logger.error(error_msg, exc_info=True)
                failed.append((feature_name, str(e)))

                # Stop on critical errors
                if feature_key in ["school", "user_admin"]:
                    self.console.print(f"[red]Critical error in {feature_name}. Stopping generation.[/red]")
                    break

        # Print summary
        self._print_summary(completed, total_steps, failed)

        # Export cache
        if self.config["output"]["export_cache"]:
            cache_file = self.config["output"]["cache_file"]
            self.cache.export_to_json(cache_file)
            self.console.print(f"\n[green]✓[/green] Exported cache to: {cache_file}")

    def _print_summary(self, completed: int, total: int, failed: List[tuple]) -> None:
        """Print generation summary"""
        self.console.print("\n" + "=" * 60)

        if failed:
            self.console.print("[yellow]⚠ Data generation completed with errors[/yellow]\n")
        else:
            self.console.print("[green]✅ Data generation complete![/green]\n")

        # Create statistics table
        table = Table(title="Generation Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Entity Type", style="cyan")
        table.add_column("Count", justify="right", style="green")

        stats = self.cache.get_statistics()

        for entity_type, count in stats.items():
            if count > 0:
                table.add_row(entity_type.replace("_", " ").title(), str(count))

        self.console.print(table)

        # Show failed items
        if failed:
            self.console.print("\n[yellow]Failed Generations:[/yellow]")
            for feature_name, error in failed:
                self.console.print(f"  [red]✗[/red] {feature_name}: {error}")

        # Summary counts
        self.console.print(f"\n[bold]Summary:[/bold]")
        self.console.print(f"  Completed: {completed}/{total}")
        self.console.print(f"  Failed: {len(failed)}")

        total_records = sum(stats.values())
        self.console.print(f"  [bold cyan]Total Records: {total_records:,}[/bold cyan]")

    def get_statistics(self) -> Dict[str, int]:
        """Get entity count statistics"""
        return self.cache.get_statistics()
