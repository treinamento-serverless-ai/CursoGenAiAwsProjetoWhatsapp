import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.localhost';
import { AppConfig, ConfigResponse, ConfigUpdateRequest } from '../models';

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/config`;

  getConfig(version?: number): Observable<ConfigResponse> {
    const url = version ? `${this.apiUrl}?version=${version}` : this.apiUrl;
    return this.http.get<ConfigResponse>(url);
  }

  updateConfig(data: ConfigUpdateRequest): Observable<any> {
    return this.http.put(this.apiUrl, data);
  }

  deleteVersion(version: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}?version=${version}`);
  }
}
