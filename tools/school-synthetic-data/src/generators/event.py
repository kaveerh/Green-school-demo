"""
Event Generator

Generate school calendar events.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
import random
from .base import BaseGenerator


class EventGenerator(BaseGenerator):
    """
    Generate event records

    Responsibilities:
    - Create school calendar events
    - Distribute event types
    - Schedule throughout academic year
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate event records

        Args:
            count: Number of events (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated event dictionaries
        """
        events = []
        school_id = self._get_school_id()

        # Get event types from config
        event_types_config = self.config.get("generation_rules", {}).get("event_types", {})

        if not event_types_config:
            raise ValueError("No event types configured")

        total_events = sum(event_types_config.values())

        # Get date range
        dates_config = self.config.get("generation_rules", {}).get("dates", {})
        start_date_str = dates_config.get("academic_year_start", "2024-09-01")
        end_date_str = dates_config.get("academic_year_end", "2025-06-30")

        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)

        # Get rooms for venue
        rooms = list(self.cache.rooms.values())

        # Get admin user for organizer
        admin_users = [u for u in self.cache.users.values() if u.get("persona") == "administrator"]
        organizer_id = admin_users[0]["id"] if admin_users else None

        self._log_progress(f"Creating {total_events} events")

        for event_type, count in event_types_config.items():
            for i in range(count):
                # Random date within academic year
                days_range = (end_date - start_date).days
                event_date = start_date + timedelta(days=random.randint(0, days_range))

                # Event titles by type
                if event_type == "assembly":
                    title = random.choice([
                        "Fall Assembly",
                        "Spring Assembly",
                        "Awards Ceremony",
                        "Welcome Back Assembly",
                        "End of Year Celebration"
                    ])
                elif event_type == "exam":
                    title = random.choice([
                        "Midterm Exams",
                        "Final Exams",
                        "Q1 Assessment Week",
                        "Q2 Testing Period",
                        "Standardized Testing"
                    ])
                elif event_type == "holiday":
                    title = random.choice([
                        "Winter Break",
                        "Spring Break",
                        "Thanksgiving Holiday",
                        "Presidents Day",
                        "Memorial Day"
                    ])
                elif event_type == "meeting":
                    title = random.choice([
                        "Parent-Teacher Conferences",
                        "Staff Meeting",
                        "PTA Meeting",
                        "School Board Meeting",
                        "Faculty Planning Day"
                    ])
                elif event_type == "parent_conference":
                    title = "Parent-Teacher Conference Day"
                elif event_type == "field_trip":
                    title = random.choice([
                        "Science Museum Field Trip",
                        "Zoo Visit",
                        "Historical Site Tour",
                        "Art Gallery Visit",
                        "Nature Center Excursion"
                    ])
                else:
                    title = f"{event_type.replace('_', ' ').title()} Event"

                # Set duration
                if event_type == "holiday":
                    duration_days = random.randint(1, 5)
                    end_event_date = event_date + timedelta(days=duration_days - 1)
                    is_all_day = True
                else:
                    end_event_date = event_date
                    is_all_day = False

                # Pick room for venue
                if event_type in ["assembly", "meeting"]:
                    # Use gym or cafeteria
                    venue_rooms = [r for r in rooms if r.get("room_type") in ["gym", "cafeteria"]]
                    room = random.choice(venue_rooms) if venue_rooms else None
                    location = room.get("room_name") if room else "Main Auditorium"
                    room_id = room.get("id") if room else None
                else:
                    room_id = None
                    location = random.choice([
                        "Main Auditorium",
                        "Gymnasium",
                        "Cafeteria",
                        "Library",
                        "Off-campus"
                    ])

                event_data = {
                    "school_id": school_id,
                    "title": title,
                    "description": f"{title} for students and staff",
                    "event_type": event_type,
                    "start_date": event_date.isoformat(),
                    "end_date": end_event_date.isoformat(),
                    "start_time": "09:00:00" if not is_all_day else None,
                    "end_time": "15:00:00" if not is_all_day else None,
                    "is_all_day": is_all_day,
                    "location": location,
                    "room_id": room_id,
                    "organizer_id": organizer_id,
                    "target_audience": "all_school",
                    "status": "scheduled",
                    "requires_rsvp": event_type in ["parent_conference", "meeting"],
                    "color": self._get_event_color(event_type),
                    "created_by_id": organizer_id,  # Add for query parameter
                }

                event = self.client.create_event(event_data)
                self.cache.add_entity("event", event["id"], event)
                events.append(event)

        self._log_progress(f"✓ Created {len(events)} events")

        return events

    def _get_event_color(self, event_type: str) -> str:
        """Get color code for event type"""
        colors = {
            "assembly": "#4CAF50",
            "exam": "#F44336",
            "holiday": "#FF9800",
            "meeting": "#2196F3",
            "parent_conference": "#9C27B0",
            "field_trip": "#00BCD4",
            "sports": "#8BC34A",
            "performance": "#E91E63",
        }
        return colors.get(event_type, "#757575")
