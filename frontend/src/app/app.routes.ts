import { Routes } from '@angular/router';
import { authGuard } from './agendente/guards/auth-guard';
import { loginGuard } from './agendente/guards/login-guard';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [loginGuard],
    loadComponent: () => import('./agendente/components/login/login').then((m) => m.Login),
  },
  {
    path: 'callback',
    loadComponent: () => import('./agendente/components/callback/callback').then((m) => m.Callback),
  },
  {
    path: 'privacy-policy',
    loadComponent: () =>
      import('./agendente/components/privacy-policy/privacy-policy').then((m) => m.PrivacyPolicy),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./agendente/components/layout/layout').then((m) => m.Layout),
    children: [
      { 
        path: '', 
        loadComponent: () => import('./agendente/components/home/home').then((m) => m.Home),
      },
      {
        path: 'attendance',
        loadComponent: () =>
          import('./agendente/components/whatsapp-panel/whatsapp-panel').then(
            (m) => m.WhatsappPanel,
          ),
      },
      {
        path: 'calendar',
        loadComponent: () =>
          import('./agendente/components/calendar-view/calendar-view').then((m) => m.CalendarView),
      },
      {
        path: 'appointments',
        loadComponent: () =>
          import('./agendente/components/appointments-list/appointments-list').then(
            (m) => m.AppointmentsList,
          ),
      },
      {
        path: 'professionals',
        loadComponent: () =>
          import('./agendente/components/professionals-list/professionals-list').then(
            (m) => m.ProfessionalsList,
          ),
      },
      {
        path: 'professionals/new',
        loadComponent: () =>
          import('./agendente/components/professional-form/professional-form').then(
            (m) => m.ProfessionalForm,
          ),
      },
      {
        path: 'professionals/:id',
        loadComponent: () =>
          import('./agendente/components/professional-form/professional-form').then(
            (m) => m.ProfessionalForm,
          ),
      },
      {
        path: 'services',
        loadComponent: () =>
          import('./agendente/components/services-list/services-list').then((m) => m.ServicesList),
      },
      {
        path: 'services/new',
        loadComponent: () =>
          import('./agendente/components/service-form/service-form').then((m) => m.ServiceForm),
      },
      {
        path: 'services/:id',
        loadComponent: () =>
          import('./agendente/components/service-form/service-form').then((m) => m.ServiceForm),
      },
      {
        path: 'clients',
        loadComponent: () =>
          import('./agendente/components/clients-list/clients-list').then((m) => m.ClientsList),
      },
      {
        path: 'clients/:phone',
        loadComponent: () =>
          import('./agendente/components/client-details/client-details').then(
            (m) => m.ClientDetails,
          ),
      },
      {
        path: 'config',
        loadComponent: () =>
          import('./agendente/components/config-panel/config-panel').then((m) => m.ConfigPanel),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
