/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// import { setupLayouts } from 'virtual:generated-layouts'
// Composables
import { createRouter, createWebHistory } from 'vue-router'
import hello from '@/components/HelloWorld.vue'
import defaultlayout from '@/layouts/default.vue'
// import { routes } from 'vue-router/auto-routes'
import init from '@/layouts/init.vue'
import admin from '@/pages/admin.vue'
import AI from '@/pages/AI.vue'
import CreateTripPage from '@/pages/CreateTripPage.vue'
import forgotPassword from '@/pages/forgot-password.vue'
import login from '@/pages/login.vue'
import Message from '@/pages/message.vue'
import plan from '@/pages/plan.vue'
import Profile from '@/pages/profile.vue'
import register from '@/pages/register.vue'
import Trip from '@/pages/trip.vue'
import welcomehome from '@/pages/welcomehome.vue'
const routes = [
  {
    path: '/',
    component: init,
  },
  {
    path: '/main',
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
      {
        path: '/AI',
        name: 'AI',
        component: AI,
      },
      {
        path: '/plan',
        name: 'plan',
        component: plan,
      },
      {
        path: '/trip/:tripId',
        name: 'Trip',
        component: Trip,
        // 如果你想把 tripId / tripName 作为 props 传入，也可以这样：
        props: route => ({
          tripId: Number(route.params.tripId),
          tripName: route.query.tripName,
        }),
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
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
  },
  {
    path: '/create-trip',
    name: 'CreateTrip',
    component: CreateTripPage,
  },
  {
    path: '/message',
    name: 'Message',
    component: Message,
  },
  {
    path: '/admin', // 新增admin路由
    name: 'Admin',
    component: admin,
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
// -----------------------------------------------------
// 全局路由守卫：登录控制 + 管理员权限控制
// -----------------------------------------------------
router.beforeEach((to, from, next) => {
  // 获取 localStorage 中的用户信息
  const userStr = localStorage.getItem('user')
  let user = null

  if (userStr) {
    try {
      user = JSON.parse(userStr)
    } catch {
      console.error('解析用户信息失败，已清除本地存储')
      localStorage.removeItem('user')
      user = null
    }
  }

  const isLoggedIn = !!user?.user_id
  const isAdmin = user?.admin_id !== null && user?.admin_id !== undefined

  // ====== 不需要登录即可访问的页面 ======
  const publicPages = ['/login', '/register', '/forgot-password', '/']

  // -------------------------------------------------------
  // ① 未登录用户：禁止访问其他页面 → 自动跳到 /login
  // -------------------------------------------------------
  if (!isLoggedIn && !publicPages.includes(to.path)) {
    return next('/login')
  }

  // -------------------------------------------------------
  // ② 已登录但访问管理员页面 → 必须 admin_id 才允许
  // -------------------------------------------------------
  if (to.path.startsWith('/admin') && !isAdmin) {
    alert('您没有管理员权限')
    return next('/home')
  }

  // -------------------------------------------------------
  // ③ 已登录用户访问 /login → 自动转回主页（或 admin）
  // -------------------------------------------------------
  if (isLoggedIn && to.path === '/login') {
    if (isAdmin) {
      return next('/admin')
    }
    return next('/home')
  }

  // 通过验证
  next()
})

export default router
