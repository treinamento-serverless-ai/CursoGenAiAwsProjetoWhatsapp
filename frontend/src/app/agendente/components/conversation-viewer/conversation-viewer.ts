import { Component, Input, inject, OnInit, OnChanges, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConversationsService } from '../../services/conversations';
import { ConversationMessage } from '../../models';

@Component({
  selector: 'app-conversation-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './conversation-viewer.html',
  styleUrl: './conversation-viewer.scss',
})
export class ConversationViewer implements OnInit, OnChanges {
  @Input() phoneNumber = '';

  private conversationsService = inject(ConversationsService);
  private cdr = inject(ChangeDetectorRef);

  messages: ConversationMessage[] = [];
  loading = false;
  lastKey: any = null;

  ngOnInit(): void {
    if (this.phoneNumber) this.load();
  }

  ngOnChanges(): void {
    if (this.phoneNumber) {
      this.messages = [];
      this.load();
    }
  }

  load(): void {
    this.loading = true;
    this.cdr.markForCheck();
    
    this.conversationsService.getConversations(this.phoneNumber, { limit: 50 }).subscribe({
      next: (res) => {
        this.messages = res.items || [];
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
    
    this.conversationsService
      .getConversations(this.phoneNumber, {
        limit: 50,
        last_evaluated_key: JSON.stringify(this.lastKey),
      })
      .subscribe({
        next: (res) => {
          this.messages = [...this.messages, ...(res.items || [])];
          this.lastKey = res.last_evaluated_key;
          this.loading = false;
          this.cdr.markForCheck();
        },
      });
  }

  getSenderLabel(sender: string): string {
    const labels: Record<string, string> = {
      user: '\u{1F464} Cliente',
      ai: '\u{1F916} IA',
      human: '\u{1F468}\u200D\u{1F4BC} Atendente',
      system: '\u2699\uFE0F Sistema',
      auto: '\u{1F4E9} Resposta Autom\u00E1tica',
    };
    return labels[sender] || sender;
  }
}
