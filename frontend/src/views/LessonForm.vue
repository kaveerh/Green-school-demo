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

        <div class="form-group">
          <label for="class_id" class="required">Class</label>
          <input
            id="class_id"
            v-model="formData.class_id"
            type="text"
            required
            placeholder="Class ID"
            class="form-control"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="teacher_id" class="required">Teacher</label>
            <input
              id="teacher_id"
              v-model="formData.teacher_id"
              type="text"
              required
              placeholder="Teacher ID"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="subject_id" class="required">Subject</label>
            <input
              id="subject_id"
              v-model="formData.subject_id"
              type="text"
              required
              placeholder="Subject ID"
              class="form-control"
            />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLessonStore } from '@/stores/lessonStore'
import type { LessonCreateRequest } from '@/types/lesson'

const router = useRouter()
const route = useRoute()
const lessonStore = useLessonStore()

const submitting = ref(false)
const currentSchoolId = ref('60da2256-81fc-4ca5-bf6b-467b8d371c61') // TODO: Get from auth/school context

const isEdit = computed(() => !!route.params.id)
const lessonId = computed(() => route.params.id as string)

const formData = reactive<LessonCreateRequest>({
  title: '',
  description: '',
  class_id: '2e008ff4-dc05-4c6b-8059-ca92fceb3f9a', // TODO: Make dynamic
  teacher_id: 'fa4a570e-6ced-42e8-ab2f-beaf59b11a89', // TODO: Make dynamic
  subject_id: '94473bd5-c1de-4e8c-9ef3-bde10cacc143', // TODO: Make dynamic
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
  submitting.value = true

  try {
    if (isEdit.value) {
      await lessonStore.updateLesson(lessonId.value, formData)
      alert('Lesson updated successfully!')
    } else {
      await lessonStore.createLesson(currentSchoolId.value, formData)
      alert('Lesson created successfully!')
    }
    router.push('/lessons')
  } catch (err) {
    console.error('Failed to save lesson:', err)
    alert('Failed to save lesson. Please try again.')
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
</style>
