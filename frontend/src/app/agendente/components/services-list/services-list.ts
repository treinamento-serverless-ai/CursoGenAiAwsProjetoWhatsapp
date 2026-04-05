import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ServicesService } from '../../services/services';
import { Service } from '../../models';

@Component({
  selector: 'app-services-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatProgressSpinnerModule],
  templateUrl: './services-list.html',
  styleUrl: './services-list.scss',
})
export class ServicesList implements OnInit {
  private servicesService = inject(ServicesService);
  private cdr = inject(ChangeDetectorRef);

  services: Service[] = [];
  loading = false;
  lastKey: any = null;
  filterCategory = '';
  filterActive = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.cdr.markForCheck();
    const filters: any = { page_size: 25 };
    if (this.filterCategory) filters.category = this.filterCategory;
    if (this.filterActive !== '') filters.is_active = parseInt(this.filterActive);

    this.servicesService.getServices(filters).subscribe({
      next: (res) => {
        this.services = res.items || [];
        this.lastKey = res.last_evaluated_key;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  loadMore(): void {
    if (!this.lastKey) return;
    this.loading = true;
    this.cdr.markForCheck();
    this.servicesService
      .getServices({
        page_size: 25,
        last_evaluated_key: JSON.stringify(this.lastKey),
      })
      .subscribe({
        next: (res) => {
          this.services = [...this.services, ...(res.items || [])];
          this.lastKey = res.last_evaluated_key;
          this.loading = false;
          this.cdr.markForCheck();
        },
      });
  }

  toggleActive(svc: Service): void {
    this.servicesService
      .updateService(svc.service_id, {
        is_active: !svc.is_active,
      })
      .subscribe(() => {
        svc.is_active = !svc.is_active;
        this.cdr.markForCheck();
      });
  }
}
