<template>
  <div class="lesson-form-container">
    <div class="header">
      <h1 class="title">{{ isEdit ? 'Edit Lesson' : 'Create Lesson' }}</h1>
      <router-link to="/lessons" class="btn btn-secondary">Back to List</router-link>
    </div>

    <form @submit.prevent="handleSubmit" class="lesson-form">
      <!-- Basic Information -->
      <div class="form-section">
        <h2 class="section-title">Basic Information</h2>

        <div class="form-group">
          <label for="title" class="required">Title</label>
          <input
            id="title"
            v-model="formData.title"
            type="text"
            required
            maxlength="200"
            placeholder="Enter lesson title"
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="3"
            placeholder="Enter lesson description"
            class="form-control"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="scheduled_date" class="required">Scheduled Date</label>
            <input
              id="scheduled_date"
              v-model="formData.scheduled_date"
              type="date"
              required
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="duration_minutes" class="required">Duration (minutes)</label>
            <input
              id="duration_minutes"
              v-model.number="formData.duration_minutes"
              type="number"
              min="1"
              max="240"
              required
              class="form-control"
            />
          </div>
        </div>

        <!-- Class Search -->
        <div class="form-group">
          <label for="class_search" class="required">Class</label>
          <div class="search-wrapper">
            <input
              id="class_search"
              v-model="classSearchQuery"
              @input="handleClassSearch"
              @focus="showClassDropdown = true"
              type="text"
              required
              placeholder="Search by class code (e.g., MATH-3-Q1-A)"
              class="form-control"
              autocomplete="off"
            />
            <div v-if="showClassDropdown && (classSearchResults.length > 0 || classSearchLoading)" class="search-dropdown">
              <div v-if="classSearchLoading" class="dropdown-loading">Searching...</div>
              <div v-else-if="classSearchResults.length > 0" class="dropdown-results">
                <div
                  v-for="classItem in classSearchResults"
                  :key="classItem.id"
                  @click="selectClass(classItem)"
                  class="dropdown-item"
                >
                  <div class="item-code">{{ classItem.code }}</div>
                  <div class="item-details">{{ classItem.name }} • Grade {{ classItem.grade_level }} • {{ classItem.quarter }}</div>
                </div>
              </div>
              <div v-else class="dropdown-empty">No classes found</div>
            </div>
          </div>
          <div v-if="selectedClass" class="selected-badge">
            <span>✓</span> {{ selectedClass.code }} - {{ selectedClass.name }}
            <button @click="clearClass" type="button" class="clear-btn">×</button>
          </div>
        </div>

        <div class="form-row">
          <!-- Teacher Search -->
          <div class="form-group">
            <label for="teacher_search" class="required">Teacher</label>
            <div class="search-wrapper">
              <input
                id="teacher_search"
                v-model="teacherSearchQuery"
                @input="handleTeacherSearch"
                @focus="showTeacherDropdown = true"
                type="text"
                required
                placeholder="Search by employee ID"
                class="form-control"
                autocomplete="off"
              />
              <div v-if="showTeacherDropdown && (teacherSearchResults.length > 0 || teacherSearchLoading)" class="search-dropdown">
                <div v-if="teacherSearchLoading" class="dropdown-loading">Searching...</div>
                <div v-else-if="teacherSearchResults.length > 0" class="dropdown-results">
                  <div
                    v-for="teacher in teacherSearchResults"
                    :key="teacher.id"
                    @click="selectTeacher(teacher)"
                    class="dropdown-item"
                  >
                    <div class="item-code">{{ teacher.employee_id }}</div>
                    <div class="item-details">{{ teacher.user?.name || 'No name' }} • {{ teacher.department || 'No dept' }}</div>
                  </div>
                </div>
                <div v-else class="dropdown-empty">No teachers found</div>
              </div>
            </div>
            <div v-if="selectedTeacher" class="selected-badge">
              <span>✓</span> {{ selectedTeacher.employee_id }} - {{ selectedTeacher.user?.name || 'No name' }}
              <button @click="clearTeacher" type="button" class="clear-btn">×</button>
            </div>
          </div>

          <!-- Subject Search -->
          <div class="form-group">
            <label for="subject_search" class="required">Subject</label>
            <div class="search-wrapper">
              <input
                id="subject_search"
                v-model="subjectSearchQuery"
                @input="handleSubjectSearch"
                @focus="showSubjectDropdown = true"
                type="text"
                required
                placeholder="Search by subject code (e.g., MATH)"
                class="form-control"
                autocomplete="off"
              />
              <div v-if="showSubjectDropdown && (subjectSearchResults.length > 0 || subjectSearchLoading)" class="search-dropdown">
                <div v-if="subjectSearchLoading" class="dropdown-loading">Searching...</div>
                <div v-else-if="subjectSearchResults.length > 0" class="dropdown-results">
                  <div
                    v-for="subject in subjectSearchResults"
                    :key="subject.id"
                    @click="selectSubject(subject)"
                    class="dropdown-item"
                  >
                    <div class="item-code">{{ subject.code }}</div>
                    <div class="item-details">{{ subject.name }}</div>
                  </div>
                </div>
                <div v-else class="dropdown-empty">No subjects found</div>
              </div>
            </div>
            <div v-if="selectedSubject" class="selected-badge">
              <span>✓</span> {{ selectedSubject.code }} - {{ selectedSubject.name }}
              <button @click="clearSubject" type="button" class="clear-btn">×</button>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="color">Color (for calendar)</label>
          <input
            id="color"
            v-model="formData.color"
            type="color"
            class="form-control color-input"
          />
        </div>
      </div>

      <!-- Lesson Plan -->
      <div class="form-section">
        <h2 class="section-title">Lesson Plan</h2>

        <div class="form-group">
          <label for="introduction">Introduction</label>
          <textarea
            id="introduction"
            v-model="formData.introduction"
            rows="3"
            placeholder="Describe how you'll introduce the topic..."
            class="form-control"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="main_activity">Main Activity</label>
          <textarea
            id="main_activity"
            v-model="formData.main_activity"
            rows="4"
            placeholder="Describe the main learning activity..."
            class="form-control"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="assessment">Assessment</label>
          <textarea
            id="assessment"
            v-model="formData.assessment"
            rows="3"
            placeholder="How will you assess student understanding?"
            class="form-control"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="homework">Homework</label>
          <textarea
            id="homework"
            v-model="formData.homework"
            rows="2"
            placeholder="Homework assignments..."
            class="form-control"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="notes">Notes</label>
          <textarea
            id="notes"
            v-model="formData.notes"
            rows="2"
            placeholder="Additional notes..."
            class="form-control"
          ></textarea>
        </div>
      </div>

      <!-- Learning Objectives -->
      <div class="form-section">
        <h2 class="section-title">Learning Objectives</h2>
        <div v-for="(objective, index) in formData.learning_objectives" :key="index" class="array-item">
          <input
            v-model="formData.learning_objectives[index]"
            type="text"
            placeholder="Learning objective..."
            class="form-control"
          />
          <button type="button" @click="removeObjective(index)" class="btn btn-sm btn-danger">
            Remove
          </button>
        </div>
        <button type="button" @click="addObjective" class="btn btn-sm btn-secondary">
          Add Objective
        </button>
      </div>

      <!-- Materials Needed -->
      <div class="form-section">
        <h2 class="section-title">Materials Needed</h2>
        <div v-for="(material, index) in formData.materials_needed" :key="index" class="array-item">
          <input
            v-model="formData.materials_needed[index]"
            type="text"
            placeholder="Material needed..."
            class="form-control"
          />
          <button type="button" @click="removeMaterial(index)" class="btn btn-sm btn-danger">
            Remove
          </button>
        </div>
        <button type="button" @click="addMaterial" class="btn btn-sm btn-secondary">
          Add Material
        </button>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="submit" :disabled="submitting" class="btn btn-primary">
          {{ submitting ? 'Saving...' : (isEdit ? 'Update Lesson' : 'Create Lesson') }}
        </button>
        <router-link to="/lessons" class="btn btn-secondary">Cancel</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLessonStore } from '@/stores/lessonStore'
