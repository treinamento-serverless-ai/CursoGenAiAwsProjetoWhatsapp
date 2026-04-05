import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.localhost';
import { PaginatedResponse } from '../models';

export interface OpenAttendance {
  phone_number: string;
  name?: string;
  last_message?: string;
  last_message_at: number;
  unread_count?: number;
  session_id: string;
  ai_enabled: boolean;
}

@Injectable({ providedIn: 'root' })
export class AttendanceService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/attendance`;

  /**
   * Lista atendimentos em aberto (clientes com ai_enabled=false ou aguardando resposta humana)
   */
  getOpenAttendances(filters?: {
    page_size?: number;
    last_evaluated_key?: string;
  }): Observable<PaginatedResponse<OpenAttendance>> {
    let params = new HttpParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params = params.set(key, String(value));
      });
    }
    return this.http.get<PaginatedResponse<OpenAttendance>>(this.apiUrl, { params });
  }

  /**
   * Envia mensagem como atendente humano
   */
  sendHumanMessage(phoneNumber: string, content: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/message`, {
      phone_number: phoneNumber,
      content: content,
    });
  }

  /**
   * Finaliza atendimento e arquiva conversa
   */
  closeAttendance(phoneNumber: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/close`, {
      phone_number: phoneNumber,
    });
  }
}
