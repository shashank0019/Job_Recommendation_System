// Test the frontend API_BASE construction logic
const RAW_API_BASE = 'http://localhost:5000'

const API_BASE = (() => {
  try {
    if (RAW_API_BASE.startsWith('http')) {
      return /\/api\/?$/.test(RAW_API_BASE) ? RAW_API_BASE.replace(/\/$/, '') : `${RAW_API_BASE.replace(/\/$/, '')}/api`
    }
  } catch {}
  return RAW_API_BASE
})()

console.log('RAW_API_BASE:', RAW_API_BASE)
console.log('API_BASE:', API_BASE)
console.log('Problems list URL:', `${API_BASE}/problems`)
console.log('Individual problem URL:', `${API_BASE}/problems/1`)
