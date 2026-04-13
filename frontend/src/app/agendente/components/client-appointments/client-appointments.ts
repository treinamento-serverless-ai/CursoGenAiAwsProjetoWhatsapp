import { Component, inject, input, effect, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AppointmentsService } from '../../services/appointments';
import { ProfessionalsService } from '../../services/professionals';
import { ServicesService } from '../../services/services';
import { Appointment, Professional, Service } from '../../models';

@Component({
  selector: 'app-client-appointments',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './client-appointments.html',
  styleUrl: './client-appointments.scss',
})
export class ClientAppointments {
  private appointmentsService = inject(AppointmentsService);
  private professionalsService = inject(ProfessionalsService);
  private servicesService = inject(ServicesService);
  private cdr = inject(ChangeDetectorRef);

  clientPhone = input.required<string>();
  clientName = input<string>('');

  appointments: Appointment[] = [];
  professionals: Professional[] = [];
  services: Service[] = [];
  loading = false;
  showForm = false;

  // Form fields
  formDate = '';
  formTime = '';
  formProfessional = '';
  formService = '';
  saving = false;

  constructor() {
    effect(() => {
      const phone = this.clientPhone();
      if (phone) this.loadAppointments();
    });
  }

  ngOnInit(): void {
    this.professionalsService.getProfessionals({ is_active: 1 }).subscribe({
      next: (res) => { this.professionals = res.items || []; this.cdr.markForCheck(); },
    });
    this.servicesService.getServices({ is_active: 1 }).subscribe({
      next: (res) => { this.services = res.items || []; this.cdr.markForCheck(); },
    });
  }

  loadAppointments(): void {
    this.loading = true;
    this.cdr.markForCheck();
    this.appointmentsService.getAppointments({ client_phone: this.clientPhone(), page_size: 50 }).subscribe({
      next: (res) => {
        this.appointments = (res.items || []).sort((a, b) => a.appointment_date.localeCompare(b.appointment_date));
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => { this.loading = false; this.cdr.markForCheck(); },
    });
  }

  get futureAppointments(): Appointment[] {
    const now = new Date().toISOString();
    return this.appointments.filter(a => a.appointment_date >= now && a.status !== 'cancelled');
  }

  get pastAppointments(): Appointment[] {
    const now = new Date().toISOString();
    return this.appointments.filter(a => a.appointment_date < now || a.status === 'cancelled');
  }

  cancelAppointment(appt: Appointment): void {
    if (!confirm(`Cancelar agendamento de ${appt.service_name}?`)) return;
    this.appointmentsService.cancelAppointment(appt.appointment_id).subscribe({
      next: () => {
        appt.status = 'cancelled';
        this.cdr.markForCheck();
      },
    });
  }

  toggleForm(): void {
    this.showForm = !this.showForm;
    if (this.showForm) {
      const now = new Date();
      this.formDate = now.toISOString().split('T')[0];
      this.formTime = '09:00';
      this.formProfessional = '';
      this.formService = '';
    }
  }

  createAppointment(): void {
    if (!this.formDate || !this.formTime || !this.formProfessional || !this.formService) return;

    const prof = this.professionals.find(p => p.professional_id === this.formProfessional);
    const svc = this.services.find(s => s.service_id === this.formService);

    const appointment: Partial<Appointment> = {
      appointment_id: crypto.randomUUID(),
      appointment_date: `${this.formDate}T${this.formTime}:00`,
      client_phone: this.clientPhone(),
      client_name: this.clientName() || this.clientPhone(),
      professional_id: this.formProfessional,
      professional_name: prof?.name || '',
      service_id: this.formService,
      service_name: svc?.name || '',
      status: 'scheduled',
    };

    this.saving = true;
    this.cdr.markForCheck();
    this.appointmentsService.createAppointment(appointment).subscribe({
      next: () => {
        this.appointments.push(appointment as Appointment);
        this.appointments.sort((a, b) => a.appointment_date.localeCompare(b.appointment_date));
        this.showForm = false;
        this.saving = false;
        this.cdr.markForCheck();
      },
      error: () => { this.saving = false; this.cdr.markForCheck(); },
    });
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      scheduled: 'Agendado', completed: 'Concluído', cancelled: 'Cancelado', no_show: 'Não compareceu',
    };
    return labels[status] || status;
  }

  getStatusClass(status: string): string {
    return status.toLowerCase();
  }
}
