<template>
  <div class="class-form-container">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            {{ isEditMode ? 'Edit Class' : 'Create Class' }}
          </h1>
          <p class="mt-1 text-sm text-gray-500">
            {{ isEditMode ? 'Update class information and settings' : 'Create a new class section' }}
          </p>
        </div>
        <router-link
          to="/classes"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to List
        </router-link>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Information Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <!-- Subject -->
          <div class="sm:col-span-2">
            <label for="subject" class="block text-sm font-medium text-gray-700">
              Subject <span class="text-red-500">*</span>
            </label>
            <select
              id="subject"
              v-model="form.subject_id"
              @change="updateCodePreview"
              required
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              :class="{ 'border-red-500': errors.subject_id }"
            >
              <option value="">Select a subject</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }} ({{ subject.code }})
              </option>
            </select>
            <p v-if="errors.subject_id" class="mt-1 text-sm text-red-600">{{ errors.subject_id }}</p>
          </div>

          <!-- Class Name -->
          <div class="sm:col-span-2">
            <label for="name" class="block text-sm font-medium text-gray-700">
              Class Name <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              v-model="form.name"
              required
              class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              :class="{ 'border-red-500': errors.name }"
              placeholder="e.g., Mathematics Grade 5 Quarter 1 Section A"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Grade Level -->
          <div>
            <label for="grade" class="block text-sm font-medium text-gray-700">
              Grade Level <span class="text-red-500">*</span>
            </label>
            <select
              id="grade"
              v-model.number="form.grade_level"
              @change="updateCodePreview"
              required
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              :class="{ 'border-red-500': errors.grade_level }"
            >
              <option value="">Select grade</option>
              <option v-for="grade in GRADE_LEVELS" :key="grade" :value="grade">
                Grade {{ grade }}
              </option>
            </select>
            <p v-if="errors.grade_level" class="mt-1 text-sm text-red-600">{{ errors.grade_level }}</p>
          </div>

          <!-- Quarter -->
          <div>
            <label for="quarter" class="block text-sm font-medium text-gray-700">
              Quarter <span class="text-red-500">*</span>
            </label>
            <select
              id="quarter"
              v-model="form.quarter"
              @change="updateCodePreview"
              required
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              :class="{ 'border-red-500': errors.quarter }"
            >
              <option value="">Select quarter</option>
              <option v-for="quarter in QUARTERS" :key="quarter" :value="quarter">
                {{ getQuarterLabel(quarter) }}
              </option>
            </select>
            <p v-if="errors.quarter" class="mt-1 text-sm text-red-600">{{ errors.quarter }}</p>
          </div>

          <!-- Academic Year -->
          <div>
            <label for="year" class="block text-sm font-medium text-gray-700">
              Academic Year <span class="text-red-500">*</span>
            </label>
            <select
              id="year"
              v-model="form.academic_year"
              required
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              :class="{ 'border-red-500': errors.academic_year }"
            >
              <option value="">Select year</option>
              <option :value="getPreviousAcademicYear()">{{ getPreviousAcademicYear() }}</option>
              <option :value="getCurrentAcademicYear()">{{ getCurrentAcademicYear() }} (Current)</option>
              <option :value="getNextAcademicYear()">{{ getNextAcademicYear() }}</option>
            </select>
            <p v-if="errors.academic_year" class="mt-1 text-sm text-red-600">{{ errors.academic_year }}</p>
          </div>

          <!-- Section -->
          <div>
            <label for="section" class="block text-sm font-medium text-gray-700">
              Section <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="section"
              v-model="section"
              @input="updateCodePreview"
              required
              maxlength="5"
              class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md uppercase"
              placeholder="e.g., A, B, 1, 2"
            />
            <p class="mt-1 text-xs text-gray-500">Single letter or number to identify the section</p>
          </div>

          <!-- Class Code (Preview) -->
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700">
              Class Code Preview
            </label>
            <div class="mt-1 px-4 py-2 bg-gray-50 border border-gray-300 rounded-md">
              <code class="text-sm font-mono text-gray-900">
                {{ codePreview || 'Select subject, grade, quarter, and section' }}
              </code>
            </div>
          </div>

          <!-- Description -->
          <div class="sm:col-span-2">
            <label for="description" class="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="description"
              v-model="form.description"
              rows="3"
              class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              placeholder="Optional description of the class"
            />
          </div>
        </div>
      </div>

      <!-- Assignment Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Assignments</h2>
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <!-- Teacher -->
          <div class="sm:col-span-2">
            <label for="teacher" class="block text-sm font-medium text-gray-700">
              Teacher <span class="text-red-500">*</span>
            </label>
            <select
              id="teacher"
              v-model="form.teacher_id"
              required
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              :class="{ 'border-red-500': errors.teacher_id }"
            >
              <option value="">Select a teacher</option>
              <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                {{ teacher.full_name }} - {{ teacher.specialization || 'General' }}
              </option>
            </select>
            <p v-if="errors.teacher_id" class="mt-1 text-sm text-red-600">{{ errors.teacher_id }}</p>
          </div>

          <!-- Room -->
          <div class="sm:col-span-2">
            <label for="room" class="block text-sm font-medium text-gray-700">
              Room (Optional)
            </label>
            <select
              id="room"
              v-model="form.room_id"
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option :value="null">No room assigned</option>
              <option v-for="room in rooms" :key="room.id" :value="room.id">
                {{ room.room_number }} - {{ room.name }} ({{ room.room_type }})
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Capacity Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Capacity</h2>
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <!-- Max Students -->
          <div>
            <label for="max_students" class="block text-sm font-medium text-gray-700">
              Maximum Students <span class="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="max_students"
              v-model.number="form.max_students"
              required
              min="1"
              max="100"
              class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              :class="{ 'border-red-500': errors.max_students }"
            />
            <p v-if="errors.max_students" class="mt-1 text-sm text-red-600">{{ errors.max_students }}</p>
          </div>

          <!-- Current Enrollment (Read-only for edit mode) -->
          <div v-if="isEditMode">
            <label class="block text-sm font-medium text-gray-700">
              Current Enrollment
            </label>
            <div class="mt-1 px-4 py-2 bg-gray-50 border border-gray-300 rounded-md">
              <span class="text-sm text-gray-900">{{ initialClass?.current_enrollment || 0 }} students</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Schedule Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Schedule (Optional)</h2>

        <div class="mb-4">
          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="hasSchedule"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm text-gray-700">Add class schedule</span>
          </label>
        </div>

        <div v-if="hasSchedule" class="space-y-4">
          <!-- Days -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Days <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <label
                v-for="day in VALID_DAYS"
                :key="day"
                class="flex items-center p-2 border rounded-md cursor-pointer hover:bg-gray-50"
                :class="schedule.days.includes(day) ? 'bg-indigo-50 border-indigo-500' : 'border-gray-300'"
              >
                <input
                  type="checkbox"
                  :value="day"
                  v-model="schedule.days"
                  class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700">{{ day }}</span>
              </label>
            </div>
          </div>

          <!-- Times -->
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label for="start_time" class="block text-sm font-medium text-gray-700">
                Start Time <span class="text-red-500">*</span>
              </label>
              <input
                type="time"
                id="start_time"
                v-model="schedule.start_time"
                required
                class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label for="end_time" class="block text-sm font-medium text-gray-700">
                End Time <span class="text-red-500">*</span>
              </label>
              <input
                type="time"
                id="end_time"
                v-model="schedule.end_time"
                required
                class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
              />
            </div>
          </div>

          <!-- Schedule Preview -->
          <div v-if="schedulePreview">
            <label class="block text-sm font-medium text-gray-700">Preview</label>
            <div class="mt-1 px-4 py-2 bg-gray-50 border border-gray-300 rounded-md">
              <span class="text-sm text-gray-900">{{ schedulePreview }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Display Settings Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Display Settings</h2>
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <!-- Color -->
          <div>
            <label for="color" class="block text-sm font-medium text-gray-700">
              Color
            </label>
            <div class="mt-1 flex items-center space-x-2">
              <input
                type="color"
                id="color"
                v-model="form.color"
                class="h-10 w-20 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                v-model="form.color"
                pattern="^#[0-9A-Fa-f]{6}$"
                class="focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                placeholder="#3B82F6"
              />
              <button
                type="button"
                @click="form.color = null"
                class="px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50"
              >
                Clear
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-500">Optional color for visual identification</p>
          </div>

          <!-- Display Order -->
          <div>
            <label for="display_order" class="block text-sm font-medium text-gray-700">
              Display Order
            </label>
            <input
              type="number"
              id="display_order"
              v-model.number="form.display_order"
              min="0"
              class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            />
            <p class="mt-1 text-xs text-gray-500">Lower numbers appear first (default: 0)</p>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex justify-end space-x-3">
        <router-link
          to="/classes"
          class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </router-link>
        <button
          type="submit"
          :disabled="isLoading"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isLoading ? 'Saving...' : (isEditMode ? 'Update Class' : 'Create Class') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useClassStore } from '@/stores/classStore';
