import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { switchMap, tap, catchError } from 'rxjs/operators';
import { EMPTY } from 'rxjs';
import { ConfigService } from '../../services/config';
import { AppConfig, ConfigVersion } from '../../models';

@Component({
  selector: 'app-config-panel',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatSlideToggleModule,
    MatCardModule,
    MatSelectModule,
    MatIconModule,
  ],
  templateUrl: './config-panel.html',
  styleUrl: './config-panel.scss',
})
export class ConfigPanel implements OnInit {
  private configService = inject(ConfigService);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);

  config: Partial<AppConfig> = {};
  availableVersions: ConfigVersion[] = [];
  selectedVersion: string = 'latest';
  currentDescription: string = '';
  description: string = '';
  saving = false;
  loading = false;
  latestVersion: number = 0;

  ngOnInit(): void {
    this.load();
  }

  load(version?: number): void {
    this.loading = true;
    this.cdr.markForCheck();

    this.configService.getConfig(version).subscribe({
      next: (response) => this.applyConfigState(response),
      error: (err) => {
        this.loading = false;
        this.cdr.markForCheck();
        this.snackBar.open('Erro ao carregar configurações', 'OK', { duration: 3000 });
      },
    });
  }

  private applyConfigState(response: any): void {
    this.config = response.current_config;
    this.availableVersions = response.available_versions;
    this.selectedVersion = response.requested_version;
    this.latestVersion = response.available_versions[0]?.version || 0;
    this.currentDescription = response.available_versions[0]?.description || '';
    
    this.loading = false;
    this.cdr.markForCheck();
  }

  onVersionChange(): void {
    if (this.selectedVersion === 'latest') {
      setTimeout(() => this.load(), 0);
    } else {
      this.load(parseInt(this.selectedVersion));
    }
  }

  isViewingLatest(): boolean {
    return this.selectedVersion === 'latest';
  }

  updateCurrent(): void {
    this.saving = true;
    this.cdr.markForCheck();
    
    const payload = {
      description: this.description || 'Atualização da configuração atual',
      create_new_version: false,
      config: this.config as AppConfig
    };

    this.configService.updateConfig(payload).pipe(
      tap(() => {
        this.saving = false;
        this.loading = true;
        this.snackBar.open('Configuração atual atualizada', 'OK', { duration: 3000 });
        this.cdr.markForCheck();
      }),
      switchMap(() => this.configService.getConfig()),
      catchError((err) => {
        this.saving = false;
        this.loading = false;
        this.cdr.markForCheck();
        this.snackBar.open('Erro ao processar requisição', 'OK', { duration: 3000 });
        return EMPTY;
      })
    ).subscribe({
      next: (response) => this.applyConfigState(response)
    });
  }

  createSnapshot(): void {
    if (!this.description.trim()) {
      this.snackBar.open('Descrição é obrigatória para criar snapshot', 'OK', { duration: 3000 });
      return;
    }

    this.saving = true;
    this.cdr.markForCheck();
    
    const payload = {
      description: this.description,
      create_new_version: true,
      config: this.config as AppConfig
    };

    this.configService.updateConfig(payload).pipe(
      tap((response) => {
        this.saving = false;
        this.loading = true;
        this.snackBar.open(`Snapshot v${response.version} criado com sucesso`, 'OK', { duration: 3000 });
        this.cdr.markForCheck();
      }),
      switchMap(() => this.configService.getConfig()),
      catchError((err) => {
        this.saving = false;
        this.loading = false;
        this.cdr.markForCheck();
        this.snackBar.open('Erro ao processar requisição', 'OK', { duration: 3000 });
        return EMPTY;
      })
    ).subscribe({
      next: (response) => this.applyConfigState(response)
    });
  }

  deleteVersion(version: number): void {
    if (confirm(`Tem certeza que deseja deletar a versao ${version}?`)) {
      this.configService.deleteVersion(version).pipe(
        tap(() => {
          this.loading = true;
          this.snackBar.open(`Versao ${version} deletada`, 'OK', { duration: 3000 });
          this.cdr.markForCheck();
        }),
        switchMap(() => this.configService.getConfig()),
        catchError((err) => {
          this.loading = false;
          this.cdr.markForCheck();
          this.snackBar.open('Erro ao deletar versao', 'OK', { duration: 3000 });
          return EMPTY;
        })
      ).subscribe({
        next: (response) => this.applyConfigState(response)
      });
    }
  }
  isTrue(value: any): boolean {
    return value === 'true' || value === true;
  }

  setBoolean(field: keyof AppConfig, value: boolean): void {
    (this.config as any)[field] = value.toString();
  }
}
