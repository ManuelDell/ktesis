import { ref } from 'vue'

// Module-level: shared across all component instances
const isKtesisAdmin = ref(false)
const authLoaded = ref(false)

export function useAuth() {
  function setAdminStatus(val) {
    isKtesisAdmin.value = !!val
    authLoaded.value = true
  }
  return { isKtesisAdmin, authLoaded, setAdminStatus }
}
