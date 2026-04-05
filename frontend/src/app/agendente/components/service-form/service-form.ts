import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ServicesService } from '../../services/services';
import { Service } from '../../models';

@Component({
  selector: 'app-service-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatProgressSpinnerModule],
  templateUrl: './service-form.html',
  styleUrl: './service-form.scss',
})
export class ServiceForm implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private servicesService = inject(ServicesService);
  private cdr = inject(ChangeDetectorRef);

  isEdit = false;
  loading = false;
  saving = false;

  service: Partial<Service> = {
    name: '',
    description: '',
    category: '',
    is_active: true,
  };

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id && id !== 'new') {
      this.isEdit = true;
      this.loadService(id);
    }
  }

  loadService(id: string): void {
    this.loading = true;
    this.cdr.markForCheck();
    this.servicesService.getService(id).subscribe({
      next: (svc) => {
        this.service = svc;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => this.router.navigate(['/services']),
    });
  }

  save(): void {
    this.saving = true;
    this.cdr.markForCheck();
    const obs = this.isEdit
      ? this.servicesService.updateService(this.service.service_id!, this.service)
      : this.servicesService.createService(this.service);

    obs.subscribe({
      next: () => this.router.navigate(['/services']),
      error: () => {
        this.saving = false;
        this.cdr.markForCheck();
      },
    });
  }
}
