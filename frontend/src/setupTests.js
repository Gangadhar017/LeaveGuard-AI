import '@testing-library/jest-dom'

// jsdom lacks createObjectURL — used by the upload preview
if (!window.URL.createObjectURL) {
  window.URL.createObjectURL = () => 'blob:mock-url'
  window.URL.revokeObjectURL = () => {}
}
