// Appointment
export interface Appointment {
  appointment_id: string;
  appointment_date: string;
  client_name: string;
  client_phone: string;
  professional_id: string;
  professional_name: string;
  service_id: string;
  service_name: string;
  status: 'CONFIRMED' | 'PENDING' | 'CANCELLED' | 'COMPLETED';
  created_at?: string;
  updated_at?: string;
}

// Professional
export interface Professional {
  professional_id: string;
  name: string;
  specialty?: string;
  career_start_date?: string;
  social_media_link?: string;
  working_days: string[];
  working_hours: { start: string; end: string };
  services: ProfessionalService[];
  scheduling_policy: SchedulingPolicy;
  is_active: boolean;
}

export interface ProfessionalService {
  service_id: string;
  service_name: string;
  duration_hours: number;
  price: number;
}

export interface SchedulingPolicy {
  type: 'FLEXIBLE_MINUTES' | 'FIXED_SLOTS';
  allowed_start_minutes: number[];
  slot_window_hours: number;
}

// Service
export interface Service {
  service_id: string;
  name: string;
  description?: string;
  category?: string;
  is_active: boolean;
}

// Client
export interface Client {
  phone_number: string;
  name?: string;
  email?: string;
  is_banned: boolean;
  ai_enabled: boolean;
  session_id: string;
  last_message_at: number;
  created_at?: string;
}

// Conversation
export interface ConversationMessage {
  phone_number: string;
  timestamp: number;
  sender: 'user' | 'ai' | 'human' | 'system';
  content: string;
  message_id?: string;
  sender_email?: string;
  created_at: string;
}

// Config
export interface AppConfig {
  business_hours_start: string;
  business_hours_end: string;
  business_hours_timezone: string;
  max_booking_days: string;
  inactivity_threshold_seconds: string;
  audio_processing_grace_period: string;
  closed_message: string;
  banned_message: string;
  transcribe_enabled: string;
  transcribe_disabled_message: string;
  audio_min_size_kb: string;
  audio_max_size_kb: string;
  ai_error_message: string;
  save_messages_after_hours: string;
  reply_with_context: string;
  reply_context_use_last: string;
  ai_global_enabled?: boolean;
}

export interface ConfigVersion {
  version: number;
  description: string;
}

export interface ConfigResponse {
  current_config: AppConfig;
  available_versions: ConfigVersion[];
  requested_version: string;
}

export interface ConfigUpdateRequest {
  description?: string;
  config: AppConfig;
}

// API Response
export interface PaginatedResponse<T> {
  items: T[];
  page_size?: number;
  limit?: number;
  last_evaluated_key?: any;
}