import { useSchool } from '@/composables/useSchool'
import {
  QUARTERS,
  GRADE_LEVELS,
  VALID_DAYS,
  getQuarterLabel,
  getCurrentAcademicYear,
  getNextAcademicYear,
  getPreviousAcademicYear,
  generateClassCode,
  formatScheduleDetailed,
  getDefaultSchedule
} from '@/types/class';
import type { ClassCreateInput, Schedule, Quarter } from '@/types/class';

const route = useRoute();
const router = useRouter();
const classStore = useClassStore();
const { currentSchoolId } = useSchool();

const isEditMode = computed(() => !!route.params.id);
const isLoading = computed(() => classStore.isLoading);
const error = computed(() => classStore.error);
const initialClass = computed(() => classStore.selectedClass);

// Form data
const section = ref('A');
const hasSchedule = ref(false);

const form = ref<ClassCreateInput>({
  code: '',
  name: '',
  subject_id: '',
  teacher_id: '',
  room_id: null,
  grade_level: 0,
  quarter: '' as Quarter,
  academic_year: getCurrentAcademicYear(),
  max_students: 30,
  description: null,
  schedule: null,
  color: '#3B82F6',
  display_order: 0
});

const schedule = ref<Schedule>({
  days: [],
  start_time: '09:00',
  end_time: '10:30'
});

