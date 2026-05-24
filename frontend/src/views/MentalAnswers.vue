<template>
  <div>
    <div class="page-head">
      <div>
        <h2>Mental javoblari</h2>
        <p>Mental arifmetika ishlagan o‘quvchilar, ularning javoblari va qaysi misol to‘g‘ri/noto‘g‘ri bo‘lgani</p>
      </div>
      <button class="primary-btn" @click="downloadExcel">Mental javoblarini yuklash</button>
    </div>

    <div class="filter-bar">
      <button class="secondary-btn" @click="loadMentalResults">Yangilash</button>
    </div>

    <div class="panel">
      <div class="table-wrap">
        <table class="mental-admin-table">
          <thead>
            <tr>
              <th>№</th>
              <th>O‘quvchi</th>
              <th>Fan / Sinfi</th>
              <th>Code</th>
              <th>Nechta to‘g‘ri</th>
              <th>Foiz</th>
              <th>Vaqt</th>
              <th>Yechgan javoblari</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in mentalResults" :key="r.id">
              <td>{{ i + 1 }}</td>
              <td><b>{{ r.student_full_name }}</b></td>
              <td>{{ r.subject_name }} / {{ r.level_name }}</td>
              <td>{{ r.student_code }}</td>
              <td>
                <span class="mental-summary-pill">{{ r.correct_count }}/{{ r.total_questions }} ta</span>
              </td>
              <td>{{ r.percent }}%</td>
              <td>{{ formatSeconds(r.spent_seconds) }}</td>
              <td>
                <div class="mental-answer-list mental-answer-list-wide">
                  <span v-for="item in r.mental_answers" :key="item.id" :class="item.is_correct ? 'ok' : 'bad'">
                    {{ item.task_order }}. {{ item.expression }} = {{ item.student_answer ?? '—' }} / {{ item.correct_answer }}
                  </span>
                </div>
              </td>
            </tr>
            <tr v-if="!mentalResults.length">
              <td colspan="8" class="empty-cell">Mental javoblari topilmadi</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api/axios'

const mentalResults = ref([])

function formatSeconds(seconds) {
  const total = Number(seconds || 0)
  const min = Math.floor(total / 60)
  const sec = total % 60
  return `${min} daq ${sec} sek`
}

async function loadMentalResults() {
  const res = await api.get('/results/mental-answers/')
  mentalResults.value = res.data
}

async function downloadExcel() {
  const res = await api.get('/results/mental-answers-export/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'mental_javoblari.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

onMounted(loadMentalResults)
</script>
