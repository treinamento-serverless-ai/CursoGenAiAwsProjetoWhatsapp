import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../services/auth';
import { ConfigService } from '../../services/config';

@Component({
  selector: 'app-layout',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, MatIconModule],
  templateUrl: './layout.html',
  styleUrl: './layout.scss',
})
export class Layout {
  authService = inject(AuthService);
  private configService = inject(ConfigService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  aiGlobalEnabled = true;
  menuOpen = false;

  toggleAiGlobal(): void {
    this.aiGlobalEnabled = !this.aiGlobalEnabled;
    this.cdr.markForCheck();
    this.configService.getConfig().subscribe({
      next: (response) => {
        const updatedConfig = {
          ...response.current_config,
          ai_global_enabled: this.aiGlobalEnabled
        };
        this.configService.updateConfig({ config: updatedConfig }).subscribe({
          next: () => this.cdr.markForCheck()
        });
      }
    });
  }

  logout(): void {
    this.authService.logout();
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }
}
