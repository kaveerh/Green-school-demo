"""
CLI Entry Point

Command-line interface for school synthetic data generator.
"""
import click
import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
import json

from .config import load_config, get_default_config_path
from .cache import EntityCache
from .client import SchoolAPIClient
from .generator import DataGenerator


console = Console()


def setup_logging(log_level: str) -> None:
    """Configure logging"""
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    School Synthetic Data Generator

    Generate realistic synthetic data for the Green School Management System.
    """
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration YAML file",
)
@click.option(
    "--cache",
    type=click.Path(exists=True),
    help="Path to existing cache JSON file (for incremental generation)",
)
@click.option(
    "--features",
    "-f",
    help="Comma-separated list of features to generate (e.g., 'students,classes,lessons')",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
def generate(config: str, cache: str, features: str, log_level: str):
    """
    Generate synthetic data

    Examples:

    \b
    # Generate all data with default config
    python -m src.main generate

    \b
    # Generate with custom config
    python -m src.main generate --config my_config.yaml

    \b
    # Generate specific features only
    python -m src.main generate --features students,classes,lessons

    \b
    # Use existing cache for incremental generation
    python -m src.main generate --cache cache.json --features assessments
    """
    try:
        # Load configuration
        config_path = config or get_default_config_path()
        cfg = load_config(config_path)

        # Setup logging
        log_level = cfg["output"].get("log_level", log_level)
        setup_logging(log_level)

        console.print(f"\n[cyan]Configuration:[/cyan] {config_path}")

        # Initialize API client
        api_url = cfg["api"]["base_url"]
        api_timeout = cfg["api"]["timeout"]
        client = SchoolAPIClient(api_url, api_timeout)

        console.print(f"[cyan]API URL:[/cyan] {api_url}")

        # Initialize cache
        entity_cache = EntityCache()

        # Load existing cache if provided
        if cache:
            console.print(f"[cyan]Loading cache:[/cyan] {cache}")
            entity_cache.import_from_json(cache)
            stats = entity_cache.get_statistics()
            console.print(f"[green]✓[/green] Loaded {sum(stats.values())} cached entities")

        # Parse features list
        feature_list = None
        if features:
            feature_list = [f.strip() for f in features.split(",")]
            console.print(f"[cyan]Features:[/cyan] {', '.join(feature_list)}")

        # Initialize generator
        generator = DataGenerator(cfg, client, entity_cache)

        # Generate data
        generator.generate_all(features=feature_list)

        console.print("\n[bold green]🎉 Generation complete![/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Generation interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Error: {str(e)}[/red]")
        logging.error("Generation failed", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option("--cache", type=click.Path(exists=True), required=True, help="Cache file to display")
def cache_stats(cache: str):
    """Show cache statistics"""
    try:
        entity_cache = EntityCache()
        entity_cache.import_from_json(cache)

        stats = entity_cache.get_statistics()

        table = Table(title=f"Cache Statistics: {cache}", show_header=True, header_style="bold cyan")
        table.add_column("Entity Type", style="cyan")
        table.add_column("Count", justify="right", style="green")

        for entity_type, count in stats.items():
            if count > 0:
                table.add_row(entity_type.replace("_", " ").title(), str(count))

        console.print("\n")
        console.print(table)

        total = sum(stats.values())
        console.print(f"\n[bold]Total Records: {total:,}[/bold]\n")

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--type", "-t", required=True, help="Entity type (student, teacher, parent, etc.)")
@click.option("--name", help="Search by name (first and last name)")
@click.option("--student-id", help="Search by student ID")
@click.option("--email", help="Search by email")
@click.option("--cache", type=click.Path(exists=True), help="Cache file to search")
def find(type: str, name: str, student_id: str, email: str, cache: str):
    """
    Find entity by name, ID, or email

    Examples:

    \b
    # Find student by name
    python -m src.main find --type student --name "John Doe"

    \b
    # Find student by ID
    python -m src.main find --type student --student-id "STU01001"

    \b
    # Find user by email
    python -m src.main find --type user --email "john.doe@school.edu"
    """
    try:
        # Load cache
        cache_file = cache or "generated_data_cache.json"
        entity_cache = EntityCache()

        if not Path(cache_file).exists():
            console.print(f"[red]✗ Cache file not found: {cache_file}[/red]")
            sys.exit(1)

        entity_cache.import_from_json(cache_file)

        result = None

        if type == "student" and student_id:
            result = entity_cache.find_student_by_student_id(student_id)
        elif type == "user" and email:
            result = entity_cache.find_user_by_email(email)
        elif name:
            parts = name.split()
            if len(parts) < 2:
                console.print("[red]✗ Name must include first and last name[/red]")
                sys.exit(1)

            first_name = parts[0]
            last_name = " ".join(parts[1:])

            if type == "user":
                result = entity_cache.find_user_by_name(first_name, last_name)
            elif type == "teacher":
                result = entity_cache.find_teacher_by_name(first_name, last_name)
            elif type == "parent":
                result = entity_cache.find_parent_by_name(first_name, last_name)
            elif type == "student":
                # Search students by user name
                for student in entity_cache.students.values():
                    if (
                        student.get("first_name", "").lower() == first_name.lower()
                        and student.get("last_name", "").lower() == last_name.lower()
                    ):
                        result = student
                        break
        else:
            console.print("[red]✗ Please provide search criteria (name, student-id, or email)[/red]")
            sys.exit(1)

        if result:
            console.print("\n[green]✓ Found:[/green]\n")
            console.print(json.dumps(result, indent=2))
            console.print()
        else:
            console.print(f"\n[yellow]⚠ No {type} found with provided criteria[/yellow]\n")

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--type", "-t", required=True, help="Entity type (students, teachers, classes, etc.)")
@click.option("--cache", type=click.Path(exists=True), help="Cache file to list from")
@click.option("--limit", type=int, default=10, help="Number of items to display")
def list_entities(type: str, cache: str, limit: int):
    """
    List entities from cache

    Examples:

    \b
    # List first 10 students
    python -m src.main list --type students

    \b
    # List all teachers
    python -m src.main list --type teachers --limit 100
    """
    try:
        # Load cache
        cache_file = cache or "generated_data_cache.json"
        entity_cache = EntityCache()

        if not Path(cache_file).exists():
            console.print(f"[red]✗ Cache file not found: {cache_file}[/red]")
            sys.exit(1)

        entity_cache.import_from_json(cache_file)

        # Get entities
        entities = entity_cache.get_all_entities(type.rstrip('s'))  # Remove trailing 's'

        if not entities:
            console.print(f"\n[yellow]⚠ No {type} found in cache[/yellow]\n")
            return

        # Show first N entities
        display_entities = entities[:limit]

        console.print(f"\n[cyan]Showing {len(display_entities)} of {len(entities)} {type}:[/cyan]\n")

        for i, entity in enumerate(display_entities, 1):
            # Show key fields
            if "first_name" in entity and "last_name" in entity:
                name = f"{entity['first_name']} {entity['last_name']}"
            elif "name" in entity:
                name = entity["name"]
            elif "title" in entity:
                name = entity["title"]
            elif "company_name" in entity:
                name = entity["company_name"]
            else:
                name = entity.get("id", "Unknown")

            console.print(f"  {i}. {name} (ID: {entity.get('id', 'N/A')})")

        if len(entities) > limit:
            console.print(f"\n[dim]... and {len(entities) - limit} more[/dim]")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--output", "-o", required=True, help="Output file path")
@click.option("--cache", type=click.Path(exists=True), help="Cache file to export")
def export_cache(output: str, cache: str):
    """Export cache to JSON file"""
    try:
        cache_file = cache or "generated_data_cache.json"
        entity_cache = EntityCache()

        if not Path(cache_file).exists():
            console.print(f"[red]✗ Cache file not found: {cache_file}[/red]")
            sys.exit(1)

        entity_cache.import_from_json(cache_file)
        entity_cache.export_to_json(output)

        console.print(f"[green]✓[/green] Exported cache to: {output}")

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), required=True, help="Config file to validate")
def validate_config(config: str):
    """Validate configuration file"""
    try:
        cfg = load_config(config)
        console.print(f"[green]✓[/green] Configuration is valid: {config}")
    except Exception as e:
        console.print(f"[red]✗[/red] Configuration error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
