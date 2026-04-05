import { Component, inject, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { AttendanceService, OpenAttendance } from '../../services/attendance';
import { ConversationsService } from '../../services/conversations';
import { ClientsService } from '../../services/clients';
import { AuthService } from '../../services/auth';
import { ConversationMessage } from '../../models';
import { ClientAppointments } from '../client-appointments/client-appointments';

@Component({
  selector: 'app-whatsapp-panel',
  standalone: true,
  imports: [CommonModule, FormsModule, MatProgressSpinnerModule, MatIconModule, ClientAppointments],
  templateUrl: './whatsapp-panel.html',
  styleUrl: './whatsapp-panel.scss',
})
export class WhatsappPanel implements OnInit, OnDestroy {
  private attendanceService = inject(AttendanceService);
  private conversationsService = inject(ConversationsService);
  private clientsService = inject(ClientsService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  openAttendances: OpenAttendance[] = [];
  selectedAttendance: OpenAttendance | null = null;
  messages: ConversationMessage[] = [];
  newMessage = '';
  loading = false;
  loadingMessages = false;
  sending = false;
  private refreshInterval: any;

  ngOnInit(): void {
    this.loadOpenAttendances();
    this.refreshInterval = setInterval(() => this.loadOpenAttendances(), 30000);
  }

  ngOnDestroy(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  loadOpenAttendances(): void {
    this.loading = true;
    this.cdr.markForCheck();
    this.attendanceService.getOpenAttendances().subscribe({
      next: (res) => {
        this.openAttendances = res.items || [];
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  selectAttendance(attendance: OpenAttendance): void {
    this.selectedAttendance = attendance;
    this.cdr.markForCheck();
    this.loadMessages(attendance.phone_number);
  }

  loadMessages(phoneNumber: string): void {
    this.loadingMessages = true;
    this.cdr.markForCheck();
    this.conversationsService.getConversations(phoneNumber, { limit: 100 }).subscribe({
      next: (res) => {
        this.messages = (res.items || []).sort((a, b) => a.timestamp - b.timestamp);
        this.loadingMessages = false;
        this.cdr.markForCheck();
        setTimeout(() => this.scrollToBottom(), 100);
      },
      error: () => {
        this.loadingMessages = false;
        this.cdr.markForCheck();
      },
    });
  }

  sendMessage(): void {
    if (!this.newMessage.trim() || !this.selectedAttendance) return;

    this.sending = true;
    this.cdr.markForCheck();
    this.attendanceService
      .sendHumanMessage(this.selectedAttendance.phone_number, this.newMessage.trim())
      .subscribe({
        next: () => {
          this.messages.push({
            phone_number: this.selectedAttendance!.phone_number,
            timestamp: Date.now(),
            sender: 'human',
            content: this.newMessage.trim(),
            sender_email: this.authService.userInfo()?.email,
            created_at: new Date().toISOString(),
          });
          this.newMessage = '';
          this.sending = false;
          this.cdr.markForCheck();
          setTimeout(() => this.scrollToBottom(), 100);
        },
        error: () => {
          this.sending = false;
          this.cdr.markForCheck();
        },
      });
  }

  closeAttendance(): void {
    if (!this.selectedAttendance) return;

    if (confirm('Deseja encerrar este atendimento e arquivar o chat?')) {
      this.attendanceService.closeAttendance(this.selectedAttendance.phone_number).subscribe({
        next: () => {
          this.openAttendances = this.openAttendances.filter(
            (a) => a.phone_number !== this.selectedAttendance!.phone_number,
          );
          this.selectedAttendance = null;
          this.messages = [];
          this.cdr.markForCheck();
        },
      });
    }
  }

  toggleAi(): void {
    if (!this.selectedAttendance) return;
    const newValue = !this.selectedAttendance.ai_enabled;

    this.clientsService
      .updateClient(this.selectedAttendance.phone_number, { ai_enabled: newValue })
      .subscribe({
        next: () => {
          this.selectedAttendance!.ai_enabled = newValue;
          const item = this.openAttendances.find(
            (a) => a.phone_number === this.selectedAttendance!.phone_number,
          );
          if (item) item.ai_enabled = newValue;
          this.cdr.markForCheck();
        },
      });
  }

  getSenderLabel(msg: ConversationMessage): string {
    if (msg.sender === 'human' && msg.sender_email) {
      const currentEmail = this.authService.userInfo()?.email;
      return msg.sender_email === currentEmail
        ? `Você (${msg.sender_email})`
        : `Atendimento Humano (${msg.sender_email})`;
    }
    const labels: Record<string, string> = { user: 'Cliente', ai: 'IA', human: 'Atendimento Humano', system: 'Sistema' };
    return labels[msg.sender] || msg.sender;
  }

  getTimeSince(timestamp: number): string {
    const now = Date.now();
    const diff = now - timestamp * 1000;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);

    if (minutes < 1) return 'agora';
    if (minutes < 60) return `${minutes}min`;
    if (hours < 24) return `${hours}h`;
    return `${Math.floor(hours / 24)}d`;
  }

  private scrollToBottom(): void {
    const container = document.querySelector('.messages-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}
