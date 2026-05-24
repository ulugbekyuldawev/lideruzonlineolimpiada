<template>
  <div>
    <div class="page-head">
      <div>
        <h2>Excel orqali o‘quvchi yuklash</h2>
        <p>Excel fayldan o‘quvchilarni yuklang va ularga avtomatik status code yarating.</p>
      </div>
    </div>

    <div class="grid-2">
      <div class="panel">
        <h3>Excel fayl tanlang</h3>
        <div class="upload-box">
          <input type="file" accept=".xlsx,.xls" @change="onFileChange" />
          <p>Kerakli ustunlar: №, Ism familya, O'quv markaz nomi, Fan, Sinfi</p>
        </div>

        <button class="primary-btn" :disabled="!file || loading" @click="upload">
          {{ loading ? 'Yuklanmoqda...' : 'Excelni yuklash' }}
        </button>

        <p v-if="message" class="success-box">{{ message }}</p>
        <p v-if="error" class="error-box">{{ error }}</p>

        <div v-if="createdStudents.length" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Ism familya</th>
                <th>O'quv markaz nomi</th>
                <th>Fan</th>
                <th>Sinfi</th>
                <th>Code</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in createdStudents" :key="student.id">
                <td>{{ student.full_name }}</td>
                <td>{{ student.center_name }}</td>
                <td>{{ student.subject_name }}</td>
                <td>{{ student.level_name }}</td>
                <td><b>{{ student.code }}</b></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="panel">
        <h3>Excel namunasi</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>№</th>
                <th>Ism familya</th>
                <th>O'quv markaz nomi</th>
                <th>Fan</th>
                <th>Sinfi</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td>Ali Valiyev</td>
                <td>LIDER.Uz Onlayn Olimpiada</td>
                <td>Ingliz tili</td>
                <td>1-sinf</td>
              </tr>
              <tr>
                <td>2</td>
                <td>Madina Karimova</td>
                <td>LIDER.Uz Onlayn Olimpiada</td>
                <td>Ingliz tili</td>
                <td>2-sinf</td>
              </tr>
              <tr>
                <td>3</td>
                <td>Jasur Sobirov</td>
                <td>LIDER.Uz Onlayn Olimpiada</td>
                <td>Ingliz tili</td>
                <td>3-sinf</td>
              </tr>
              <tr>
                <td>4</td>
                <td>Dilshod Ergashev</td>
                <td>LIDER.Uz Onlayn Olimpiada</td>
                <td>Mental arifmetika</td>
                <td>5 yosh</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="hint-text">
          Excel ustunlari aynan shunday bo‘lsin: №, Ism familya, O'quv markaz nomi, Fan, Sinfi. Ingliz tili uchun Sinfi ustuniga 1-sinf, 2-sinf, 3-sinf, 4-sinf, 5-sinf, 6-sinf yoki 7-sinf yozing. Markaz nomi bo‘sh bo‘lsa LIDER.Uz Onlayn Olimpiada olinadi.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/axios'

const file = ref(null)
const loading = ref(false)
const message = ref('')
const error = ref('')
const createdStudents = ref([])

function onFileChange(event) {
  file.value = event.target.files[0]
  message.value = ''
  error.value = ''
  createdStudents.value = []
}

async function upload() {
  if (!file.value) return
  loading.value = true
  message.value = ''
  error.value = ''
  createdStudents.value = []

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    const res = await api.post('/students/import-excel/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    createdStudents.value = res.data.students || []
    const errors = res.data.errors || []
    message.value = `${res.data.created_count} ta o‘quvchi yaratildi va random code berildi.`
    if (errors.length) {
      error.value = `${errors.length} ta qatorda xatolik bor: ${JSON.stringify(errors)}`
    }
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Xatolik')
  } finally {
    loading.value = false
  }
}
</script>
