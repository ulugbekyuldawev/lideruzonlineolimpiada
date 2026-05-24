<template>
  <div>
    <div class="page-head">
      <div>
        <h2>Natijalar</h2>
        <p>Test va mental arifmetika natijalari: o‘quvchi, fan, sinf, nechtadan nechta to‘g‘ri va foiz</p>
      </div>
      <button class="primary-btn" @click="downloadExcel">Natijalarni Excelga yuklash</button>
    </div>

    <div class="filter-bar">
      <button class="secondary-btn" @click="loadResults">Yangilash</button>
    </div>

    <div class="panel">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>№</th>
              <th>O‘quvchi</th>
              <th>Fan</th>
              <th>Sinfi</th>
              <th>Code</th>
              <th>Nechta to‘g‘ri</th>
              <th>Foiz</th>
              <th>Vaqt</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in results" :key="r.id">
              <td>{{ i + 1 }}</td>
              <td><b>{{ r.student_full_name }}</b></td>
              <td>{{ r.subject_name }}</td>
              <td>{{ r.level_name }}</td>
              <td>{{ r.student_code }}</td>
              <td><b>{{ r.correct_count }}/{{ r.total_questions }}</b></td>
              <td>{{ r.percent }}%</td>
              <td>{{ formatSeconds(r.spent_seconds) }}</td>
            </tr>
            <tr v-if="!results.length">
              <td colspan="8" class="empty-cell">Natija topilmadi</td>
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

const results = ref([])

function formatSeconds(seconds) {
  const total = Number(seconds || 0)
  const min = Math.floor(total / 60)
  const sec = total % 60
  return `${min} daq ${sec} sek`
}

async function loadResults() {
  const res = await api.get('/results/')
  results.value = res.data
}

async function downloadExcel() {
  const res = await api.get('/results/export-excel/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'olimpiada_natijalari.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

onMounted(loadResults)
</script>
