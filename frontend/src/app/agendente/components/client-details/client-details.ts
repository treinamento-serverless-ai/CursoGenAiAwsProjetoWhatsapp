import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ClientsService } from '../../services/clients';
import { Client } from '../../models';
import { ConversationViewer } from '../conversation-viewer/conversation-viewer';

@Component({
  selector: 'app-client-details',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ConversationViewer, MatProgressSpinnerModule],
  templateUrl: './client-details.html',
  styleUrl: './client-details.scss',
})
export class ClientDetails implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private clientsService = inject(ClientsService);
  private cdr = inject(ChangeDetectorRef);

  client: Client | null = null;
  loading = false;
  editing = false;
  editForm = { name: '', email: '' };

  ngOnInit(): void {
    const phone = this.route.snapshot.paramMap.get('phone');
    if (phone) this.loadClient(phone);
    else this.router.navigate(['/clients']);
  }

  loadClient(phone: string): void {
    this.loading = true;
    this.cdr.markForCheck();
    
    this.clientsService.getClient(phone).subscribe({
      next: (client) => {
        this.client = client;
        this.editForm = { name: client.name || '', email: client.email || '' };
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
        this.router.navigate(['/clients']);
      },
    });
  }

  startEdit(): void {
    this.editing = true;
    this.cdr.markForCheck();
  }

  cancelEdit(): void {
    this.editing = false;
    if (this.client) {
      this.editForm = { name: this.client.name || '', email: this.client.email || '' };
    }
    this.cdr.markForCheck();
  }

  saveEdit(): void {
    if (!this.client) return;
    this.clientsService
      .updateClient(this.client.phone_number, this.editForm)
      .subscribe(() => {
        if (this.client) {
          this.client.name = this.editForm.name;
          this.client.email = this.editForm.email;
        }
        this.editing = false;
        this.cdr.markForCheck();
      });
  }

  toggleAi(): void {
    if (!this.client) return;
    this.clientsService
      .updateClient(this.client.phone_number, {
        ai_enabled: !this.client.ai_enabled,
      })
      .subscribe(() => {
        this.client!.ai_enabled = !this.client!.ai_enabled;
        this.cdr.markForCheck();
      });
  }

  toggleBanned(): void {
    if (!this.client) return;
    this.clientsService
      .updateClient(this.client.phone_number, {
        is_banned: !this.client.is_banned,
      })
      .subscribe(() => {
        this.client!.is_banned = !this.client!.is_banned;
        this.cdr.markForCheck();
      });
  }
}
