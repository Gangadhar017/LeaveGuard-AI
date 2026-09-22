import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
})

/** Maps any thrown error into a user-friendly message. */
export function getApiError(error) {
  if (error.code === 'ECONNABORTED') {
    return 'The request timed out. Please try again.'
  }
  if (error.response) {
    const data = error.response.data
    if (data?.error?.message) return data.error.message
    if (data?.detail) {
      return typeof data.detail === 'string'
        ? data.detail
        : 'The server rejected the request. Please check the uploaded file.'
    }
    return `Server error (${error.response.status}).`
  }
  if (error.request) {
    return 'Cannot reach the LeafGuard API. Is the backend running on ' + API_BASE_URL + '?'
  }
  return error.message || 'Something went wrong.'
}

export const leafguardApi = {
  health: () => client.get('/health'),

  predict: (file, onUploadProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/api/v1/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    })
  },

  listPredictions: (params) => client.get('/api/v1/predictions', { params }),
  getPrediction: (id) => client.get(`/api/v1/predictions/${id}`),
  deletePrediction: (id) => client.delete(`/api/v1/predictions/${id}`),
  stats: () => client.get('/api/v1/stats'),
}
