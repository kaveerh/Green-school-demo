<template>
  <div class="parent-form">
    <!-- Header -->
    <div class="form-header">
      <button @click="goBack" class="btn-back">← Back to Parents</button>
      <h2>{{ isEditMode ? 'Edit Parent' : 'Create New Parent' }}</h2>
    </div>

    <!-- Loading State -->
    <div v-if="isEditMode && parentStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading parent data...</p>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="form-container">
      <!-- Error Messages -->
      <div v-if="formError" class="error-banner">
        {{ formError }}
      </div>

      <!-- User Selection -->
      <div class="form-section">
        <h3>User Account</h3>

        <div class="form-group">
          <UserSelector
            v-model="formData.user_id"
            label="Parent User Account"
            placeholder="Search for user by name or email..."
            help-text="Select the user account that will be associated with this parent"
            filter-persona="parent"
            :required="true"
            :disabled="isSubmitting || isEditMode"
            input-id="user_id"
            name="user_id"
            @select="handleUserSelect"
          />
          <small v-if="isEditMode" class="help-text">User account cannot be changed after creation</small>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="form-section">
        <h3>Contact Information</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="phone_mobile">Mobile Phone</label>
            <input
              id="phone_mobile"
              v-model="formData.phone_mobile"
              type="tel"
              :disabled="isSubmitting"
              placeholder="+1-555-0123"
            />
            <small class="help-text">Parent's primary mobile number</small>
          </div>

          <div class="form-group">
            <label for="phone_work">Work Phone</label>
            <input
              id="phone_work"
              v-model="formData.phone_work"
              type="tel"
              :disabled="isSubmitting"
              placeholder="+1-555-0124"
            />
            <small class="help-text">Parent's work phone number</small>
          </div>
        </div>

        <div class="form-group">
          <label for="preferred_contact_method">Preferred Contact Method</label>
          <select
            id="preferred_contact_method"
            v-model="formData.preferred_contact_method"
            :disabled="isSubmitting"
          >
            <option value="">Select preferred method</option>
            <option value="email">Email</option>
            <option value="phone">Phone</option>
            <option value="sms">SMS</option>
            <option value="app_notification">App Notification</option>
          </select>
          <small class="help-text">How the parent prefers to be contacted</small>
        </div>
      </div>

      <!-- Employment Information -->
      <div class="form-section">
        <h3>Employment Information</h3>

        <div class="form-group">
          <label for="occupation">Occupation</label>
          <input
            id="occupation"
            v-model="formData.occupation"
            type="text"
            :disabled="isSubmitting"
            placeholder="e.g., Software Engineer, Teacher, Doctor"
          />
        </div>

        <div class="form-group">
          <label for="workplace">Workplace</label>
          <input
            id="workplace"
            v-model="formData.workplace"
            type="text"
            :disabled="isSubmitting"
            placeholder="e.g., Tech Corp, Lincoln Elementary"
          />
        </div>
      </div>

      <!-- Preferences -->
      <div class="form-section">
        <h3>Preferences & Permissions</h3>

        <div class="checkbox-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="formData.emergency_contact"
              :disabled="isSubmitting"
            />
            <div class="checkbox-info">
              <strong>Emergency Contact</strong>
              <small>Can be contacted in case of emergencies</small>
            </div>
          </label>

          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="formData.pickup_authorized"
              :disabled="isSubmitting"
            />
            <div class="checkbox-info">
              <strong>Pickup Authorized</strong>
              <small>Authorized to pick up students from school</small>
            </div>
          </label>

          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="formData.receives_newsletter"
              :disabled="isSubmitting"
            />
            <div class="checkbox-info">
              <strong>Receives Newsletter</strong>
              <small>Subscribe to school newsletters and updates</small>
            </div>
          </label>
        </div>
      </div>

      <!-- Children (Edit Mode Only) -->
      <div v-if="isEditMode && selectedParent" class="form-section">
        <h3>Children</h3>

        <div v-if="selectedParent.children && selectedParent.children.length > 0" class="children-list">
          <div
            v-for="child in selectedParent.children"
            :key="child.student_id"
            class="child-item"
          >
            <div class="child-info">
              <strong>{{ getChildName(child) }}</strong>
              <span class="relationship-badge">{{ getRelationshipLabel(child.relationship_type) }}</span>
              <div class="child-details">
                Grade {{ child.student?.grade_level }}
                <span v-if="child.is_primary_contact" class="badge">Primary Contact</span>
                <span v-if="child.has_legal_custody" class="badge">Legal Custody</span>
                <span v-if="child.has_pickup_permission" class="badge">Pickup Permission</span>
              </div>
            </div>
            <button
              type="button"
              @click="unlinkChild(child.student_id)"
              class="btn-danger-small"
              :disabled="isSubmitting"
            >
              Remove
            </button>
          </div>
        </div>

        <div v-else class="empty-children">
          <p>No children linked to this parent yet.</p>
        </div>

        <button
          type="button"
          @click="showLinkStudentDialog = true"
          class="btn-secondary"
          :disabled="isSubmitting"
        >
          + Link Student
        </button>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="goBack" class="btn-secondary" :disabled="isSubmitting">
          Cancel
        </button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Update Parent' : 'Create Parent') }}
        </button>
      </div>
    </form>

    <!-- Link Student Dialog -->
    <div v-if="showLinkStudentDialog" class="modal-overlay" @click="closeLinkDialog">
      <div class="modal-content" @click.stop>
        <h3>Link Student to Parent</h3>

        <div class="form-group">
          <label for="student_id">Student ID</label>
          <input
            id="student_id"
            v-model="linkData.student_id"
            type="text"
            placeholder="Enter student UUID"
            required
          />
        </div>

        <div class="form-group">
          <label for="relationship_type">Relationship Type</label>
          <select id="relationship_type" v-model="linkData.relationship_type" required>
            <option value="">Select relationship</option>
            <option value="mother">Mother</option>
            <option value="father">Father</option>
            <option value="guardian">Guardian</option>
            <option value="stepmother">Stepmother</option>
            <option value="stepfather">Stepfather</option>
            <option value="grandparent">Grandparent</option>
            <option value="foster_parent">Foster Parent</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div class="checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="linkData.is_primary_contact" />
            <span>Primary Contact</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="linkData.has_legal_custody" />
            <span>Legal Custody</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="linkData.has_pickup_permission" />
            <span>Pickup Permission</span>
          </label>
        </div>

        <div class="modal-actions">
          <button type="button" @click="closeLinkDialog" class="btn-secondary">
            Cancel
          </button>
          <button type="button" @click="executeLinkStudent" class="btn-primary">
            Link Student
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useParentStore } from '@/stores/parentStore'
import type { ParentCreateInput, ParentUpdateInput, ParentStudentLinkInput } from '@/types/parent'
import { getRelationshipTypeLabel } from '@/types/parent'
import UserSelector from './UserSelector.vue'

