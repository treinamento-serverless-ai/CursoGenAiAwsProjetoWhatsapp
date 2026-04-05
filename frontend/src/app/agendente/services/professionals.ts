import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.localhost';
import { Professional, PaginatedResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class ProfessionalsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/professionals`;

  getProfessionals(filters?: {
    is_active?: number;
    page_size?: number;
    last_evaluated_key?: string;
  }): Observable<PaginatedResponse<Professional>> {
    let params = new HttpParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params = params.set(key, String(value));
      });
    }
    return this.http.get<PaginatedResponse<Professional>>(this.apiUrl, { params });
  }

  getProfessional(id: string): Observable<Professional> {
    return this.http.get<Professional>(this.apiUrl, { params: { id } });
  }

  createProfessional(professional: Partial<Professional>): Observable<any> {
    return this.http.post(this.apiUrl, professional);
  }

  updateProfessional(id: string, data: Partial<Professional>): Observable<any> {
    return this.http.put(this.apiUrl, data, { params: { id } });
  }

  deleteProfessional(id: string): Observable<any> {
    return this.http.delete(this.apiUrl, { params: { id } });
  }
}
