import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './pages/HomePage.vue'
import AboutPage from './pages/AboutPage.vue'
import HowItWorks from './pages/HowItWorks.vue'
import EnvironmentalImpact from './pages/EnvironmentalImpact.vue'
import NotFound from './pages/NotFound.vue'

const routes = [
  { path: '/', name: "home", component: HomePage },
  { path: '/how-it-works', name: 'howItWorks', component: HowItWorks },
  { path: '/about', name: 'about', component: AboutPage },
  { path: '/environmental-impact', name: 'environmentalImpact', component: EnvironmentalImpact },
  {
    path: "/batches/:id",
    name: "batch",
    component: () => import("@/pages/BatchView.vue"), // your crop/review UI
    props: true,
  },
  {
    path: "/batches/:id/crop",
    name: "cropWizard",
    component: () => import("@/pages/CropWizard.vue"), // your crop/review UI
    props: true,
  },
  {
    path: "/batches/:id/label",
    name: "labelWizard",
    component: () => import("@/pages/LabelWizard.vue"), // the side by side label UI
    props: true,
  },

  {
    path: "/:pathMatch(.*)*",
    name: "notFound",
    component: NotFound,
  },

  // Add more routes here as needed
]

export default createRouter({
  history: createWebHistory(), // history mode
  routes,
})
