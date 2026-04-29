import { createApp } from 'vue'
import {
  FrappeUI,
  Button,
  Input,
  TextInput,
  Textarea,
  Select,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  LoadingIndicator,
  FeatherIcon,
  resourcesPlugin,
  frappeRequest,
  setConfig,
} from 'frappe-ui'
import App from './App.vue'
import './index.css'

const app = createApp(App)

setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)
app.use(resourcesPlugin)

const globalComponents = {
  Button,
  Input,
  TextInput,
  Textarea,
  Select,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  LoadingIndicator,
  FeatherIcon,
}

for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

app.mount('#app')
