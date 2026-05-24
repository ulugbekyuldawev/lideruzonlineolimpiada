<template>
  <div>
    <div class="page-head">
      <div>
        <h2>Yaratilgan o‘quvchilar</h2>
        <p>Code, test holati, natijalar va fan/sinflarni nazorat qilish</p>
      </div>
      <div class="page-actions">
        <button class="secondary-btn" :disabled="downloading" @click="downloadStudentsExcel">
          {{ downloading ? 'Yuklanmoqda...' : 'Excel yuklash' }}
        </button>
        <RouterLink v-if="mainAdmin" to="/admin/students/create" class="primary-btn">+ O‘quvchi yaratish</RouterLink>
      </div>
    </div>

    <div class="filter-bar">
      <input v-model="filters.q" placeholder="Ism, familya yoki code qidirish" @input="loadStudents" />
      <select v-model="filters.subject" @change="onFilterSubjectChange">
        <option value="">Barcha fanlar</option>
        <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
          {{ subject.name }}
        </option>
      </select>
      <select v-model="filters.status" @change="loadStudents">
        <option value="">Barcha status</option>
        <option value="not_started">Ishlamagan</option>
        <option value="in_progress">Ishlayapti</option>
        <option value="completed">Ishlab bo‘ldi</option>
      </select>
      <button class="secondary-btn" @click="clearFilters">Tozalash</button>
      <button class="secondary-btn" @click="loadStudents">Yangilash</button>
    </div>

    <div v-if="canManageStudents" class="bulk-actions-bar">
      <div>
        <b>{{ selectedCount }} ta o‘quvchi tanlandi</b>
        <span>Keraklilarini belgilang va birdan o‘chiring.</span>
      </div>
      <div class="bulk-actions-buttons">
        <button class="secondary-btn" :disabled="!selectedCount" @click="clearSelectedStudents">Belgini tozalash</button>
        <button class="danger-btn" :disabled="!selectedCount || bulkDeleting" @click="openBulkDeleteModal">
          {{ bulkDeleting ? 'O‘chirilmoqda...' : `Tanlanganlarni o‘chirish (${selectedCount})` }}
        </button>
      </div>
    </div>

    <div class="panel">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th v-if="canManageStudents" class="select-col">
                <input
                  type="checkbox"
                  class="student-check"
                  :checked="allVisibleSelected"
                  :indeterminate.prop="someVisibleSelected"
                  :disabled="!students.length"
                  title="Ko‘rinib turgan hammasini belgilash"
                  @change="toggleSelectAllVisible"
                />
              </th>
              <th>№</th>
              <th>O‘quvchi</th>
              <th>O‘quv markaz nomi</th>
              <th>Fan</th>
              <th>Sinfi</th>
              <th>Code</th>
              <th>Status</th>
              <th>Nechta to‘g‘ri</th>
              <th>Foiz</th>
              <th v-if="canManageStudents">Amal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(s, i) in students" :key="s.id">
              <td v-if="canManageStudents" class="select-col">
                <input
                  v-model="selectedIds"
                  type="checkbox"
                  class="student-check"
                  :value="s.id"
                  :title="`${s.full_name} o‘quvchini belgilash`"
                />
              </td>
              <td>{{ i + 1 }}</td>
              <td><b>{{ s.full_name }}</b></td>
              <td>{{ s.center_name || 'LIDER.Uz Onlayn Olimpiada' }}</td>
              <td>{{ s.subject_name }}</td>
              <td>{{ s.level_name }}</td>
              <td>
                <div class="code-copy-cell">
                  <button class="code-pill" :title="`${s.code} codeni copy qilish`" @click="copyCode(s.code)">
                    {{ s.code }}
                  </button>
                  <button class="copy-code-btn" :class="{ copied: copiedCode === s.code }" @click="copyCode(s.code)">
                    {{ copiedCode === s.code ? 'Copy qilindi' : 'Copy' }}
                  </button>
                </div>
              </td>
              <td><StatusBadge :status="s.status" /></td>
              <td>
                <span v-if="s.correct_count !== null && s.correct_count !== undefined">
                  {{ s.correct_count }}/{{ s.total_questions }} ta
                </span>
                <span v-else>—</span>
              </td>
              <td>
                <span v-if="s.percent !== null && s.percent !== undefined">{{ s.percent }}%</span>
                <span v-else>—</span>
              </td>
              <td v-if="canManageStudents">
                <div class="student-row-actions">
                  <button class="secondary-btn small-action-btn" @click="openEditModal(s)">
                    Tahrirlash
                  </button>
                  <button class="danger-btn small-action-btn" @click="openDeleteModal(s)">
                    O‘chirish
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!students.length">
              <td :colspan="canManageStudents ? 11 : 9" class="empty-cell">O‘quvchi topilmadi</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="editModalOpen" class="modal-backdrop" @click.self="closeEditModal">
      <div class="edit-student-modal">
        <div class="modal-head">
          <div>
            <h3>O‘quvchini tahrirlash</h3>
            <p>{{ editingStudent?.full_name }}</p>
          </div>
          <button class="modal-close-btn" @click="closeEditModal">×</button>
        </div>

        <form class="form-grid" @submit.prevent="saveStudentEdit">
          <label>
            Fan
            <select v-model="editForm.subject" required @change="onEditSubjectChange">
              <option value="">Fan tanlang</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </label>

          <label>
            Sinfi
            <select v-model="editForm.level" required>
              <option value="">Sinf tanlang</option>
              <option v-for="level in editFilteredLevels" :key="level.id" :value="level.id">
                {{ level.name }} — {{ level.duration_minutes }} daqiqa
              </option>
            </select>
          </label>

          <p v-if="editError" class="error-box">{{ editError }}</p>

          <div class="modal-actions">
            <button type="button" class="secondary-btn" @click="closeEditModal">Bekor qilish</button>
            <button class="primary-btn" :disabled="savingEdit">
              {{ savingEdit ? 'Saqlanmoqda...' : 'Saqlash' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="deleteModalOpen" class="modal-backdrop" @click.self="closeDeleteModal">
      <div class="edit-student-modal delete-confirm-modal">
        <div class="modal-head">
          <div>
            <h3>O‘quvchini o‘chirish</h3>
            <p>{{ deletingStudent?.full_name }}</p>
          </div>
          <button class="modal-close-btn" @click="closeDeleteModal">×</button>
        </div>

        <div class="delete-warning-box">
          <b>O‘chirishni xohlaysizmi?</b>
          <span>Ha bosilganda o‘quvchi, natijasi va javoblari o‘chiriladi.</span>
        </div>

        <p v-if="deleteError" class="error-box">{{ deleteError }}</p>

        <div class="modal-actions">
          <button type="button" class="secondary-btn" @click="closeDeleteModal">Yo‘q</button>
          <button class="danger-btn" :disabled="deleting" @click="deleteStudent">
            {{ deleting ? 'O‘chirilmoqda...' : 'Ha, o‘chirish' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="bulkDeleteModalOpen" class="modal-backdrop" @click.self="closeBulkDeleteModal">
      <div class="edit-student-modal delete-confirm-modal">
        <div class="modal-head">
          <div>
            <h3>Tanlangan o‘quvchilarni o‘chirish</h3>
            <p>{{ selectedCount }} ta o‘quvchi tanlangan</p>
          </div>
          <button class="modal-close-btn" @click="closeBulkDeleteModal">×</button>
        </div>

        <div class="delete-warning-box">
          <b>Rostdan ham o‘chirasizmi?</b>
          <span>Ha bosilganda tanlangan o‘quvchilar, ularning natijalari va javoblari o‘chiriladi.</span>
        </div>

        <p v-if="bulkDeleteError" class="error-box">{{ bulkDeleteError }}</p>

        <div class="modal-actions">
          <button type="button" class="secondary-btn" @click="closeBulkDeleteModal">Yo‘q</button>
          <button class="danger-btn" :disabled="bulkDeleting" @click="deleteSelectedStudents">
            {{ bulkDeleting ? 'O‘chirilmoqda...' : `Ha, ${selectedCount} tasini o‘chirish` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../api/axios'
import StatusBadge from '../components/StatusBadge.vue'
import { fetchCurrentAdmin, getStoredAdminProfile, isMainAdmin } from '../utils/auth'

const students = ref([])
const subjects = ref([])
const levels = ref([])
const downloading = ref(false)
const currentAdmin = ref(getStoredAdminProfile())

const editModalOpen = ref(false)
const editingStudent = ref(null)
const savingEdit = ref(false)
const editError = ref('')

const deleteModalOpen = ref(false)
const deletingStudent = ref(null)
const deleting = ref(false)
const deleteError = ref('')

const selectedIds = ref([])
const bulkDeleteModalOpen = ref(false)
const bulkDeleting = ref(false)
const bulkDeleteError = ref('')

const copiedCode = ref('')
let copiedTimer = null

const filters = reactive({ q: '', subject: '', status: '' })
const editForm = reactive({ subject: '', level: '' })

const mainAdmin = computed(() => isMainAdmin(currentAdmin.value))
const canManageStudents = computed(() => Boolean(currentAdmin.value?.can_edit_students && currentAdmin.value?.can_delete_students))
const selectedCount = computed(() => selectedIds.value.length)
const visibleStudentIds = computed(() => students.value.map(student => student.id))
const allVisibleSelected = computed(() => {
  return visibleStudentIds.value.length > 0 && visibleStudentIds.value.every(id => selectedIds.value.includes(id))
})
const someVisibleSelected = computed(() => {
  return !allVisibleSelected.value && visibleStudentIds.value.some(id => selectedIds.value.includes(id))
})

const editFilteredLevels = computed(() => {
  const list = levels.value.filter(level => String(level.subject) === String(editForm.subject))
  const selectedSubject = subjects.value.find(subject => String(subject.id) === String(editForm.subject))

  if (selectedSubject?.name === 'IT') {
    const order = ['Frontend 1', 'Frontend 2', 'Backend 1', 'Backend 2']
    return [...list].sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name))
  }

  if (selectedSubject?.name === 'English') {
    const order = ['Starter', 'Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate']
    return [...list].sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name))
  }

  return list
})

async function loadStudents() {
  const params = {}
  if (filters.q) params.q = filters.q
  if (filters.subject) params.subject = filters.subject
  if (filters.status) params.status = filters.status
  const res = await api.get('/students/', { params })
  students.value = res.data
  const visibleIds = new Set(students.value.map(student => student.id))
  selectedIds.value = selectedIds.value.filter(id => visibleIds.has(id))
}

function onFilterSubjectChange() {
  loadStudents()
}

function clearFilters() {
  filters.q = ''
  filters.subject = ''
  filters.status = ''
  loadStudents()
}

async function loadOptions() {
  const [subjectsRes, levelsRes] = await Promise.all([
    api.get('/subjects/'),
    api.get('/levels/'),
  ])
  subjects.value = subjectsRes.data
  levels.value = levelsRes.data
}

async function loadCurrentAdmin() {
  try {
    currentAdmin.value = await fetchCurrentAdmin()
  } catch {
    currentAdmin.value = getStoredAdminProfile()
  }
}

function toggleSelectAllVisible(event) {
  if (event.target.checked) {
    selectedIds.value = Array.from(new Set([...selectedIds.value, ...visibleStudentIds.value]))
  } else {
    const visible = new Set(visibleStudentIds.value)
    selectedIds.value = selectedIds.value.filter(id => !visible.has(id))
  }
}

function clearSelectedStudents() {
  selectedIds.value = []
}

function openBulkDeleteModal() {
  if (!selectedIds.value.length) return
  bulkDeleteError.value = ''
  bulkDeleteModalOpen.value = true
}

function closeBulkDeleteModal() {
  if (bulkDeleting.value) return
  bulkDeleteModalOpen.value = false
  bulkDeleteError.value = ''
}

async function deleteSelectedStudents() {
  if (!selectedIds.value.length) return

  bulkDeleting.value = true
  bulkDeleteError.value = ''

  try {
    const idsToDelete = [...selectedIds.value]
    await api.post('/students/bulk-delete/', { ids: idsToDelete })
    const deleted = new Set(idsToDelete)
    students.value = students.value.filter(student => !deleted.has(student.id))
    selectedIds.value = []
    bulkDeleteModalOpen.value = false
  } catch (e) {
    bulkDeleteError.value = JSON.stringify(e.response?.data || 'Tanlangan o‘quvchilarni o‘chirishda xatolik yuz berdi.')
  } finally {
    bulkDeleting.value = false
  }
}

function openEditModal(student) {
  editingStudent.value = student
  editForm.subject = student.subject
  editForm.level = student.level
  editError.value = ''
  editModalOpen.value = true
}

function closeEditModal() {
  editModalOpen.value = false
  editingStudent.value = null
  editError.value = ''
  editForm.subject = ''
  editForm.level = ''
}

function onEditSubjectChange() {
  editForm.level = ''
}

async function saveStudentEdit() {
  if (!editingStudent.value) return

  savingEdit.value = true
  editError.value = ''

  try {
    const res = await api.patch(`/students/${editingStudent.value.id}/`, {
      subject: editForm.subject,
      level: editForm.level,
    })

    const index = students.value.findIndex(student => student.id === editingStudent.value.id)
    if (index !== -1) students.value[index] = res.data

    closeEditModal()
  } catch (e) {
    editError.value = JSON.stringify(e.response?.data || 'Tahrirlashda xatolik yuz berdi.')
  } finally {
    savingEdit.value = false
  }
}

function openDeleteModal(student) {
  deletingStudent.value = student
  deleteError.value = ''
  deleteModalOpen.value = true
}

function closeDeleteModal() {
  deleteModalOpen.value = false
  deletingStudent.value = null
  deleteError.value = ''
}

async function deleteStudent() {
  if (!deletingStudent.value) return

  deleting.value = true
  deleteError.value = ''

  try {
    const deletedId = deletingStudent.value.id
    await api.delete(`/students/${deletedId}/`)
    students.value = students.value.filter(student => student.id !== deletedId)
    selectedIds.value = selectedIds.value.filter(id => id !== deletedId)
    closeDeleteModal()
  } catch (e) {
    deleteError.value = JSON.stringify(e.response?.data || 'O‘chirishda xatolik yuz berdi.')
  } finally {
    deleting.value = false
  }
}

async function copyCode(code) {
  try {
    await navigator.clipboard.writeText(code)
    copiedCode.value = code
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = code
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    textarea.remove()
    copiedCode.value = code
  }

  if (copiedTimer) clearTimeout(copiedTimer)
  copiedTimer = setTimeout(() => {
    copiedCode.value = ''
  }, 1500)
}

async function downloadStudentsExcel() {
  downloading.value = true
  try {
    const params = {}
    if (filters.q) params.q = filters.q
    if (filters.subject) params.subject = filters.subject
    if (filters.status) params.status = filters.status

    const res = await api.get('/students/export-excel/', { params, responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'barcha_oquvchilar.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } finally {
    downloading.value = false
  }
}

onMounted(async () => {
  await loadCurrentAdmin()
  await Promise.all([loadOptions(), loadStudents()])
})
</script>
