<template>
  <div class="exam-page" v-if="payload">
    <header class="exam-header">
      <div>
        <h1>{{ payload.student.full_name }}</h1>
        <p>{{ payload.student.subject_name }} / {{ payload.student.level_name }}</p>
      </div>
      <div v-if="!isMental" class="timer" :class="{ danger: remainingSeconds < 300 }">{{ formattedTime }}</div>
      <div v-else class="timer mental-timer" :class="{ danger: remainingSeconds < 60 }">
        {{ formattedTime }} · Mental {{ Math.min(currentMentalIndex + 1, mentalTasks.length) }}/{{ mentalTasks.length }}
      </div>
    </header>

    <main v-if="isMental" class="mental-stage">
      <div v-if="mentalPhase === 'countdown'" class="countdown-card">
        <p>Tayyorlaning</p>
        <strong>{{ countdownValue }}</strong>
      </div>

      <div v-else-if="mentalPhase === 'showing'" class="mental-number-card">
        <p>{{ currentMentalIndex + 1 }}-misol</p>
        <strong>{{ shownValue }}</strong>
        <span>Misol 3 sekund ko‘rsatiladi. Javob modalida ham vaqt davom etadi.</span>
      </div>

      <div v-else-if="mentalPhase === 'finished'" class="countdown-card">
        <p>Natija yuborilmoqda...</p>
      </div>

      <div class="mental-progress">
        <span v-for="(task, index) in mentalTasks" :key="task.id" :class="{ active: index === currentMentalIndex, done: mentalAnswers[task.id] !== undefined }"></span>
      </div>

      <div v-if="mentalPhase === 'answer'" class="modal-backdrop">
        <div class="answer-modal">
          <h2>{{ currentMentalIndex + 1 }}-misol javobi</h2>
          <p>Hisoblagan natijangizni kiriting.</p>
          <form @submit.prevent="saveMentalAnswer">
            <input ref="answerInputRef" v-model="answerInput" type="number" inputmode="numeric" placeholder="Javob" required />
            <button class="primary-btn" type="submit">Javobni saqlash</button>
          </form>
        </div>
      </div>

    </main>

    <main v-else class="exam-body">
      <div v-for="(q, index) in payload.questions" :key="q.id" class="question-card">
        <h3>{{ index + 1 }}. {{ q.text }}</h3>
        <img v-if="q.image" class="question-image" :src="questionImageUrl(q.image)" alt="Savol rasmi" loading="lazy" />
        <div class="options-grid">
          <label v-for="opt in optionList(q)" :key="opt.value" class="option-card" :class="{ selected: answers[q.id] === opt.value }">
            <input type="radio" :name="`question-${q.id}`" :value="opt.value" v-model="answers[q.id]" @change="persistTestProgress" />
            <span>{{ opt.value }}) {{ opt.text }}</span>
          </label>
        </div>
      </div>
      <button class="primary-btn finish-btn" :disabled="submitting || finishModal.show" @click="submitExam">{{ submitting ? 'Yakunlanmoqda...' : 'Testni yakunlash' }}</button>
    </main>

    <div v-if="finishModal.show" class="modal-backdrop success-backdrop">
      <div class="finish-modal-card" :class="finishModal.type">
        <div class="finish-icon">{{ finishModal.type === 'success' ? '✓' : '!' }}</div>
        <h2>{{ finishModal.title }}</h2>
        <p>{{ finishModal.message }}</p>
        <div v-if="finishModal.result" class="finish-visible-summary">
          <div>
            <span>O‘quvchi ism familyasi</span>
            <b>{{ finishModal.result.student_full_name || payload.student.full_name }}</b>
          </div>
          <div>
            <span>Nechta to‘g‘ri topgani</span>
            <b>{{ finishModal.result.correct_count }}/{{ finishModal.result.total_questions }}</b>
          </div>
          <div>
            <span>Necha minutda ishlab bo‘lgani</span>
            <b>{{ formatSeconds(finishModal.result.spent_seconds) }}</b>
          </div>
        </div>
        <div v-if="finishModal.result" class="student-result-box result-split-box">
          <div>
            <span>Nechta to‘g‘ri</span>
            <strong>{{ finishModal.result.correct_count }}/{{ finishModal.result.total_questions }}</strong>
          </div>
          <div>
            <span>Foiz</span>
            <strong>{{ finishModal.result.percent }}%</strong>
          </div>
        </div>
        <button class="primary-btn" type="button" @click="finishModal.type === 'success' ? goToStudentLogin() : closeFinishModal()">{{ finishModal.type === 'success' ? 'Code kiritish sahifasiga qaytish' : 'Yopish' }}</button>
      </div>
    </div>
  </div>
  <div v-else class="student-entry-page">
    <div class="student-card">
      <h1>Test topilmadi</h1>
      <RouterLink to="/student" class="primary-btn block-link">Code kiritish sahifasiga qaytish</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()
