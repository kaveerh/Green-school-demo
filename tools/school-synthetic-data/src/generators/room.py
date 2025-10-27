"""
Room Generator

Generate room/facility records.
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class RoomGenerator(BaseGenerator):
    """
    Generate room records

    Responsibilities:
    - Create rooms based on type distribution
    - Assign room numbers and buildings
    - Set capacity and features
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate room records

        Args:
            count: Not used (rooms from config)
            **kwargs: Additional parameters

        Returns:
            List of generated room dictionaries
        """
        rooms = []
        school_id = self._get_school_id()

        # Get room types from config
        room_types_config = self.config.get("generation_rules", {}).get("room_types", {})

        if not room_types_config:
            raise ValueError("No room types configured in generation_rules.room_types")

        total_rooms = sum(room_types_config.values())
        self._log_progress(f"Creating {total_rooms} rooms")

        room_number_counter = 101

        for room_type, count in room_types_config.items():
            for i in range(count):
                # Assign building and floor
                building = self.faker.random_element(["Main Building", "East Wing", "West Wing"])
                floor = self.faker.random_int(min=1, max=3)

                # Set capacity based on room type
                if room_type == "classroom":
                    capacity = self.faker.random_int(min=20, max=30)
                elif room_type == "lab":
                    capacity = self.faker.random_int(min=15, max=25)
                elif room_type == "gym":
                    capacity = self.faker.random_int(min=100, max=200)
                elif room_type == "library":
                    capacity = self.faker.random_int(min=50, max=100)
                elif room_type == "office":
                    capacity = self.faker.random_int(min=2, max=5)
                else:
                    capacity = 30

                # Set equipment based on room type
                equipment = []
                if room_type == "classroom":
                    equipment = ["Whiteboard", "Projector", "Computer", "Desks", "Chairs"]
                elif room_type == "lab":
                    equipment = ["Lab Tables", "Safety Equipment", "Microscopes", "Computers"]
                elif room_type == "gym":
                    equipment = ["Basketball Hoops", "Mats", "Exercise Equipment"]
                elif room_type == "library":
                    equipment = ["Bookshelves", "Reading Tables", "Computers", "Catalog System"]
                elif room_type == "office":
                    equipment = ["Desk", "Computer", "Filing Cabinet", "Phone"]

                # Set features
                features = []
                if self.faker.boolean(chance_of_getting_true=60):
                    features.append("Air Conditioning")
                if self.faker.boolean(chance_of_getting_true=40):
                    features.append("Natural Light")
                if room_type in ["classroom", "lab"]:
                    if self.faker.boolean(chance_of_getting_true=70):
                        features.append("Smart Board")

                room_data = {
                    "school_id": school_id,
                    "room_number": str(room_number_counter),
                    "building": building,
                    "floor": floor,
                    "room_type": room_type,
                    "room_name": f"{room_type.title()} {room_number_counter}",
                    "capacity": capacity,
                    "equipment": equipment,
                    "features": features,
                    "is_active": True,
                    "is_available": True,
                }

                room = self.client.create_room(room_data)
                self.cache.add_entity("room", room["id"], room)
                rooms.append(room)

                room_number_counter += 1

        self._log_progress(f"✓ Created {len(rooms)} rooms")

        return rooms
