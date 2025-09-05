import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy load components for better performance
const Dashboard = () => import('@/views/Dashboard.vue')
const Login = () => import('@/views/Login.vue')
const Register = () => import('@/views/Register.vue')
const Activities = () => import('@/views/Activities.vue')
const LogActivity = () => import('@/views/LogActivity.vue')
const Challenges = () => import('@/views/Challenges.vue')
const Leaderboards = () => import('@/views/Leaderboards.vue')
const Badges = () => import('@/views/Badges.vue')
const Social = () => import('@/views/Social.vue')
const Profile = () => import('@/views/Profile.vue')

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register', 
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/activities',
    name: 'Activities',
    component: Activities,
    meta: { requiresAuth: true }
  },
  {
    path: '/log-activity',
    name: 'LogActivity',
    component: LogActivity,
    meta: { requiresAuth: true }
  },
  {
    path: '/challenges',
    name: 'Challenges',
    component: Challenges,
    meta: { requiresAuth: true }
  },
  {
    path: '/leaderboards',
    name: 'Leaderboards',
    component: Leaderboards,
    meta: { requiresAuth: true }
  },
  {
    path: '/badges',
    name: 'Badges',
    component: Badges,
    meta: { requiresAuth: true }
  },
  {
    path: '/social',
    name: 'Social',
    component: Social,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router