const route = useRoute()
const router = useRouter()
const parentStore = useParentStore()

const parentId = computed(() => route.params.id as string)
const isEditMode = computed(() => !!parentId.value && parentId.value !== 'create')

const isSubmitting = ref(false)
const formError = ref<string | null>(null)
const showLinkStudentDialog = ref(false)

interface FormData {
  user_id: string
  occupation: string
  workplace: string
  phone_mobile: string
  phone_work: string
  preferred_contact_method: string
  emergency_contact: boolean
  pickup_authorized: boolean
  receives_newsletter: boolean
}

const formData = reactive<FormData>({
  user_id: '',
  occupation: '',
  workplace: '',
  phone_mobile: '',
  phone_work: '',
  preferred_contact_method: '',
  emergency_contact: false,
  pickup_authorized: false,
  receives_newsletter: true
})

const linkData = reactive<ParentStudentLinkInput>({
  student_id: '',
  relationship_type: 'mother',
  is_primary_contact: false,
  has_legal_custody: true,
  has_pickup_permission: true
})

const selectedParent = computed(() => parentStore.selectedParent)

onMounted(async () => {
  if (isEditMode.value) {
    await loadParent()
  }
})

async function loadParent() {
  try {
    await parentStore.fetchParentById(parentId.value)
    const parent = parentStore.selectedParent

    if (parent) {
      formData.user_id = parent.user_id
      formData.occupation = parent.occupation || ''
      formData.workplace = parent.workplace || ''
      formData.phone_mobile = parent.phone_mobile || ''
      formData.phone_work = parent.phone_work || ''
      formData.preferred_contact_method = parent.preferred_contact_method || ''
      formData.emergency_contact = parent.emergency_contact
      formData.pickup_authorized = parent.pickup_authorized
      formData.receives_newsletter = parent.receives_newsletter
    }
  } catch (error: any) {
    formError.value = error.message || 'Failed to load parent'
  }
}