const payload = ref(null)
const answers = reactive({})
const remainingSeconds = ref(0)
const submitting = ref(false)
const finishModal = reactive({
  show: false,
  type: 'success',
  title: '',
  message: '',
  result: null,
})

const mentalPhase = ref('countdown')
const countdownValue = ref(3)
const currentMentalIndex = ref(0)
const shownValue = ref('')
const mentalAnswers = reactive({})
const answerInput = ref('')
const answerInputRef = ref(null)
const mentalTimers = []

let intervalId = null
let submitted = false

const isMental = computed(() => payload.value?.mode === 'mental')
const mentalTasks = computed(() => payload.value?.mental_tasks || [])
const formattedTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60)
  const s = remainingSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function formatSeconds(seconds) {
  const total = Number(seconds || 0)
  const min = Math.floor(total / 60)
  const sec = total % 60
  return `${min} daq ${sec} sek`
}

function showFinishSuccess(result) {
  finishModal.show = true
  finishModal.type = 'success'
  finishModal.title = isMental.value ? 'Mental arifmetika yakunlandi' : 'Test muvaffaqiyatli yakunlandi'
  if (isMental.value && result) {
    finishModal.message = `Siz ${result.total_questions} tadan ${result.correct_count} tasini to‘g‘ri ishladingiz.`
  } else {
    finishModal.message = 'Javoblaringiz adminga yuborildi. To‘g‘ri javoblar kaliti ko‘rsatilmaydi.'
  }
  finishModal.result = result || null
}

function showFinishError(message) {
  finishModal.show = true
  finishModal.type = 'error'
  finishModal.title = 'Xatolik yuz berdi'
  finishModal.message = message || 'Javoblarni yuborishda xatolik yuz berdi.'
  finishModal.result = null
}

function goToStudentLogin() {
  router.push('/student')
}

function closeFinishModal() {
  finishModal.show = false
}


function questionImageUrl(image) {
  if (!image) return ''
  if (image.startsWith('http://') || image.startsWith('https://') || image.startsWith('/')) return image
  return `/${image}`
}

function optionList(q) {
  return [
    { value: 'A', text: q.option_a },
    { value: 'B', text: q.option_b },
    { value: 'C', text: q.option_c },
    { value: 'D', text: q.option_d },
  ]
}

function examProgressKey() {
  return payload.value?.code ? `exam_progress_${payload.value.code}` : ''
}

function persistTestProgress() {
  const key = examProgressKey()
  if (!key) return
  localStorage.setItem(key, JSON.stringify({ answers: { ...answers } }))
}

function loadTestProgress() {
  const key = examProgressKey()
  if (!key) return
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '{}')
    if (saved.answers && typeof saved.answers === 'object') {
      Object.assign(answers, saved.answers)
    }
  } catch (_) {}
}

function examDurationSeconds(defaultMinutes) {
  return Math.max(1, Number(defaultMinutes || 30) * 60)
}

function normalizedRemainingFromBackend() {
  const value = Number(payload.value?.remaining_seconds)
  if (Number.isFinite(value) && value >= 0) return Math.floor(value)
  return null
}

function clientElapsedSeconds() {
  const duration = examDurationSeconds(payload.value?.duration_minutes || (isMental.value ? 10 : 30))
  const elapsed = duration - Number(remainingSeconds.value || 0)
  return Math.max(0, Math.min(duration, Math.floor(elapsed)))
}

