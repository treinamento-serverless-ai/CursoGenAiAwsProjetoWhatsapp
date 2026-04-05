import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ProfessionalsService } from '../../services/professionals';
import { ServicesService } from '../../services/services';
import { Professional, ProfessionalService, Service } from '../../models';

@Component({
  selector: 'app-professional-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatProgressSpinnerModule],
  templateUrl: './professional-form.html',
  styleUrl: './professional-form.scss',
})
export class ProfessionalForm implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private professionalsService = inject(ProfessionalsService);
  private servicesService = inject(ServicesService);
  private cdr = inject(ChangeDetectorRef);

  isEdit = false;
  loading = false;
  saving = false;
  availableServices: Service[] = [];

  professional: Partial<Professional> = {
    name: '',
    specialty: '',
    career_start_date: '',
    social_media_link: '',
    working_days: [],
    working_hours: { start: '09:00', end: '18:00' },
    services: [],
    scheduling_policy: {
      type: 'FLEXIBLE_MINUTES',
      allowed_start_minutes: [0, 30],
      slot_window_hours: 1,
    },
    is_active: true,
  };

  weekDays = [
    { key: 'monday', label: 'Segunda' },
    { key: 'tuesday', label: 'Terca' },
    { key: 'wednesday', label: 'Quarta' },
    { key: 'thursday', label: 'Quinta' },
    { key: 'friday', label: 'Sexta' },
    { key: 'saturday', label: 'Sabado' },
    { key: 'sunday', label: 'Domingo' },
  ];

  ngOnInit(): void {
    this.loadServices();
    const id = this.route.snapshot.paramMap.get('id');
    if (id && id !== 'new') {
      this.isEdit = true;
      this.loadProfessional(id);
    }
  }

  loadServices(): void {
    this.servicesService.getServices({ is_active: 1 }).subscribe({
      next: (res) => {
        this.availableServices = res.items || [];
        this.cdr.markForCheck();
      },
    });
  }

  loadProfessional(id: string): void {
    this.loading = true;
    this.cdr.markForCheck();
    
    this.professionalsService.getProfessional(id).subscribe({
      next: (prof) => {
        this.professional = prof;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
        this.router.navigate(['/professionals']);
      },
    });
  }

  toggleDay(day: string): void {
    const days = this.professional.working_days || [];
    const idx = days.indexOf(day);
    if (idx >= 0) days.splice(idx, 1);
    else days.push(day);
    this.professional.working_days = days;
    this.cdr.markForCheck();
  }

  isDaySelected(day: string): boolean {
    return this.professional.working_days?.includes(day) || false;
  }

  addService(): void {
    this.professional.services = [
      ...(this.professional.services || []),
      {
        service_id: '',
        service_name: '',
        duration_hours: 1,
        price: 0,
      },
    ];
    this.cdr.markForCheck();
  }

  removeService(index: number): void {
    this.professional.services?.splice(index, 1);
    this.cdr.markForCheck();
  }

  onServiceSelect(index: number, serviceId: string): void {
    const service = this.availableServices.find((s) => s.service_id === serviceId);
    if (service && this.professional.services) {
      this.professional.services[index].service_id = service.service_id;
      this.professional.services[index].service_name = service.name;
    }
    this.cdr.markForCheck();
  }

  save(): void {
    this.saving = true;
    this.cdr.markForCheck();
    
    const obs = this.isEdit
      ? this.professionalsService.updateProfessional(
          this.professional.professional_id!,
          this.professional,
        )
      : this.professionalsService.createProfessional(this.professional);

    obs.subscribe({
      next: () => this.router.navigate(['/professionals']),
      error: () => {
        this.saving = false;
        this.cdr.markForCheck();
      },
    });
  }
}
