/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// import { setupLayouts } from 'virtual:generated-layouts'
// Composables
import { createRouter, createWebHistory } from 'vue-router'
import hello from '@/components/HelloWorld.vue'
// import { routes } from 'vue-router/auto-routes'
import defaultlayout from '@/layouts/default.vue'
import login from '@/pages/login.vue'
import register from '@/pages/register.vue'
import forgotPassword from "@/pages/forgot-password.vue";
import welcomehome from '@/pages/welcomehome.vue'
const routes = [
  {
    path: '/',
    component: defaultlayout,
    children: [
      {
        path: '/hello',
        component: hello,
      },
      {
        path: '/home',
        component: welcomehome,
      },
    ],
  },
  {
    path: '/login',
    component: login,
  },
  {
    path: '/register',
    component: register,
  },
  {
    path: '/forgot-password',
    component: forgotPassword,
  },
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // routes: setupLayouts(routes),
})

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (localStorage.getItem('vuetify:dynamic-reload')) {
      console.error('Dynamic import error, reloading page did not fix it', err)
    } else {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