function prepareTimer(defaultMinutes) {
  const duration = examDurationSeconds(defaultMinutes)
  const backendRemaining = normalizedRemainingFromBackend()

  // Qolgan vaqtni backenddan olamiz. Browser timezone/Date.parse sabab 00:00 bo'lib
  // qolmasligi uchun frontend started_at ni o'zi parse qilib vaqt hisoblamaydi.
  if (backendRemaining !== null) {
    remainingSeconds.value = Math.max(0, Math.min(duration, backendRemaining))
    return
  }

  remainingSeconds.value = duration
}

function submitPayload(extra = {}) {
  return {
    code: payload.value.code,
    client_started_at: payload.value.started_at || '',
    client_elapsed_seconds: clientElapsedSeconds(),
    ...extra,
  }
}

function clearMentalTimers() {
  while (mentalTimers.length) clearTimeout(mentalTimers.pop())
}

function mentalProgressKey() {
  return payload.value?.code ? `mental_progress_${payload.value.code}` : ''
}

function persistMentalProgress() {
  const key = mentalProgressKey()
  if (!key) return
  localStorage.setItem(key, JSON.stringify({ answers: { ...mentalAnswers } }))
}

function hasMentalAnswer(task) {
  return Object.prototype.hasOwnProperty.call(mentalAnswers, task.id) && mentalAnswers[task.id] !== '' && mentalAnswers[task.id] !== null && mentalAnswers[task.id] !== undefined
}

function loadMentalProgress() {
  const key = mentalProgressKey()

  // Avval serverda saqlangan javoblarni yuklaymiz. Shunda bola boshqa sahifaga chiqib
  // qayta kirsa ham o'sha javob berilmagan savoldan davom etadi.
  mentalTasks.value.forEach(task => {
    if (task.student_answer !== null && task.student_answer !== undefined && task.student_answer !== '') {
      mentalAnswers[task.id] = String(task.student_answer)
    }
  })

  if (key) {
    try {
      const saved = JSON.parse(localStorage.getItem(key) || '{}')
      if (saved.answers && typeof saved.answers === 'object') {
        Object.assign(mentalAnswers, saved.answers)
      }
    } catch (_) {}
  }

  const firstUnansweredIndex = mentalTasks.value.findIndex(task => !hasMentalAnswer(task))
  currentMentalIndex.value = firstUnansweredIndex === -1 ? mentalTasks.value.length : Math.max(0, firstUnansweredIndex)
  persistMentalProgress()
}

function startMentalCountdown(startIndex = 0) {
  mentalPhase.value = 'countdown'
  countdownValue.value = 3
  const tick = () => {
    if (countdownValue.value <= 1) {
      playMentalTask(startIndex)
      return
    }
    countdownValue.value -= 1
    mentalTimers.push(setTimeout(tick, 1000))
  }
  mentalTimers.push(setTimeout(tick, 1000))
}

function playMentalTask(index) {
  clearMentalTimers()
  const task = mentalTasks.value[index]
  if (!task) {
    submitMentalExam()
    return
  }

  currentMentalIndex.value = index
  mentalPhase.value = 'showing'
  shownValue.value = ''
  answerInput.value = ''

  const flashes = task.flashes || []
  const taskDisplayMs = Number(task.task_display_ms || 3000)
  const perFlashMs = flashes.length ? Math.max(250, Math.floor(taskDisplayMs / flashes.length)) : taskDisplayMs

  flashes.forEach((value, flashIndex) => {
    mentalTimers.push(setTimeout(() => {
      shownValue.value = value
    }, flashIndex * perFlashMs))
  })

  mentalTimers.push(setTimeout(async () => {
    mentalPhase.value = 'answer'
    shownValue.value = ''
    await nextTick()
    answerInputRef.value?.focus()
  }, taskDisplayMs))
}