import { useClassStore } from '@/stores/classStore'
import { useSchool } from '@/composables/useSchool'
import { teacherService } from '@/services/teacherService'
import { subjectService } from '@/services/subjectService'
import type { LessonCreateRequest } from '@/types/lesson'
import type { Class } from '@/types/class'
import type { Teacher } from '@/types/teacher'
import type { Subject } from '@/types/subject'

const router = useRouter()
const route = useRoute()
const lessonStore = useLessonStore()
const classStore = useClassStore()
const { currentSchoolId } = useSchool()

const submitting = ref(false)

const isEdit = computed(() => !!route.params.id)
const lessonId = computed(() => route.params.id as string)

// Class search state
const classSearchQuery = ref('')
const classSearchResults = ref<Class[]>([])
const classSearchLoading = ref(false)
const showClassDropdown = ref(false)
const selectedClass = ref<Class | null>(null)
let classSearchTimeout: ReturnType<typeof setTimeout> | null = null

// Teacher search state
const teacherSearchQuery = ref('')
const teacherSearchResults = ref<Teacher[]>([])
const teacherSearchLoading = ref(false)
const showTeacherDropdown = ref(false)
const selectedTeacher = ref<Teacher | null>(null)
let teacherSearchTimeout: ReturnType<typeof setTimeout> | null = null

