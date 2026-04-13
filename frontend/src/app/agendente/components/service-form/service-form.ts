import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { forkJoin } from 'rxjs';
import { ServicesService } from '../../services/services';
import { ProfessionalsService } from '../../services/professionals';
import { Service, Professional } from '../../models';

interface ProfessionalLink {
  professional_id: string;
  name: string;
  linked: boolean;
  duration_hours: number;
  price: number;
}

@Component({
  selector: 'app-service-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatProgressSpinnerModule, MatButtonToggleModule],
  templateUrl: './service-form.html',
  styleUrl: './service-form.scss',
})
export class ServiceForm implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private servicesService = inject(ServicesService);
  private professionalsService = inject(ProfessionalsService);
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

  professionalLinks: ProfessionalLink[] = [];
  private originalProfessionals: Professional[] = [];

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id && id !== 'new') {
      this.isEdit = true;
      this.loadData(id);
    }
  }

  loadData(id: string): void {
    this.loading = true;
    this.cdr.markForCheck();

    forkJoin({
      service: this.servicesService.getService(id),
      professionals: this.professionalsService.getProfessionals(),
    }).subscribe({
      next: ({ service, professionals }) => {
        this.service = service;
        this.originalProfessionals = professionals.items || [];
        this.professionalLinks = this.originalProfessionals.map((prof) => {
          const existing = prof.services?.find((s) => s.service_id === id);
          return {
            professional_id: prof.professional_id,
            name: prof.name,
            linked: !!existing,
            duration_hours: existing?.duration_hours ?? 1,
            price: existing?.price ?? 0,
          };
        });
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => this.router.navigate(['/services']),
    });
  }

  save(): void {
    this.saving = true;
    this.cdr.markForCheck();

    const saveService$ = this.isEdit
      ? this.servicesService.updateService(this.service.service_id!, this.service)
      : this.servicesService.createService(this.service);

    saveService$.subscribe({
      next: (res) => {
        const serviceId = this.service.service_id || res?.service_id;
        const serviceName = this.service.name || '';

        if (!this.isEdit || this.originalProfessionals.length === 0) {
          this.router.navigate(['/services']);
          return;
        }

        // Build update requests for professionals whose link status changed
        const updates$ = this.originalProfessionals
          .map((prof) => {
            const link = this.professionalLinks.find(
              (l) => l.professional_id === prof.professional_id,
            );
            if (!link) return null;

            const hadService = prof.services?.some((s) => s.service_id === serviceId);
            if (link.linked === !!hadService && hadService) {
              // Check if price/duration changed
              const existing = prof.services?.find((s) => s.service_id === serviceId);
              if (
                existing &&
                existing.duration_hours === link.duration_hours &&
                existing.price === link.price
              ) {
                return null;
              }
            }
            if (!link.linked && !hadService) return null;

            const updatedServices = link.linked
              ? [
                  ...(prof.services || []).filter((s) => s.service_id !== serviceId),
                  {
                    service_id: serviceId!,
                    service_name: serviceName,
                    duration_hours: link.duration_hours,
                    price: link.price,
                  },
                ]
              : (prof.services || []).filter((s) => s.service_id !== serviceId);

            return this.professionalsService.updateProfessional(prof.professional_id, {
              services: updatedServices,
            });
          })
          .filter((obs) => obs !== null);

        if (updates$.length === 0) {
          this.router.navigate(['/services']);
          return;
        }

        forkJoin(updates$).subscribe({
          next: () => this.router.navigate(['/services']),
          error: () => {
            this.saving = false;
            this.cdr.markForCheck();
          },
        });
      },
      error: () => {
        this.saving = false;
        this.cdr.markForCheck();
      },
    });
  }
}
