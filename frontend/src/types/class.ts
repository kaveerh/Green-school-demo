/**
 * Class Types
 *
 * TypeScript type definitions for Class management
 */

export type Quarter = 'Q1' | 'Q2' | 'Q3' | 'Q4';

export type EnrollmentStatus = 'enrolled' | 'dropped' | 'completed' | 'withdrawn';

export interface Schedule {
  days: string[];
  start_time: string;
  end_time: string;
}

export interface Class {
  id: string;
  school_id: string;
  code: string;
  name: string;
  subject_id: string;
  teacher_id: string;
  room_id: string | null;
  grade_level: number;
  quarter: Quarter;
  academic_year: string;
  max_students: number;
  current_enrollment: number;
  description: string | null;
  schedule: Schedule | null;
  is_active: boolean;
  color: string | null;
  display_order: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;

  // Computed fields
  subject_name?: string;
  subject_code?: string;
  teacher_name?: string;
  room_number?: string;
  is_full?: boolean;
  capacity_percent?: number;
  available_seats?: number;
}

export interface ClassCreateInput {
  code: string;
  name: string;
  subject_id: string;
  teacher_id: string;
  room_id?: string | null;
  grade_level: number;
  quarter: Quarter;
  academic_year: string;
  max_students: number;
  description?: string | null;
  schedule?: Schedule | null;
  color?: string | null;
  display_order?: number;
}

export interface ClassUpdateInput {
  code?: string;
  name?: string;
  subject_id?: string;
  teacher_id?: string;
  room_id?: string | null;
  grade_level?: number;
  quarter?: Quarter;
  academic_year?: string;
  max_students?: number;
  description?: string | null;
  schedule?: Schedule | null;
  color?: string | null;
  display_order?: number;
}

export interface StudentClass {
  id: string;
  student_id: string;
  class_id: string;
  enrollment_date: string;
  drop_date: string | null;
  status: EnrollmentStatus;
  final_grade: string | null;
  final_score: number | null;
  created_at: string;
  updated_at: string;

  // Computed fields
  student_name?: string;
}

export interface EnrollmentCreateInput {
  student_id: string;
  class_id: string;
  enrollment_date?: string;
}

export interface EnrollmentUpdateGradesInput {
  final_grade?: string | null;
  final_score?: number | null;
}

export interface EnrollmentCompleteInput {
  final_grade?: string | null;
  final_score?: number | null;
}

export interface ClassSearchParams {
  school_id: string;
  page?: number;
  limit?: number;
  subject_id?: string;
  teacher_id?: string;
  room_id?: string;
  grade_level?: number;
  quarter?: Quarter;
  academic_year?: string;
  is_active?: boolean;
}

export interface ClassStatistics {
  total_classes: number;
  active_classes: number;
  inactive_classes: number;
  by_grade: Record<string, number>;
  by_quarter: Record<string, number>;
  by_subject: Record<string, number>;
  total_enrollment: number;
  average_class_size: number;
  capacity_utilization: number;
}

// Helper functions
export const QUARTERS: Quarter[] = ['Q1', 'Q2', 'Q3', 'Q4'];

export const VALID_DAYS = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
] as const;

export const GRADE_LEVELS = [1, 2, 3, 4, 5, 6, 7] as const;

export function getQuarterLabel(quarter: Quarter): string {
  const labels: Record<Quarter, string> = {
    Q1: 'Quarter 1',
    Q2: 'Quarter 2',
    Q3: 'Quarter 3',
    Q4: 'Quarter 4'
  };
  return labels[quarter];
}

export function getGradeLevelLabel(grade: number): string {
  return `Grade ${grade}`;
}

export function formatAcademicYear(year: string): string {
  return `Academic Year ${year}`;
}

export function getCurrentAcademicYear(): string {
  const now = new Date();
  const month = now.getMonth(); // 0-11
  const year = now.getFullYear();

  // Academic year starts in August (month 7)
  if (month >= 7) {
    return `${year}-${year + 1}`;
  } else {
    return `${year - 1}-${year}`;
  }
}

export function getNextAcademicYear(): string {
  const current = getCurrentAcademicYear();
  const [startYear] = current.split('-').map(Number);
  return `${startYear + 1}-${startYear + 2}`;
}

export function getPreviousAcademicYear(): string {
  const current = getCurrentAcademicYear();
  const [startYear] = current.split('-').map(Number);
  return `${startYear - 1}-${startYear}`;
}

export function isValidAcademicYear(year: string): boolean {
  const pattern = /^\d{4}-\d{4}$/;
  if (!pattern.test(year)) return false;

  const [start, end] = year.split('-').map(Number);
  return end === start + 1;
}

export function generateClassCode(
  subjectCode: string,
  gradeLevel: number,
  quarter: Quarter,
  section: string
): string {
  return `${subjectCode.toUpperCase()}-${gradeLevel}-${quarter}-${section.toUpperCase()}`;
}

