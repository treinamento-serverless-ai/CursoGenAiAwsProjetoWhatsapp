import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth';

export const authGuard: CanActivateFn = async () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const isValid = await authService.ensureTokenValid();
  
  if (isValid) {
    return true;
  }

  return router.parseUrl('/login');
};
