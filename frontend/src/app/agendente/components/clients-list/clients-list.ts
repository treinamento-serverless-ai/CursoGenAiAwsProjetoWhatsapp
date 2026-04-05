import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ClientsService } from '../../services/clients';
import { Client } from '../../models';

@Component({
  selector: 'app-clients-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatProgressSpinnerModule],
  templateUrl: './clients-list.html',
  styleUrl: './clients-list.scss',
})
export class ClientsList implements OnInit {
  private clientsService = inject(ClientsService);
  private cdr = inject(ChangeDetectorRef);

  clients: Client[] = [];
  filteredClients: Client[] = [];
  loading = false;
  lastKey: any = null;
  filterAiEnabled = '';
  filterBanned = '';
  searchName = '';
  searchPhone = '';
  searchEmail = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.cdr.markForCheck();
    
    const filters: any = { page_size: 25 };
    if (this.filterAiEnabled !== '') filters.ai_enabled = parseInt(this.filterAiEnabled);
    if (this.filterBanned !== '') filters.is_banned = parseInt(this.filterBanned);

    this.clientsService.getClients(filters).subscribe({
      next: (res) => {
        this.clients = res.items || [];
        this.lastKey = res.last_evaluated_key;
        this.applySearch();
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  applySearch(): void {
    this.filteredClients = this.clients.filter((c) => {
      const matchName = !this.searchName || (c.name || '').toLowerCase().includes(this.searchName.toLowerCase());
      const matchPhone = !this.searchPhone || c.phone_number.includes(this.searchPhone);
      const matchEmail = !this.searchEmail || (c.email || '').toLowerCase().includes(this.searchEmail.toLowerCase());
      return matchName && matchPhone && matchEmail;
    });
    this.cdr.markForCheck();
  }

  loadMore(): void {
    if (!this.lastKey) return;
    this.loading = true;
    this.cdr.markForCheck();
    
    this.clientsService
      .getClients({
        page_size: 25,
        last_evaluated_key: JSON.stringify(this.lastKey),
      })
      .subscribe({
        next: (res) => {
          this.clients = [...this.clients, ...(res.items || [])];
          this.lastKey = res.last_evaluated_key;
          this.applySearch();
          this.loading = false;
          this.cdr.markForCheck();
        },
      });
  }

  toggleAi(client: Client): void {
    this.clientsService
      .updateClient(client.phone_number, {
        ai_enabled: !client.ai_enabled,
      })
      .subscribe(() => {
        client.ai_enabled = !client.ai_enabled;
        this.cdr.markForCheck();
      });
  }
}
