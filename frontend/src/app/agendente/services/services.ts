import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.localhost';
import { Service, PaginatedResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class ServicesService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/services`;

  getServices(filters?: {
    category?: string;
    is_active?: number;
    page_size?: number;
    last_evaluated_key?: string;
  }): Observable<PaginatedResponse<Service>> {
    let params = new HttpParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params = params.set(key, String(value));
      });
    }
    return this.http.get<PaginatedResponse<Service>>(this.apiUrl, { params });
  }

  getService(id: string): Observable<Service> {
    return this.http.get<Service>(this.apiUrl, { params: { id } });
  }

  createService(service: Partial<Service>): Observable<any> {
    return this.http.post(this.apiUrl, service);
  }

  updateService(id: string, data: Partial<Service>): Observable<any> {
    return this.http.put(this.apiUrl, data, { params: { id } });
  }

  deleteService(id: string): Observable<any> {
    return this.http.delete(this.apiUrl, { params: { id } });
  }
}