// Subject search state
const subjectSearchQuery = ref('')
const subjectSearchResults = ref<Subject[]>([])
const subjectSearchLoading = ref(false)
const showSubjectDropdown = ref(false)
const selectedSubject = ref<Subject | null>(null)
let subjectSearchTimeout: ReturnType<typeof setTimeout> | null = null

const formData = reactive<LessonCreateRequest>({
  title: '',
  description: '',
  class_id: '',
  teacher_id: '',
  subject_id: '',
  scheduled_date: new Date().toISOString().split('T')[0],
  duration_minutes: 45,
  learning_objectives: [],
  materials_needed: [],
  curriculum_standards: [],
  introduction: '',
  main_activity: '',
  assessment: '',
  homework: '',
  notes: '',
  links: [],
  color: '#2563eb'
})

// Class search handlers
async function handleClassSearch() {
  if (classSearchTimeout) clearTimeout(classSearchTimeout)

  const query = classSearchQuery.value.trim()
  if (query.length < 2) {
    classSearchResults.value = []
    showClassDropdown.value = false
    return
  }

  classSearchTimeout = setTimeout(async () => {
    classSearchLoading.value = true
    showClassDropdown.value = true
    try {
      await classStore.searchClasses(currentSchoolId.value, query, 1, 20)
      classSearchResults.value = classStore.classes
    } catch (error) {
      console.error('Failed to search classes:', error)
      classSearchResults.value = []
    } finally {
      classSearchLoading.value = false
    }
  }, 300)
}

function selectClass(classItem: Class) {
  selectedClass.value = classItem
  formData.class_id = classItem.id
  classSearchQuery.value = classItem.code
  showClassDropdown.value = false
  classSearchResults.value = []
}

function clearClass() {
  selectedClass.value = null
  formData.class_id = ''
  classSearchQuery.value = ''
  classSearchResults.value = []
}

// Teacher search handlers
async function handleTeacherSearch() {
  if (teacherSearchTimeout) clearTimeout(teacherSearchTimeout)

  const query = teacherSearchQuery.value.trim()
  if (query.length < 2) {
    teacherSearchResults.value = []
    showTeacherDropdown.value = false
    return
  }

  teacherSearchTimeout = setTimeout(async () => {
    teacherSearchLoading.value = true
    showTeacherDropdown.value = true
    try {
      const response = await teacherService.searchTeachers(query, {
        page: 1,
        limit: 20,
        status: 'active'
      })
      teacherSearchResults.value = response.teachers || []
    } catch (error) {
      console.error('Failed to search teachers:', error)
      teacherSearchResults.value = []
    } finally {
      teacherSearchLoading.value = false
    }
  }, 300)
}

function selectTeacher(teacher: Teacher) {
  selectedTeacher.value = teacher
  formData.teacher_id = teacher.id
  teacherSearchQuery.value = teacher.employee_id
  showTeacherDropdown.value = false
  teacherSearchResults.value = []
}