export function parseClassCode(code: string): {
  subjectCode: string;
  gradeLevel: number;
  quarter: Quarter;
  section: string;
} | null {
  const pattern = /^([A-Z]+)-([1-7])-(Q[1-4])-([A-Z0-9]+)$/;
  const match = code.match(pattern);

  if (!match) return null;

  return {
    subjectCode: match[1],
    gradeLevel: parseInt(match[2]),
    quarter: match[3] as Quarter,
    section: match[4]
  };
}

export function formatSchedule(schedule: Schedule | null): string {
  if (!schedule) return 'No schedule';

  const { days, start_time, end_time } = schedule;

  if (!days.length || !start_time || !end_time) {
    return 'No schedule';
  }

  // Abbreviate days
  const dayAbbr = days.map(day => day.substring(0, 3)).join(', ');

  return `${dayAbbr} • ${start_time}-${end_time}`;
}

export function formatTime(time: string): string {
  // Convert 24h to 12h format
  const [hours, minutes] = time.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
}

export function formatScheduleDetailed(schedule: Schedule | null): string {
  if (!schedule) return 'No schedule';

  const { days, start_time, end_time } = schedule;

  if (!days.length || !start_time || !end_time) {
    return 'No schedule';
  }

  const daysStr = days.join(', ');
  const startFormatted = formatTime(start_time);
  const endFormatted = formatTime(end_time);

  return `${daysStr} from ${startFormatted} to ${endFormatted}`;
}

export function getCapacityColor(percent: number): string {
  if (percent >= 100) return 'text-red-600';
  if (percent >= 90) return 'text-orange-600';
  if (percent >= 75) return 'text-yellow-600';
  return 'text-green-600';
}

export function getCapacityBadgeColor(percent: number): string {
  if (percent >= 100) return 'bg-red-100 text-red-800';
  if (percent >= 90) return 'bg-orange-100 text-orange-800';
  if (percent >= 75) return 'bg-yellow-100 text-yellow-800';
  return 'bg-green-100 text-green-800';
}

export function getEnrollmentStatusLabel(status: EnrollmentStatus): string {
  const labels: Record<EnrollmentStatus, string> = {
    enrolled: 'Enrolled',
    dropped: 'Dropped',
    completed: 'Completed',
    withdrawn: 'Withdrawn'
  };
  return labels[status];
}

export function getEnrollmentStatusColor(status: EnrollmentStatus): string {
  const colors: Record<EnrollmentStatus, string> = {
    enrolled: 'bg-green-100 text-green-800',
    dropped: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800',
    withdrawn: 'bg-gray-100 text-gray-800'
  };
  return colors[status];
}

export function isValidTime(time: string): boolean {
  const pattern = /^([01]\d|2[0-3]):([0-5]\d)$/;
  return pattern.test(time);
}

export function isValidSchedule(schedule: Schedule): boolean {
  if (!schedule.days.length) return false;
  if (!isValidTime(schedule.start_time)) return false;
  if (!isValidTime(schedule.end_time)) return false;

  // Check start < end
  const [startH, startM] = schedule.start_time.split(':').map(Number);
  const [endH, endM] = schedule.end_time.split(':').map(Number);
  const startMinutes = startH * 60 + startM;
  const endMinutes = endH * 60 + endM;

  return endMinutes > startMinutes;
}

export function getDefaultSchedule(): Schedule {
  return {
    days: ['Monday', 'Wednesday', 'Friday'],
    start_time: '09:00',
    end_time: '10:30'
  };
}

export function sortClassesByCode(classes: Class[]): Class[] {
  return [...classes].sort((a, b) => a.code.localeCompare(b.code));
}

export function sortClassesByGrade(classes: Class[]): Class[] {
  return [...classes].sort((a, b) => {
    if (a.grade_level !== b.grade_level) {
      return a.grade_level - b.grade_level;
    }
    return a.code.localeCompare(b.code);
  });
}

export function filterClassesByQuarter(classes: Class[], quarter: Quarter): Class[] {
  return classes.filter(c => c.quarter === quarter);
}

export function filterClassesByGrade(classes: Class[], grade: number): Class[] {
  return classes.filter(c => c.grade_level === grade);
}

export function filterClassesByActive(classes: Class[], active: boolean): Class[] {
  return classes.filter(c => c.is_active === active);
}

export function getClassFullName(classObj: Class): string {
  return `${classObj.code} - ${classObj.name}`;
}

export function getClassDisplayName(classObj: Class): string {
  const subjectName = classObj.subject_name || 'Unknown Subject';
  const grade = `Grade ${classObj.grade_level}`;
  const quarter = classObj.quarter;
  return `${subjectName} - ${grade} - ${quarter}`;
}

export function isClassFull(classObj: Class): boolean {
  return classObj.current_enrollment >= classObj.max_students;
}

export function canEnrollStudent(classObj: Class): boolean {
  return classObj.is_active && !isClassFull(classObj);
}

export function getAvailableSeats(classObj: Class): number {
  return Math.max(0, classObj.max_students - classObj.current_enrollment);
}
