/**
 * Class Service
 *
 * API client for Class operations
 */

import type {
  Class,
  ClassCreateInput,
  ClassUpdateInput,
  ClassSearchParams,
  ClassStatistics,
  StudentClass,
  EnrollmentCreateInput,
  EnrollmentUpdateGradesInput,
  EnrollmentCompleteInput,
  Quarter
} from '@/types/class';

const API_BASE = 'http://localhost:8000/api/v1/classes';

interface PaginatedResponse<T> {
  classes?: T[];
  enrollments?: StudentClass[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ============================================================================
// Class API Methods
// ============================================================================

export async function createClass(
  schoolId: string,
  data: ClassCreateInput
): Promise<Class> {
  const response = await fetch(`${API_BASE}?school_id=${schoolId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create class');
  }

  return response.json();
}

export async function getClasses(
  params: ClassSearchParams
): Promise<PaginatedResponse<Class>> {
  const queryParams = new URLSearchParams();
  queryParams.append('school_id', params.school_id);

  if (params.page) queryParams.append('page', params.page.toString());
  if (params.limit) queryParams.append('limit', params.limit.toString());
  if (params.subject_id) queryParams.append('subject_id', params.subject_id);
  if (params.teacher_id) queryParams.append('teacher_id', params.teacher_id);
  if (params.room_id) queryParams.append('room_id', params.room_id);
  if (params.grade_level) queryParams.append('grade_level', params.grade_level.toString());
  if (params.quarter) queryParams.append('quarter', params.quarter);
  if (params.academic_year) queryParams.append('academic_year', params.academic_year);
  if (params.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());

  const response = await fetch(`${API_BASE}?${queryParams}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch classes');
  }

  return response.json();
}

export async function getClassById(classId: string): Promise<Class> {
  const response = await fetch(`${API_BASE}/${classId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch class');
  }

  return response.json();
}

export async function getClassByCode(
  schoolId: string,
  code: string
): Promise<Class> {
  const response = await fetch(`${API_BASE}/code/${code}?school_id=${schoolId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch class');
  }

  return response.json();
}

export async function searchClasses(
  schoolId: string,
  query: string,
  page: number = 1,
  limit: number = 50
): Promise<PaginatedResponse<Class>> {
  const queryParams = new URLSearchParams({
    school_id: schoolId,
    query,
    page: page.toString(),
    limit: limit.toString()
  });

  const response = await fetch(`${API_BASE}/search?${queryParams}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to search classes');
  }

  return response.json();
}

export async function updateClass(
  classId: string,
  data: ClassUpdateInput
): Promise<Class> {
  const response = await fetch(`${API_BASE}/${classId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update class');
  }

  return response.json();
}

export async function deleteClass(classId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/${classId}`, {
    method: 'DELETE'
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete class');
  }
}

export async function toggleClassStatus(classId: string): Promise<Class> {
  const response = await fetch(`${API_BASE}/${classId}/status`, {
    method: 'PATCH'
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to toggle class status');
  }

  return response.json();
}

export async function getClassStatistics(
  schoolId?: string
): Promise<ClassStatistics> {
  const queryParams = schoolId
    ? new URLSearchParams({ school_id: schoolId })
    : '';

  const response = await fetch(`${API_BASE}/statistics${queryParams ? '?' + queryParams : ''}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch statistics');
  }

  return response.json();
}

export async function getClassesByTeacher(
  schoolId: string,
  teacherId: string,
  quarter?: Quarter,
  academicYear?: string
): Promise<Class[]> {
  const queryParams = new URLSearchParams({ school_id: schoolId });
  if (quarter) queryParams.append('quarter', quarter);
  if (academicYear) queryParams.append('academic_year', academicYear);

  const response = await fetch(`${API_BASE}/teacher/${teacherId}?${queryParams}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch teacher classes');
  }

  return response.json();
}

export async function getClassesBySubject(
  schoolId: string,
  subjectId: string,
  gradeLevel?: number,
  quarter?: Quarter
): Promise<Class[]> {
  const queryParams = new URLSearchParams({ school_id: schoolId });
  if (gradeLevel) queryParams.append('grade_level', gradeLevel.toString());
  if (quarter) queryParams.append('quarter', quarter);

  const response = await fetch(`${API_BASE}/subject/${subjectId}?${queryParams}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch subject classes');
  }

  return response.json();
}

export async function getClassesByRoom(
  schoolId: string,
  roomId: string
): Promise<Class[]> {
  const queryParams = new URLSearchParams({ school_id: schoolId });

  const response = await fetch(`${API_BASE}/room/${roomId}?${queryParams}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch room classes');
  }

  return response.json();
}

// ============================================================================
// Student Enrollment API Methods
// ============================================================================

export async function enrollStudent(
  data: EnrollmentCreateInput
): Promise<StudentClass> {
  const response = await fetch(`${API_BASE}/enrollments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to enroll student');
  }

  return response.json();
}

export async function getEnrollmentById(
  enrollmentId: string
): Promise<StudentClass> {
  const response = await fetch(`${API_BASE}/enrollments/${enrollmentId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch enrollment');
  }

  return response.json();
}

export async function getStudentsInClass(
  classId: string
): Promise<{ enrollments: StudentClass[]; total: number }> {
  const response = await fetch(`${API_BASE}/${classId}/students`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch students');
  }

  return response.json();
}

export async function getClassesForStudent(
  studentId: string,
  status?: string
): Promise<{ enrollments: StudentClass[]; total: number }> {
  const queryParams = status
    ? new URLSearchParams({ status })
    : '';

  const response = await fetch(`${API_BASE}/students/${studentId}/classes${queryParams ? '?' + queryParams : ''}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch student classes');
  }

  return response.json();
}

export async function dropStudent(enrollmentId: string): Promise<StudentClass> {
  const response = await fetch(`${API_BASE}/enrollments/${enrollmentId}/drop`, {
    method: 'PATCH'
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to drop student');
  }

  return response.json();
}

export async function withdrawStudent(enrollmentId: string): Promise<StudentClass> {
  const response = await fetch(`${API_BASE}/enrollments/${enrollmentId}/withdraw`, {
    method: 'PATCH'
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to withdraw student');
  }

  return response.json();
}

export async function completeEnrollment(
  enrollmentId: string,
  data: EnrollmentCompleteInput
): Promise<StudentClass> {
  const response = await fetch(`${API_BASE}/enrollments/${enrollmentId}/complete`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to complete enrollment');
  }

  return response.json();
}

export async function updateEnrollmentGrades(
  enrollmentId: string,
  data: EnrollmentUpdateGradesInput
): Promise<StudentClass> {
  const response = await fetch(`${API_BASE}/enrollments/${enrollmentId}/grades`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update grades');
  }

  return response.json();
}

export async function deleteEnrollment(enrollmentId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/enrollments/${enrollmentId}`, {
    method: 'DELETE'
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete enrollment');
  }
}
