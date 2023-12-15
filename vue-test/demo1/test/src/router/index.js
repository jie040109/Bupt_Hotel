import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// 导入其他需要的组件
import CustomerRoomView from '../views/CustomerRoomView.vue'
import FrontDeskView from '../views/FrontDeskView.vue'
import ControlRoomView from '../views/ControlRoomView.vue'
import CreateRoomView from '../views/CreateRoomView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  //{
  //path: '/about',
  //name: 'about',
  // route level code-splitting
  // this generates a separate chunk (about.[hash].js) for this route
  // which is lazy-loaded when the route is visited.
  //component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  //}
  {
    path: '/room/:id',
    name: 'room',
    component: CustomerRoomView,
    props: true // 允许通过路由传递参数到组件
  },
  {
    path: '/front-desk',
    name: 'frontDesk',
    component: FrontDeskView
  },
  {
    path: '/control-room',
    name: 'controlRoom',
    component: ControlRoomView
  },
  {
    path: '/create-room',
    name: 'createRoom',
    component: CreateRoomView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
