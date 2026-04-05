import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.localhost';
import { Appointment, PaginatedResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class AppointmentsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/appointments`;

  getAppointments(filters?: {
    professional_id?: string;
    client_phone?: string;
    status?: string;
    page_size?: number;
    last_evaluated_key?: string;
  }): Observable<PaginatedResponse<Appointment>> {
    let params = new HttpParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params = params.set(key, String(value));
      });
    }
    return this.http.get<PaginatedResponse<Appointment>>(this.apiUrl, { params });
  }

  getAppointment(id: string): Observable<Appointment> {
    return this.http.get<Appointment>(this.apiUrl, { params: { id } });
  }

  createAppointment(appointment: Partial<Appointment>): Observable<any> {
    return this.http.post(this.apiUrl, appointment);
  }

  updateAppointment(id: string, data: Partial<Appointment>): Observable<any> {
    return this.http.put(this.apiUrl, data, { params: { id } });
  }

  cancelAppointment(id: string): Observable<any> {
    return this.http.delete(this.apiUrl, { params: { id } });
  }
}
