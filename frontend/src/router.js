import Vue from 'vue'
import Router from 'vue-router'
import RepoDetails from './components/RepoDetails'
import MainSec from './components/MainSec'
import Main from './components/Main'
import Details from './components/Details'
import Branches from './components/Branches'
import BranchDetails from './components/BranchDetails'
import Dashboard from './components/Dashboard'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      component: Main,
      redirect: '/dashboard',
      children: [{
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
      },        
      {
        path: 'repos/:name',
        name: 'Repos',
        component: Branches,
        props: true
      },
      {
        path: 'repos/:name/:branch',
        name: 'RepoDetails',
        component: RepoDetails,
        props: true
      },
      {
        path: 'repos/:name/:branch/:id',
        name: 'BranchDetails',
        component: BranchDetails,
        props: true
      },
      {
        path: 'projects/:name',
        name: 'Projects',
        component: MainSec,
        props: true
      },
      {
        path: 'projects/:name/:id',
        name: 'ProjectsId',
        component: Details,
        props: true
      }
      ]
    }
  ]
})