const errors = ref<Record<string, string>>({});

// Mock data - Replace with actual API calls
const subjects = ref([
  { id: '94473bd5-c1de-4e8c-9ef3-bde10cacc143', code: 'MATH', name: 'Mathematics' },
  { id: 'subject-2', code: 'ELA', name: 'English Language Arts' },
  { id: 'subject-3', code: 'SCI', name: 'Science' },
  { id: 'subject-4', code: 'SS', name: 'Social Studies' }
]);

const teachers = ref([
  { id: 'fa4a570e-6ced-42e8-ab2f-beaf59b11a89', full_name: 'John Smith', specialization: 'Mathematics' },
  { id: 'teacher-2', full_name: 'Jane Doe', specialization: 'Science' }
]);

const rooms = ref([
  { id: 'de1b92cc-282b-4387-ae03-20fa18366c6d', room_number: '101', name: 'Main Classroom', room_type: 'classroom' },
  { id: 'room-2', room_number: '102', name: 'Science Lab', room_type: 'lab' }
]);

const codePreview = computed(() => {
  const selectedSubject = subjects.value.find(s => s.id === form.value.subject_id);
  if (!selectedSubject || !form.value.grade_level || !form.value.quarter || !section.value) {
    return '';
  }

  return generateClassCode(
    selectedSubject.code,
    form.value.grade_level,
    form.value.quarter,
    section.value
  );
});

const schedulePreview = computed(() => {
  if (!hasSchedule.value || schedule.value.days.length === 0) {
    return '';
  }

  return formatScheduleDetailed(schedule.value);
});

onMounted(async () => {
  if (isEditMode.value) {
    await loadClass();
  }
});

async function loadClass() {
  const classId = route.params.id as string;
  await classStore.fetchClassById(classId);

  if (initialClass.value) {
    // Parse code to get section
    const codeParts = initialClass.value.code.split('-');
    if (codeParts.length === 4) {
      section.value = codeParts[3];
    }

    // Populate form
    form.value = {
      code: initialClass.value.code,
      name: initialClass.value.name,
      subject_id: initialClass.value.subject_id,
      teacher_id: initialClass.value.teacher_id,
      room_id: initialClass.value.room_id,
      grade_level: initialClass.value.grade_level,
      quarter: initialClass.value.quarter,
      academic_year: initialClass.value.academic_year,
      max_students: initialClass.value.max_students,
      description: initialClass.value.description,
      schedule: initialClass.value.schedule,
      color: initialClass.value.color,
      display_order: initialClass.value.display_order
    };

    // Populate schedule
    if (initialClass.value.schedule) {
      hasSchedule.value = true;
      schedule.value = { ...initialClass.value.schedule };
    }
  }
}

function updateCodePreview() {
  // Just trigger reactivity
  form.value.code = codePreview.value;
}

watch(hasSchedule, (value) => {
  if (value && schedule.value.days.length === 0) {
    const defaultSchedule = getDefaultSchedule();
    schedule.value = { ...defaultSchedule };
  }
});

function validateForm(): boolean {
  errors.value = {};

  if (!form.value.subject_id) {
    errors.value.subject_id = 'Subject is required';
  }

  if (!form.value.name.trim()) {
    errors.value.name = 'Class name is required';
  }

  if (!form.value.grade_level || form.value.grade_level < 1 || form.value.grade_level > 7) {
    errors.value.grade_level = 'Grade level must be between 1 and 7';
  }

  if (!form.value.quarter) {
    errors.value.quarter = 'Quarter is required';
  }

  if (!form.value.academic_year) {
    errors.value.academic_year = 'Academic year is required';
  }

  if (!form.value.teacher_id) {
    errors.value.teacher_id = 'Teacher is required';
  }

  if (!form.value.max_students || form.value.max_students < 1) {
    errors.value.max_students = 'Maximum students must be at least 1';
  }

  return Object.keys(errors.value).length === 0;
}

async function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  // Update code from preview
  form.value.code = codePreview.value;

  // Set schedule if enabled
  if (hasSchedule.value && schedule.value.days.length > 0) {
    form.value.schedule = { ...schedule.value };
  } else {
    form.value.schedule = null;
  }

  try {
    if (!currentSchoolId.value) {
      console.error('Cannot save class: no school selected');
      return;
    }

    if (isEditMode.value) {
      await classStore.updateClass(route.params.id as string, form.value);
    } else {
      await classStore.createClass(currentSchoolId.value, form.value);
    }

    router.push('/classes');
  } catch (err: any) {
    console.error('Failed to save class:', err);
  }
}
</script>

<style scoped>
.class-form-container {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}
</style>
