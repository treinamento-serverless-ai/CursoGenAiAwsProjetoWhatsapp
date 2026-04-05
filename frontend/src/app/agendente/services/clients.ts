import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.localhost';
import { Client, PaginatedResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class ClientsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/clients`;

  getClients(filters?: {
    ai_enabled?: number;
    is_banned?: number;
    page_size?: number;
    last_evaluated_key?: string;
  }): Observable<PaginatedResponse<Client>> {
    let params = new HttpParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params = params.set(key, String(value));
      });
    }
    return this.http.get<PaginatedResponse<Client>>(this.apiUrl, { params });
  }

  getClient(phoneNumber: string): Observable<Client> {
    return this.http.get<Client>(this.apiUrl, { params: { phone_number: phoneNumber } });
  }

  updateClient(phoneNumber: string, data: Partial<Client>): Observable<any> {
    return this.http.put(this.apiUrl, data, { params: { phone_number: phoneNumber } });
  }
}
