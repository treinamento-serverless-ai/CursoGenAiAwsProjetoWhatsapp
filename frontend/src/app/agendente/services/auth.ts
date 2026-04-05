import { Injectable, signal, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { environment } from '../../../environments/environment.localhost';

interface UserInfo {
  name: string;
  email: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

  isAuthenticated = signal(this.hasToken());
  userInfo = signal<UserInfo | null>(this.getUserInfoFromToken());
  private validationPromise: Promise<boolean> | null = null;

  redirectToHostedUI(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const { domain, clientId, redirectUri } = environment.cognito;
    const loginUrl = `https://${domain}/login?client_id=${clientId}&response_type=code&scope=openid+email+profile&redirect_uri=${encodeURIComponent(redirectUri)}`;
    window.location.href = loginUrl;
  }

  handleCallback(code: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!isPlatformBrowser(this.platformId)) {
        reject('Not in browser');
        return;
      }

      const tokenUrl = `https://${environment.cognito.domain}/oauth2/token`;

      fetch(tokenUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'authorization_code',
          client_id: environment.cognito.clientId,
          code,
          redirect_uri: environment.cognito.redirectUri,
        }),
      })
        .then((res) => res.json())
        .then((tokens) => {
          localStorage.setItem('id_token', tokens.id_token);
          localStorage.setItem('access_token', tokens.access_token);
          localStorage.setItem('refresh_token', tokens.refresh_token);
          this.isAuthenticated.set(true);
          this.userInfo.set(this.getUserInfoFromToken());
          resolve();
        })
        .catch(reject);
    });
  }

  async ensureTokenValid(): Promise<boolean> {
    // Se não tem token, retorna false imediatamente
    if (!this.hasToken()) {
      return false;
    }

    // Se já está validando, retorna a mesma promise
    if (this.validationPromise) {
      return this.validationPromise;
    }

    // Inicia nova validação
    this.validationPromise = this.validateTokenWithAWS();
    const result = await this.validationPromise;
    this.validationPromise = null;
    return result;
  }

  async validateTokenWithAWS(): Promise<boolean> {
    const accessToken = this.getAccessToken();
    if (!accessToken) {
      this.handleInvalidToken(false);
      return false;
    }

    try {
      const response = await fetch(`https://${environment.cognito.domain}/oauth2/userInfo`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (response.ok) {
        this.isAuthenticated.set(true);
        return true;
      }

      const refreshed = await this.tryRefreshToken();
      
      if (refreshed) {
        return true;
      }

      this.handleInvalidToken(true);
      return false;

    } catch (error) {
      this.handleInvalidToken(true);
      return false;
    }
  }

  private async tryRefreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`https://${environment.cognito.domain}/oauth2/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'refresh_token',
          client_id: environment.cognito.clientId,
          refresh_token: refreshToken,
        }),
      });

      if (response.ok) {
        const tokens = await response.json();
        localStorage.setItem('id_token', tokens.id_token);
        localStorage.setItem('access_token', tokens.access_token);
        this.isAuthenticated.set(true);
        this.userInfo.set(this.getUserInfoFromToken());
        return true;
      }

      return false;
    } catch (error) {
      return false;
    }
  }

  private handleInvalidToken(showAlert: boolean = true): void {
    localStorage.removeItem('id_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.isAuthenticated.set(false);
    this.userInfo.set(null);
    
    if (showAlert) {
      this.snackBar.open('Sua sessão expirou. Por favor, faça login novamente.', 'OK', {
        duration: 5000,
        horizontalPosition: 'center',
        verticalPosition: 'bottom',
        panelClass: ['custom-snackbar'],
      });
    }
  }

  hasToken(): boolean {
    if (!isPlatformBrowser(this.platformId)) return false;
    return !!localStorage.getItem('access_token');
  }

  logout(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    
    localStorage.removeItem('id_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    this.isAuthenticated.set(false);
    this.userInfo.set(null);

    const { domain, clientId, logoutUri } = environment.cognito;
    window.location.href = `https://${domain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(logoutUri)}`;
  }

  getIdToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) return null;
    return localStorage.getItem('id_token');
  }

  getAccessToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) return null;
    return localStorage.getItem('access_token');
  }

  private getUserInfoFromToken(): UserInfo | null {
    if (!isPlatformBrowser(this.platformId)) return null;

    const token = localStorage.getItem('id_token');
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        name: payload.name || payload.email?.split('@')[0] || 'Usuário',
        email: payload.email || '',
      };
    } catch {
      return null;
    }
  }
}
