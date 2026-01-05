import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Dashboard from '../views/Dashboard.vue';
import Schedule from '../views/Schedule.vue';
import ScheduleCalendar from '../views/ScheduleCalendar.vue';
import Doctors from '../views/Doctors.vue';
import Departments from '../views/Departments.vue';
import Rooms from '../views/Rooms.vue';
import ShiftTypes from '../views/ShiftTypes.vue';
import TradeApproval from '../views/TradeApproval.vue';
import Preferences from '../views/Preferences.vue';
import Statistics from '../views/Statistics.vue';
import Settings from '../views/Settings.vue';
import AuditLogs from '../views/AuditLogs.vue';
import Feedback from '../views/Feedback.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { guest: true }
    },
    {
        path: '/',
        component: Dashboard,
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                redirect: '/schedule-calendar'
            },
            {
                path: '/schedule',
                name: 'Schedule',
                component: Schedule
            },
            {
                path: '/schedule-calendar',
                name: 'ScheduleCalendar',
                component: ScheduleCalendar
            },
            {
                path: '/doctors',
                name: 'Doctors',
                component: Doctors
            },
            {
                path: '/departments',
                name: 'Departments',
                component: Departments
            },
            {
                path: '/rooms',
                name: 'Rooms',
                component: Rooms
            },
            {
                path: '/shift-types',
                name: 'ShiftTypes',
                component: ShiftTypes
            },
            {
                path: '/trade-approval',
                name: 'TradeApproval',
                component: TradeApproval
            },
            {
                path: '/preferences',
                name: 'Preferences',
                component: Preferences
            },
            {
                path: '/statistics',
                name: 'Statistics',
                component: Statistics
            },
            {
                path: '/settings',
                name: 'Settings',
                component: Settings
            },
            {
                path: '/audit-logs',
                name: 'AuditLogs',
                component: AuditLogs
            },
            {
                path: '/feedback',
                name: 'Feedback',
                component: Feedback
            }
        ]
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    if (to.meta.requiresAuth && !token) {
        next('/login');
    } else if (to.meta.guest && token) {
        next('/');
    } else {
        next();
    }
});

export default router;
