<template>
  <div class="student-entry-page olympiad-entry world-entry">
    <div class="entry-orb entry-orb-one"></div>
    <div class="entry-orb entry-orb-two"></div>
    <div class="entry-orb entry-orb-three"></div>

    <button type="button" class="public-result-top-btn" @click="openResultModal">
      Natijalar ko‘rish
    </button>

    <section class="world-hero-shell">
      <div class="world-hero-copy">
        <div class="world-brand-line no-mark">
          <div>
            <span class="entry-badge">LIDER.Uz Onlayn Olimpiada Education Contest</span>
            <h1>LIDER.Uz Onlayn Olimpiada</h1>
          </div>
        </div>

        <p class="entry-subtitle world-subtitle">
          LIDER.Uz Onlayn Olimpiada o‘quvchilari uchun zamonaviy online test platformasi. Status code orqali testga kiring,
          topshiriqlarni bajaring va natijangizni tezkor tekshiring.
        </p>

        <div class="world-feature-grid">
          <span>⚡ Tezkor kirish</span>
          <span>🏆 LIDER.Uz Onlayn Olimpiada testlari</span>
          <span>📊 Natija ko‘rish</span>
        </div>
      </div>

      <div class="student-card entry-card world-login-card">
        <div class="entry-top compact">
          <span class="entry-badge">Student access</span>
        </div>

        <h2>Testga kirish</h2>
        <p class="entry-subtitle">Admin bergan 6 xonali status code’ni kiriting.</p>

        <form @submit.prevent="startExam" class="code-form entry-form">
          <label class="code-label">
            Status code
            <input
              v-model="code"
              maxlength="6"
              minlength="6"
              inputmode="numeric"
              placeholder="582914"
              required
            />
          </label>
          <button class="primary-btn entry-start-btn" :disabled="loading">
            {{ loading ? 'Tekshirilmoqda...' : 'Testni boshlash' }}
          </button>
        </form>

        <p v-if="error" class="error-box">{{ error }}</p>

        <RouterLink to="/admin/login" class="admin-login-link entry-admin-link">
          Admin panelga kirish
        </RouterLink>
      </div>
    </section>

    <div v-if="showResultModal" class="modal-backdrop result-lookup-backdrop" @click.self="closeResultModal">
      <div class="answer-modal result-lookup-modal public-results-modal">
        <button type="button" class="modal-close-btn" @click="closeResultModal">×</button>

        <div class="result-modal-icon">📊</div>
        <h2>Natijalar</h2>
        <p>Code kiritish shart emas. O‘quv markaz va fan bo‘yicha filterlab ko‘rishingiz mumkin.</p>

        <div class="public-results-filters">
          <label>
            O‘quv markaz tanlash
            <select v-model="selectedCenter" @change="loadPublicResults">
              <option value="">Barcha o‘quv markazlar</option>
              <option v-for="center in centers" :key="center.id" :value="center.id">
                {{ center.name }}
              </option>
            </select>
          </label>

          <label>
            Fan tanlash
            <select v-model="selectedSubject" @change="loadPublicResults">
              <option value="">Barcha fanlar</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </label>

          <button type="button" class="secondary-btn" @click="clearResultFilters">
            Tozalash
          </button>
        </div>

        <p v-if="resultLoading" class="loading-box">Natijalar yuklanmoqda...</p>
        <p v-if="resultError" class="error-box">{{ resultError }}</p>

        <div class="public-results-table-wrap">
          <table class="public-results-table">
            <thead>
              <tr>
                <th>№</th>
                <th>O‘quvchi ism familyasi</th>
                <th>O‘quv markaz</th>
                <th>Fan</th>
                <th>Sinfi</th>
                <th>Nechta to‘g‘ri</th>
                <th>Foiz</th>
                <th>Vaqt</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(result, index) in publicResults" :key="result.id">
                <td>{{ index + 1 }}</td>
                <td><b>{{ result.student_full_name }}</b></td>
                <td>{{ result.center_name }}</td>
                <td>{{ result.subject_name }}</td>
                <td>{{ result.level_name }}</td>
                <td><b>{{ result.correct_count }}/{{ result.total_questions }}</b></td>
                <td>{{ result.percent }}%</td>
                <td>{{ formatSeconds(result.spent_seconds) }}</td>
              </tr>
              <tr v-if="!resultLoading && !publicResults.length">
                <td colspan="8" class="empty-cell">Hozircha natija topilmadi</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()
const code = ref('')
const loading = ref(false)
const error = ref('')
const showResultModal = ref(false)
const resultLoading = ref(false)
const resultError = ref('')
const publicResults = ref([])
const centers = ref([])
const subjects = ref([])
const selectedCenter = ref('')
const selectedSubject = ref('')

function cleanCode(value) {
  return String(value || '').trim()
}

function formatSeconds(seconds) {
  const total = Number(seconds || 0)
  const min = Math.floor(total / 60)
  const sec = total % 60
  return `${min} daq ${sec} sek`
}

function openResultModal() {
  showResultModal.value = true
  resultError.value = ''
  loadPublicResults()
}

function closeResultModal() {
  showResultModal.value = false
}

function clearResultFilters() {
  selectedCenter.value = ''
  selectedSubject.value = ''
  loadPublicResults()
}

async function startExam() {
  loading.value = true
  error.value = ''
  try {
    const finalCode = cleanCode(code.value)
    // Progressni o'chirmaymiz: bola testdan chiqib ketib qayta kirsa,
    // javoblari va vaqt hisoblanishi birinchi boshlagan joyidan davom etishi kerak.
    // Vaqt backenddagi student.started_at bo'yicha yuradi, qayta kirganda 30/10 daqiqadan
    // boshidan boshlanib ketmaydi.
    sessionStorage.removeItem('exam_payload')
    const res = await api.post('/exam/start/', { code: finalCode })
    sessionStorage.setItem('exam_payload', JSON.stringify({
      ...res.data,
      code: finalCode,
    }))
    router.push('/exam')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Code xato yoki oldin ishlatilgan.'
  } finally {
    loading.value = false
  }
}

async function loadPublicResults() {
  resultLoading.value = true
  resultError.value = ''
  try {
    const res = await api.get('/exam/public-results/', {
      params: {
        center: selectedCenter.value || undefined,
        subject: selectedSubject.value || undefined,
      },
    })
    publicResults.value = res.data.results || []
    centers.value = res.data.centers || []
    subjects.value = res.data.subjects || []
  } catch (e) {
    resultError.value = e.response?.data?.detail || 'Natijalarni yuklab bo‘lmadi.'
  } finally {
    resultLoading.value = false
  }
}
</script>
