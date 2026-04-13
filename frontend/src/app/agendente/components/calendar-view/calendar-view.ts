import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AppointmentsService } from '../../services/appointments';
import { ProfessionalsService } from '../../services/professionals';
import { Appointment, Professional } from '../../models';

@Component({
  selector: 'app-calendar-view',
  standalone: true,
  imports: [CommonModule, FormsModule, MatProgressSpinnerModule],
  templateUrl: './calendar-view.html',
  styleUrl: './calendar-view.scss',
})
export class CalendarView implements OnInit {
  private appointmentsService = inject(AppointmentsService);
  private professionalsService = inject(ProfessionalsService);
  private cdr = inject(ChangeDetectorRef);

  appointments: Appointment[] = [];
  professionals: Professional[] = [];
  currentDate = new Date();
  selectedProfessional = '';
  viewMode: 'month' | 'week' = 'month';
  loading = false;

  ngOnInit(): void {
    this.loadProfessionals();
    this.loadAppointments();
  }

  loadProfessionals(): void {
    this.professionalsService.getProfessionals({ is_active: 1 }).subscribe({
      next: (res) => {
        this.professionals = res.items || [];
        this.cdr.markForCheck();
      },
    });
  }

  loadAppointments(): void {
    this.loading = true;
    this.cdr.markForCheck();
    const filters: any = {};
    if (this.selectedProfessional) filters.professional_id = this.selectedProfessional;

    this.appointmentsService.getAppointments(filters).subscribe({
      next: (res) => {
        this.appointments = res.items || [];
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  get calendarDays(): Date[] {
    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - startDate.getDay());

    const days: Date[] = [];
    const current = new Date(startDate);
    while (current <= lastDay || days.length % 7 !== 0) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    return days;
  }

  getAppointmentsForDay(date: Date): Appointment[] {
    const dateStr = date.toISOString().split('T')[0];
    return this.appointments.filter((a) => a.appointment_date?.startsWith(dateStr));
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      scheduled: '#2196f3',
      completed: '#4caf50',
      cancelled: '#f44336',
      no_show: '#ff9800',
    };
    return colors[status] || '#666';
  }

  prevMonth(): void {
    this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1);
  }

  nextMonth(): void {
    this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1);
  }

  isToday(date: Date): boolean {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  }

  isCurrentMonth(date: Date): boolean {
    return date.getMonth() === this.currentDate.getMonth();
  }
}