async function saveMentalAnswer() {
  const task = mentalTasks.value[currentMentalIndex.value]
  if (!task || submitting.value) return

  const value = String(answerInput.value || '').trim()
  if (value === '') return

  mentalAnswers[task.id] = value
  persistMentalProgress()

  // Har bir javob darhol backendga saqlanadi. Bola chiqib ketib qayta kirsa,
  // oldingi javoblari va keyingi savol o'rni yo'qolmaydi.
  try {
    await api.post('/exam/mental-progress/', {
      code: payload.value.code,
      task_id: task.id,
      answer: value,
    })
  } catch (e) {
    // Internet vaqtincha uzilib qolsa ham localStorage saqlab turadi.
    console.warn('Mental progress save failed', e)
  }

  const nextIndex = currentMentalIndex.value + 1
  if (remainingSeconds.value <= 0 || nextIndex >= mentalTasks.value.length) {
    submitMentalExam()
  } else {
    playMentalTask(nextIndex)
  }
}

async function submitMentalExam() {
  if (submitted || !payload.value) return
  submitted = true
  submitting.value = true
  mentalPhase.value = 'finished'
  clearMentalTimers()

  const lastAttemptedIndex = Math.min(currentMentalIndex.value, mentalTasks.value.length - 1)
  const answerList = mentalTasks.value
    .filter((task, index) => index <= lastAttemptedIndex || mentalAnswers[task.id] !== undefined)
    .map(task => ({
      task_id: task.id,
      answer: mentalAnswers[task.id] ?? '',
    }))

  try {
    const res = await api.post('/exam/submit/', submitPayload({ answers: answerList }))
    sessionStorage.removeItem('exam_payload')
    localStorage.removeItem(mentalProgressKey())
    localStorage.removeItem(examProgressKey())
    showFinishSuccess(res.data)
  } catch (e) {
    submitted = false
    showFinishError(e.response?.data?.detail || 'Mental javoblarni yuborishda xatolik.')
  } finally {
    submitting.value = false
  }
}

async function submitExam() {
  if (submitted || !payload.value) return
  submitted = true
  submitting.value = true
  clearInterval(intervalId)
  const answerList = payload.value.questions.map(q => ({ question_id: q.id, answer: answers[q.id] || '' }))
  try {
    const res = await api.post('/exam/submit/', submitPayload({ answers: answerList }))
    sessionStorage.removeItem('exam_payload')
    localStorage.removeItem(examProgressKey())
    localStorage.removeItem(mentalProgressKey())
    showFinishSuccess(res.data)
  } catch (e) {
    submitted = false
    showFinishError(e.response?.data?.detail || 'Testni yakunlashda xatolik.')
  } finally {
    submitting.value = false
  }
}

function startTimer() {
  clearInterval(intervalId)
  intervalId = setInterval(() => {
    if (submitted) {
      clearInterval(intervalId)
      return
    }

    remainingSeconds.value = Math.max(0, remainingSeconds.value - 1)

    if (remainingSeconds.value <= 0) {
      remainingSeconds.value = 0
      clearInterval(intervalId)
      clearMentalTimers()
      if (isMental.value) submitMentalExam()
      else submitExam()
    }
  }, 1000)
}

onMounted(() => {
  const saved = sessionStorage.getItem('exam_payload')
  if (!saved) return
  payload.value = JSON.parse(saved)

  if (isMental.value) {
    // Mental arifmetikada vaqt code birinchi kiritilgan paytdan yuradi.
    // Agar o'quvchi chiqib ketib qayta kirsa, o'sha qolgan vaqt va keyingi
    // javob berilmagan savoldan davom etadi.
    const durationMinutes = Number(payload.value.duration_minutes || 10)
    prepareTimer(durationMinutes)

    loadMentalProgress()
    startTimer()

    if (currentMentalIndex.value >= mentalTasks.value.length) {
      submitMentalExam()
    } else {
      startMentalCountdown(currentMentalIndex.value)
    }
    return
  }

  // Oddiy testlarda ham vaqt code birinchi kiritilgan paytdan yuradi.
  // Chiqib ketib qayta kirsa, javoblar va qolgan vaqt o'sha joyidan davom etadi.
  const durationMinutes = Number(payload.value.duration_minutes || 30)
  prepareTimer(durationMinutes)
  loadTestProgress()
  startTimer()
})

onBeforeUnmount(() => {
  clearInterval(intervalId)
  clearMentalTimers()
})
</script>
