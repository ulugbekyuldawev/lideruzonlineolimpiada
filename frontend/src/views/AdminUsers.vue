<template>
  <div>
    <div class="page-head">
      <div>
        <h2>Adminlar</h2>
        <p>Platforma uchun yangi admin login va parol yarating.</p>
      </div>
    </div>

    <div class="grid-2">
      <div class="panel">
        <h3>Admin yaratish</h3>
        <form @submit.prevent="createAdmin" class="form-grid">
          <label>Login <input v-model="form.username" required /></label>
          <label>Parol <input v-model="form.password" type="password" required minlength="6" /></label>
          <button class="primary-btn">Yaratish</button>
        </form>
        <p v-if="message" class="success-box">{{ message }}</p>
        <p v-if="error" class="error-box">{{ error }}</p>
      </div>

      <div class="panel">
        <h3>Adminlar ro‘yxati</h3>
        <div class="list-cards">
          <div v-for="admin in admins" :key="admin.id" class="mini-card">
            <b>{{ admin.username }}</b>
            <small>{{ admin.is_main_admin ? 'Bosh admin' : 'Admin' }}</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '../api/axios'

const admins = ref([])
const message = ref('')
const error = ref('')
const form = reactive({ username: '', password: '' })

async function loadAdmins() {
  const res = await api.get('/accounts/admins/')
  admins.value = res.data
}

async function createAdmin() {
  message.value = ''
  error.value = ''
  try {
    await api.post('/accounts/admins/', form)
    Object.assign(form, { username: '', password: '' })
    message.value = 'Admin yaratildi.'
    await loadAdmins()
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Xatolik')
  }
}

onMounted(loadAdmins)
</script>
