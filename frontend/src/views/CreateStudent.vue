<template>
  <div>
    <div class="page-head">
      <div>
        <h2>O‘quvchi yaratish</h2>
        <p>O‘quvchiga fan va sinf biriktiriladi, keyin 6 xonali status code beriladi.</p>
      </div>
      <RouterLink v-if="canCreateStudents" class="primary-btn" to="/admin/students/import">Excel orqali yuklash</RouterLink>
    </div>

    <div v-if="!canCreateStudents" class="error-box">
      Sizga o‘quvchi yaratish ruxsati berilmagan.
    </div>

    <div v-else class="grid-2">
      <div class="panel">
        <h3>Yangi o‘quvchi</h3>
        <form @submit.prevent="createStudent" class="form-grid">
          <label>
            O‘quvchi Ism Familyasi
            <input v-model="form.full_name" placeholder="Masalan: Aliyev Vali" required />
          </label>

          <label>O‘quv markaz nomi
            <input v-model="form.center_name" placeholder="Masalan: LIDER.Uz Onlayn Olimpiada" required />
          </label>

          <label>Fan
            <select v-model="form.subject" required @change="filterLevels">
              <option value="">Tanlang</option>
              <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </label>

          <label>Sinfi
            <select v-model="form.level" required>
              <option value="">Tanlang</option>
              <option v-for="l in filteredLevels" :key="l.id" :value="l.id">
                {{ l.name }} — {{ l.duration_minutes }} daqiqa
              </option>
            </select>
          </label>

          <button class="primary-btn">Yaratish</button>
        </form>
        <p v-if="error" class="error-box">{{ error }}</p>
      </div>

      <div class="panel result-panel" v-if="createdStudent">
        <h3>O‘quvchi yaratildi</h3>
        <div class="success-code">{{ createdStudent.code }}</div>
        <p><b>{{ createdStudent.full_name }}</b></p>
        <p>{{ createdStudent.center_name }}</p>
        <p>{{ createdStudent.subject_name }} / {{ createdStudent.level_name }}</p>
        <button class="secondary-btn" @click="copyCode(createdStudent.code)">Code copy qilish</button>
        <RouterLink class="primary-btn block-link" to="/admin/students">Yaratilgan o‘quvchilarga o‘tish</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../api/axios'
import { fetchCurrentAdmin, getStoredAdminProfile } from '../utils/auth'

const subjects = ref([])
const levels = ref([])
const createdStudent = ref(null)
const error = ref('')
const currentAdmin = ref(getStoredAdminProfile())
const form = reactive({ full_name: '', center_name: 'LIDER.Uz Onlayn Olimpiada', subject: '', level: '' })

const canCreateStudents = computed(() => Boolean(currentAdmin.value?.can_create_students))

const filteredLevels = computed(() => {
  const list = levels.value.filter(l => String(l.subject) === String(form.subject))
  const selectedSubject = subjects.value.find(s => String(s.id) === String(form.subject))
  if (selectedSubject?.name === 'IT') {
    const order = ['Frontend 1', 'Frontend 2', 'Backend 1', 'Backend 2']
    return [...list].sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name))
  }
  if (selectedSubject?.name === 'Ingliz tili') {
    const order = ['1-sinf', '2-sinf', '3-sinf', '4-sinf', '5-sinf', '6-sinf', '7-sinf']
    return [...list].sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name))
  }
  return list
})

function filterLevels() {
  form.level = ''
}

function splitFullName(fullName) {
  const parts = String(fullName || '').trim().split(/\s+/).filter(Boolean)
  if (parts.length < 2) {
    throw new Error('O‘quvchi ism va familyasini to‘liq kiriting.')
  }
  return {
    first_name: parts[0],
    last_name: parts.slice(1).join(' '),
  }
}

async function loadOptions() {
  const [subjectsRes, levelsRes] = await Promise.all([api.get('/subjects/'), api.get('/levels/')])
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

async function createStudent() {
  error.value = ''
  try {
    if (!canCreateStudents.value) throw new Error('Sizga o‘quvchi yaratish ruxsati yo‘q.')
    const { first_name, last_name } = splitFullName(form.full_name)

    const payload = {
      first_name,
      last_name,
      center_name: form.center_name,
      subject: form.subject,
      level: form.level,
    }
    const res = await api.post('/students/', payload)
    createdStudent.value = res.data
    Object.assign(form, {
      full_name: '',
      center_name: 'LIDER.Uz Onlayn Olimpiada',
      subject: '',
      level: '',
    })
  } catch (e) {
    error.value = e.message || JSON.stringify(e.response?.data || 'Xatolik')
  }
}

async function copyCode(code) {
  await navigator.clipboard.writeText(code)
}

onMounted(async () => {
  await Promise.all([loadOptions(), loadCurrentAdmin()])
})
</script>
