import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { ProfessionalsService } from '../../services/professionals';
import { Professional } from '../../models';

@Component({
  selector: 'app-professionals-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatProgressSpinnerModule, MatIconModule],
  templateUrl: './professionals-list.html',
  styleUrl: './professionals-list.scss',
})
export class ProfessionalsList implements OnInit {
  private professionalsService = inject(ProfessionalsService);
  private cdr = inject(ChangeDetectorRef);

  professionals: Professional[] = [];
  loading = false;
  lastKey: any = null;
  filterName = '';
  filterActive = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.cdr.markForCheck();
    
    const filters: any = { page_size: 25 };
    if (this.filterName) filters.name = this.filterName;
    if (this.filterActive !== '') filters.is_active = parseInt(this.filterActive);
    
    this.professionalsService.getProfessionals(filters).subscribe({
      next: (res) => {
        this.professionals = res.items || [];
        this.lastKey = res.last_evaluated_key;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  loadMore(): void {
    if (!this.lastKey) return;
    this.loading = true;
    this.cdr.markForCheck();
    
    this.professionalsService
      .getProfessionals({
        page_size: 25,
        last_evaluated_key: JSON.stringify(this.lastKey),
      })
      .subscribe({
        next: (res) => {
          this.professionals = [...this.professionals, ...(res.items || [])];
          this.lastKey = res.last_evaluated_key;
          this.loading = false;
          this.cdr.markForCheck();
        },
      });
  }

  toggleActive(prof: Professional): void {
    this.professionalsService
      .updateProfessional(prof.professional_id, {
        is_active: !prof.is_active,
      })
      .subscribe(() => {
        prof.is_active = !prof.is_active;
        this.cdr.markForCheck();
      });
  }

  translateDays(days: string[]): string {
    const translations: Record<string, string> = {
      monday: 'segunda',
      tuesday: 'terça',
      wednesday: 'quarta',
      thursday: 'quinta',
      friday: 'sexta',
      saturday: 'sábado',
      sunday: 'domingo',
    };
    return days.map(d => translations[d.toLowerCase()] || d).join(', ');
  }
}
