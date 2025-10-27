"""
Attendance Generator

Generate daily attendance records for students.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
import random
from .base import BaseGenerator


class AttendanceGenerator(BaseGenerator):
    """
    Generate attendance records

    Responsibilities:
    - Create daily attendance for students
    - Use realistic attendance patterns
    - Set check-in times and statuses
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate attendance records

        Creates attendance records for each student across multiple school days.

        Args:
            count: Number of days to generate (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated attendance dictionaries
        """
        attendance_records = []
        school_id = self._get_school_id()

        # Get days from config
        attendance_days = self.config.get("data_volumes", {}).get("attendance_days", 90)

        # Get students
        students = list(self.cache.students.values())

        if not students:
            raise ValueError("No students found in cache. Generate students first.")

        # Get attendance patterns
        attendance_config = self.config.get("generation_rules", {}).get("attendance", {})
        present_rate = attendance_config.get("present_rate", 0.90)
        absent_rate = attendance_config.get("absent_rate", 0.05)
        tardy_rate = attendance_config.get("tardy_rate", 0.03)
        excused_rate = attendance_config.get("excused_rate", 0.015)
        sick_rate = attendance_config.get("sick_rate", 0.005)

        # Normalize rates
        total_rate = present_rate + absent_rate + tardy_rate + excused_rate + sick_rate
        if total_rate != 1.0:
            # Normalize
            present_rate /= total_rate
            absent_rate /= total_rate
            tardy_rate /= total_rate
            excused_rate /= total_rate
            sick_rate /= total_rate

        # Get date range
        dates_config = self.config.get("generation_rules", {}).get("dates", {})
        start_date_str = dates_config.get("academic_year_start", "2024-09-01")
        start_date = date.fromisoformat(start_date_str)

        # Generate list of school days (skip weekends)
        school_days = []
        current_date = start_date
        days_added = 0

        while days_added < attendance_days:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                school_days.append(current_date)
                days_added += 1
            current_date += timedelta(days=1)

        total_records = len(students) * len(school_days)
        self._log_progress(f"Creating {total_records} attendance records ({len(school_days)} days × {len(students)} students)")

        # Create attendance for each student for each day
        for student in students:
            # Get student's first class (homeroom)
            student_enrollments = [
                e for e in self.cache.student_classes
                if e.get("student_id") == student["id"]
            ]

            class_id = None
            if student_enrollments:
                class_id = student_enrollments[0].get("class_id")

            for school_day in school_days:
                # Determine attendance status
                status = random.choices(
                    population=["present", "absent", "tardy", "excused", "sick"],
                    weights=[present_rate, absent_rate, tardy_rate, excused_rate, sick_rate],
                    k=1
                )[0]

                # Generate check-in time
                check_in_time = None
                if status in ["present", "tardy"]:
                    base_time = "08:00:00"  # School starts at 8 AM
                    if status == "tardy":
                        # Late by 5-30 minutes
                        minutes_late = random.randint(5, 30)
                        check_in_time = f"08:{minutes_late:02d}:00"
                    else:
                        # On time or early
                        minutes_offset = random.randint(-10, 5)
                        if minutes_offset < 0:
                            check_in_time = f"07:{60 + minutes_offset:02d}:00"
                        else:
                            check_in_time = f"08:{minutes_offset:02d}:00"

                attendance_data = {
                    "school_id": school_id,
                    "student_id": student["id"],
                    "class_id": class_id,
                    "attendance_date": school_day.isoformat(),
                    "status": status,
                    "check_in_time": check_in_time,
                    "check_out_time": "15:00:00" if status == "present" else None,
                    "parent_notified": status in ["absent", "sick"],
                }

                # Add notes for absences
                if status in ["absent", "sick", "excused"]:
                    if status == "sick":
                        attendance_data["notes"] = random.choice([
                            "Called in sick",
                            "Doctor's note provided",
                            "Flu symptoms",
                            "Not feeling well"
                        ])
                    elif status == "excused":
                        attendance_data["notes"] = random.choice([
                            "Family emergency",
                            "Doctor appointment",
                            "School approved absence",
                            "Religious holiday"
                        ])

                attendance = self.client.create_attendance(attendance_data)
                self.cache.add_entity("attendance", attendance["id"], attendance)
                attendance_records.append(attendance)

        self._log_progress(f"✓ Created {len(attendance_records)} attendance records")

        return attendance_records