function clearTeacher() {
  selectedTeacher.value = null
  formData.teacher_id = ''
  teacherSearchQuery.value = ''
  teacherSearchResults.value = []
}

// Subject search handlers
async function handleSubjectSearch() {
  if (subjectSearchTimeout) clearTimeout(subjectSearchTimeout)

  const query = subjectSearchQuery.value.trim()
  if (query.length < 2) {
    subjectSearchResults.value = []
    showSubjectDropdown.value = false
    return
  }

  subjectSearchTimeout = setTimeout(async () => {
    subjectSearchLoading.value = true
    showSubjectDropdown.value = true
    try {
      const response = await subjectService.searchSubjects(query, {
        school_id: currentSchoolId.value,
        page: 1,
        limit: 20,
        is_active: true
      })
      subjectSearchResults.value = response.subjects || []
    } catch (error) {
      console.error('Failed to search subjects:', error)
      subjectSearchResults.value = []
    } finally {
      subjectSearchLoading.value = false
    }
  }, 300)
}

function selectSubject(subject: Subject) {
  selectedSubject.value = subject
  formData.subject_id = subject.id
  subjectSearchQuery.value = subject.code
  showSubjectDropdown.value = false
  subjectSearchResults.value = []
}

function clearSubject() {
  selectedSubject.value = null
  formData.subject_id = ''
  subjectSearchQuery.value = ''
  subjectSearchResults.value = []
}

// Close dropdowns when clicking outside
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.search-wrapper')) {
    showClassDropdown.value = false
    showTeacherDropdown.value = false
    showSubjectDropdown.value = false
  }
}

function addObjective() {
  formData.learning_objectives?.push('')
}

function removeObjective(index: number) {
  formData.learning_objectives?.splice(index, 1)
}

function addMaterial() {
  formData.materials_needed?.push('')
}

function removeMaterial(index: number) {
  formData.materials_needed?.splice(index, 1)
}

async function handleSubmit() {
  // Validate required fields
  if (!formData.class_id || !selectedClass.value) {
    alert('Please select a class')
    return
  }

  if (!formData.teacher_id || !selectedTeacher.value) {
    alert('Please select a teacher')
    return
  }

  if (!formData.subject_id || !selectedSubject.value) {
    alert('Please select a subject')
    return
  }

  if (!formData.title.trim()) {
    alert('Please enter a lesson title')
    return
  }

  if (!formData.scheduled_date) {
    alert('Please select a scheduled date')
    return
  }

  if (!formData.duration_minutes || formData.duration_minutes < 1) {
    alert('Please enter a valid duration')
    return
  }

  submitting.value = true

  try {
    // Clean up form data - remove empty arrays and empty strings
    const cleanedData: any = {
      title: formData.title.trim(),
      class_id: formData.class_id,
      teacher_id: formData.teacher_id,
      subject_id: formData.subject_id,
      scheduled_date: formData.scheduled_date,
      duration_minutes: formData.duration_minutes
    }

    // Add optional fields only if they have values
    if (formData.description?.trim()) {
      cleanedData.description = formData.description.trim()
    }

    if (formData.learning_objectives && formData.learning_objectives.length > 0) {
      cleanedData.learning_objectives = formData.learning_objectives.filter(o => o.trim())
    }

    if (formData.materials_needed && formData.materials_needed.length > 0) {
      cleanedData.materials_needed = formData.materials_needed.filter(m => m.trim())
    }

    if (formData.curriculum_standards && formData.curriculum_standards.length > 0) {
      cleanedData.curriculum_standards = formData.curriculum_standards.filter(s => s.trim())
    }

    if (formData.introduction?.trim()) {
      cleanedData.introduction = formData.introduction.trim()
    }

    if (formData.main_activity?.trim()) {
      cleanedData.main_activity = formData.main_activity.trim()
    }

    if (formData.assessment?.trim()) {
      cleanedData.assessment = formData.assessment.trim()
    }

    if (formData.homework?.trim()) {
      cleanedData.homework = formData.homework.trim()
    }

    if (formData.notes?.trim()) {
      cleanedData.notes = formData.notes.trim()
    }

    if (formData.links && formData.links.length > 0) {
      cleanedData.links = formData.links.filter(l => l.trim())
    }

    if (formData.color) {
      cleanedData.color = formData.color
    }

    console.log('Submitting lesson data:', cleanedData)

    if (isEdit.value) {
      await lessonStore.updateLesson(lessonId.value, cleanedData)
      alert('Lesson updated successfully!')
    } else {
      await lessonStore.createLesson(currentSchoolId.value, cleanedData)
      alert('Lesson created successfully!')
    }
    router.push('/lessons')
  } catch (err: any) {
    console.error('Failed to save lesson:', err)
    const errorMessage = err?.message || 'Failed to save lesson. Please try again.'
    alert(errorMessage)
  } finally {
    submitting.value = false
  }
}

