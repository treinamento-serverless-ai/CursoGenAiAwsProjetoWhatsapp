import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.localhost';
import { ConversationMessage, PaginatedResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class ConversationsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/conversations`;

  getConversations(
    phoneNumber: string,
    filters?: {
      limit?: number;
      last_evaluated_key?: string;
    },
  ): Observable<PaginatedResponse<ConversationMessage>> {
    let params = new HttpParams().set('phone_number', phoneNumber);
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params = params.set(key, String(value));
      });
    }
    return this.http.get<PaginatedResponse<ConversationMessage>>(this.apiUrl, { params });
  }
}
