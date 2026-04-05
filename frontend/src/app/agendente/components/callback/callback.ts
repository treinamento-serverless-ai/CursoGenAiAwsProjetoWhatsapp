import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-callback',
  standalone: true,
  template: '<p>Autenticando...</p>',
})
export class Callback implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authService = inject(AuthService);

  ngOnInit(): void {
    const code = this.route.snapshot.queryParamMap.get('code');
    if (code) {
      this.authService
        .handleCallback(code)
        .then(() => this.router.navigate(['/']))
        .catch(() => this.router.navigate(['/login']));
    } else {
      this.router.navigate(['/login']);
    }
  }
}