async function loadLesson() {
  if (isEdit.value) {
    try {
      const lesson = await lessonStore.fetchLessonById(lessonId.value)
      if (lesson) {
        Object.assign(formData, {
          title: lesson.title,
          description: lesson.description,
          class_id: lesson.class_id,
          teacher_id: lesson.teacher_id,
          subject_id: lesson.subject_id,
          scheduled_date: lesson.scheduled_date,
          duration_minutes: lesson.duration_minutes,
          learning_objectives: lesson.learning_objectives || [],
          materials_needed: lesson.materials_needed || [],
          curriculum_standards: lesson.curriculum_standards || [],
          introduction: lesson.introduction,
          main_activity: lesson.main_activity,
          assessment: lesson.assessment,
          homework: lesson.homework,
          notes: lesson.notes,
          links: lesson.links || [],
          color: lesson.color
        })

        // Load related entities for display
        if (lesson.class_id) {
          try {
            const classItem = await classStore.fetchClassById(lesson.class_id)
            if (classItem) {
              selectedClass.value = classItem
              classSearchQuery.value = classItem.code
            }
          } catch (err) {
            console.error('Failed to load class:', err)
          }
        }

        if (lesson.teacher_id) {
          try {
            const teacher = await teacherService.getTeacherById(lesson.teacher_id)
            if (teacher) {
              selectedTeacher.value = teacher
              teacherSearchQuery.value = teacher.employee_id
            }
          } catch (err) {
            console.error('Failed to load teacher:', err)
          }
        }

        if (lesson.subject_id) {
          try {
            const subject = await subjectService.getSubjectById(lesson.subject_id)
            if (subject) {
              selectedSubject.value = subject
              subjectSearchQuery.value = subject.code
            }
          } catch (err) {
            console.error('Failed to load subject:', err)
          }
        }
      }
    } catch (err) {
      console.error('Failed to load lesson:', err)
      alert('Failed to load lesson')
      router.push('/lessons')
    }
  }
}

onMounted(() => {
  loadLesson()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  if (classSearchTimeout) clearTimeout(classSearchTimeout)
  if (teacherSearchTimeout) clearTimeout(teacherSearchTimeout)
  if (subjectSearchTimeout) clearTimeout(subjectSearchTimeout)
})
</script>

<style scoped>
.lesson-form-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.lesson-form {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #374151;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

label.required::after {
  content: '*';
  color: #ef4444;
  margin-left: 4px;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.color-input {
  width: 100px;
  height: 40px;
  padding: 4px;
}

.array-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.array-item .form-control {
  flex: 1;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 13px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Search Dropdown Styles */
.search-wrapper {
  position: relative;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
}

.dropdown-loading,
.dropdown-empty {
  padding: 12px 16px;
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}

.dropdown-results {
  padding: 4px 0;
}

.dropdown-item {
  padding: 10px 16px;
  cursor: pointer;
  transition: background-color 0.15s;
  border-bottom: 1px solid #f3f4f6;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f9fafb;
}

.item-code {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
  margin-bottom: 2px;
}

.item-details {
  color: #6b7280;
  font-size: 12px;
}

.selected-badge {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #166534;
}

.selected-badge span {
  color: #16a34a;
  font-size: 16px;
}

.clear-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.clear-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}
</style>
