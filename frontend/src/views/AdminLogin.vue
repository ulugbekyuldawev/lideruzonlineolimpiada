<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="brand-circle brand-icon-only">🏆</div>
      <h1>LIDER.Uz Onlayn Olimpiada</h1>
      <p>Admin panelga xavfsiz kirish</p>

      <form @submit.prevent="login" class="form-grid">
        <label>
          Login
          <input v-model="form.username" placeholder="ulugbek" required />
        </label>
        <label>
          Parol
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </label>
        <button class="primary-btn" :disabled="loading">
          {{ loading ? 'Kirilmoqda...' : 'Kirish' }}
        </button>
      </form>

      <p v-if="error" class="error-box">{{ error }}</p>
      <RouterLink to="/student" class="student-panel-link">
        O‘quvchi panelga o‘tish
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import { fetchCurrentAdmin } from '../utils/auth'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = reactive({ username: 'ulugbek', password: '' })

async function login() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/auth/login/', form)
    localStorage.setItem('access', res.data.access)
    localStorage.setItem('refresh', res.data.refresh)
    await fetchCurrentAdmin()
    router.push('/admin/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login yoki parol xato.'
  } finally {
    loading.value = false
  }
}
</script>