async function handleSubmit() {
  formError.value = null
  isSubmitting.value = true

  try {
    if (isEditMode.value) {
      await updateParent()
    } else {
      await createParent()
    }

    router.push('/parents')
  } catch (error: any) {
    formError.value = error.message || 'Failed to save parent'
  } finally {
    isSubmitting.value = false
  }
}

async function createParent() {
  const schoolId = localStorage.getItem('current_school_id') || 'SCHOOL_ID_PLACEHOLDER'

  const parentData: ParentCreateInput = {
    school_id: schoolId,
    user_id: formData.user_id,
  }

  if (formData.occupation) parentData.occupation = formData.occupation
  if (formData.workplace) parentData.workplace = formData.workplace
  if (formData.phone_mobile) parentData.phone_mobile = formData.phone_mobile
  if (formData.phone_work) parentData.phone_work = formData.phone_work
  if (formData.preferred_contact_method) parentData.preferred_contact_method = formData.preferred_contact_method as any
  parentData.emergency_contact = formData.emergency_contact
  parentData.pickup_authorized = formData.pickup_authorized
  parentData.receives_newsletter = formData.receives_newsletter

  await parentStore.createParent(parentData)
}

async function updateParent() {
  const parentData: ParentUpdateInput = {}

  if (formData.occupation !== undefined) parentData.occupation = formData.occupation
  if (formData.workplace !== undefined) parentData.workplace = formData.workplace
  if (formData.phone_mobile !== undefined) parentData.phone_mobile = formData.phone_mobile
  if (formData.phone_work !== undefined) parentData.phone_work = formData.phone_work
  if (formData.preferred_contact_method !== undefined) parentData.preferred_contact_method = formData.preferred_contact_method as any
  parentData.emergency_contact = formData.emergency_contact
  parentData.pickup_authorized = formData.pickup_authorized
  parentData.receives_newsletter = formData.receives_newsletter

  await parentStore.updateParent(parentId.value, parentData)
}

function handleUserSelect(user: any) {
  console.log('Selected user:', user)
}

async function unlinkChild(studentId: string) {
  if (!confirm('Are you sure you want to unlink this student?')) {
    return
  }

  try {
    await parentStore.unlinkStudent(parentId.value, studentId)
  } catch (error: any) {
    formError.value = error.message || 'Failed to unlink student'
  }
}

async function executeLinkStudent() {
  try {
    await parentStore.linkStudent(parentId.value, linkData)
    closeLinkDialog()
  } catch (error: any) {
    formError.value = error.message || 'Failed to link student'
  }
}

function closeLinkDialog() {
  showLinkStudentDialog.value = false
  linkData.student_id = ''
  linkData.relationship_type = 'mother'
  linkData.is_primary_contact = false
  linkData.has_legal_custody = true
  linkData.has_pickup_permission = true
}

function getChildName(child: any): string {
  if (child.student?.user) {
    return `${child.student.user.first_name} ${child.student.user.last_name}`
  }
  return 'Unknown Student'
}

function getRelationshipLabel(type: string): string {
  return getRelationshipTypeLabel(type as any)
}

function goBack() {
  router.push('/parents')
}
</script>

<style scoped>
.parent-form {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 2rem;
}

.form-header h2 {
  margin: 1rem 0 0 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.btn-back {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #42b883;
  margin-bottom: 1rem;
}

.btn-back:hover {
  background: #f8f9fa;
}

.form-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.error-banner {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 2rem;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #42b883;
}

.form-group input:disabled,
.form-group select:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
  margin-top: 0.25rem;
}

.checkbox-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.checkbox-info strong {
  color: #2c3e50;
}

.checkbox-info small {
  color: #6c757d;
  font-size: 0.85rem;
}

.children-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.child-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.child-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.relationship-badge {
  font-size: 0.85rem;
  color: #42b883;
  font-weight: 500;
}

.child-details {
  font-size: 0.85rem;
  color: #6c757d;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.125rem 0.5rem;
  background: #e0f2f1;
  color: #00695c;
  border-radius: 12px;
  font-size: 0.75rem;
}

.empty-children {
  padding: 2rem;
  text-align: center;
  color: #6c757d;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #35a372;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #42b883;
  border: 1px solid #42b883;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #42b883;
  color: white;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger-small {
  padding: 0.5rem 1rem;
  background: #c62828;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.btn-danger-small:hover:not(:disabled) {
  background: #b71c1c;
}

.btn-danger-small:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #6c757d;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b883;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
