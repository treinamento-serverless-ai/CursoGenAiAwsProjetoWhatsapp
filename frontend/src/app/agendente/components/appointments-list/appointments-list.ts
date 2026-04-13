import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AppointmentsService } from '../../services/appointments';
import { ProfessionalsService } from '../../services/professionals';
import { Appointment, Professional } from '../../models';

@Component({
  selector: 'app-appointments-list',
  standalone: true,
  imports: [CommonModule, FormsModule, MatProgressSpinnerModule],
  templateUrl: './appointments-list.html',
  styleUrl: './appointments-list.scss',
})
export class AppointmentsList implements OnInit {
  private appointmentsService = inject(AppointmentsService);
  private professionalsService = inject(ProfessionalsService);
  private cdr = inject(ChangeDetectorRef);

  appointments: Appointment[] = [];
  professionals: Professional[] = [];
  loading = false;
  lastKey: any = null;
  filterProfessional = '';
  filterStatus = '';

  ngOnInit(): void {
    this.loadProfessionals();
    this.load();
  }

  loadProfessionals(): void {
    this.professionalsService.getProfessionals({ is_active: 1 }).subscribe({
      next: (res) => {
        this.professionals = res.items || [];
        this.cdr.markForCheck();
      },
    });
  }

  load(): void {
    this.loading = true;
    this.cdr.markForCheck();
    const filters: any = { page_size: 25 };
    if (this.filterProfessional) filters.professional_id = this.filterProfessional;
    if (this.filterStatus) filters.status = this.filterStatus;

    this.appointmentsService.getAppointments(filters).subscribe({
      next: (res) => {
        this.appointments = res.items || [];
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
    this.appointmentsService
      .getAppointments({
        page_size: 25,
        last_evaluated_key: JSON.stringify(this.lastKey),
      })
      .subscribe({
        next: (res) => {
          this.appointments = [...this.appointments, ...(res.items || [])];
          this.lastKey = res.last_evaluated_key;
          this.loading = false;
          this.cdr.markForCheck();
        },
      });
  }

  updateStatus(appt: Appointment, status: string): void {
    this.appointmentsService
      .updateAppointment(appt.appointment_id, { status: status as any })
      .subscribe({
        next: () => {
          appt.status = status as any;
          this.cdr.markForCheck();
        },
      });
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      scheduled: 'Agendado',
      completed: 'Concluído',
      cancelled: 'Cancelado',
      no_show: 'Não compareceu',
    };
    return labels[status] || status;
  }
}
