# Product Overview

## Product Purpose

Agendente is a didactic open-source project that demonstrates how to build a WhatsApp-integrated virtual scheduling assistant using AWS serverless services and Generative AI. The core value proposition is teaching AWS serverless architecture through a practical, functional example.

The assistant converses with customers in natural language (text and audio) via WhatsApp, interprets intent using Amazon Bedrock (LLM), and executes real actions — checking availability, creating and canceling appointments — autonomously without predefined menus. The example scenario is a barbershop, but the architecture is white-label and adaptable to any appointment-based business (pet shop, clinic, studio, etc.).

This project accompanies the Udemy course "Inteligência Artificial Sem Servidor na AWS" (Serverless AI on AWS), taught in Brazilian Portuguese.

## Target Users

There are three distinct user groups:

- **Course students and developers learning AWS**: The primary audience. They use this project to study serverless services (Lambda, Step Functions, Bedrock, DynamoDB, Cognito, etc.) through a real-world GenAI example. The architecture intentionally uses more services than strictly necessary to maximize learning exposure.
- **Business owners / administrators**: In the application scenario, these users access the Angular dashboard to manage appointments, professionals, services, clients, and system configuration (business hours, AI agent on/off).
- **End customers (WhatsApp users)**: They interact with the chatbot via WhatsApp to schedule, check, or cancel appointments using natural language.

## Key Features

### WhatsApp Chatbot (AI-powered)
- Natural language conversation via text and audio messages
- Audio transcription using Amazon Transcribe
- Intent interpretation and action execution via Amazon Bedrock Agent with Action Groups
- Message batching with inactivity detection (Step Functions orchestration)
- Business hours enforcement with automatic closed-hours messaging
- Session management with 30-minute timeout

### Admin Dashboard (Angular)
- Calendar view of appointments
- CRUD for professionals, services, clients, and appointments
- WhatsApp conversation viewer and attendance panel
- System configuration panel (business hours, AI mode toggle, transcription settings)
- OAuth2 authentication via Amazon Cognito (admin and regular user groups)

### Infrastructure
- Full Infrastructure as Code with Terraform (single `terraform apply` deploys everything)
- Automated frontend build and deploy to S3 during `terraform apply`
- CloudWatch dashboard and alarms for operational monitoring
- mTLS support for WhatsApp webhook security
- Custom domain support with Route 53 and CloudFront
- DLQ processing and security monitoring via scheduled tasks

## Business Objectives

- **Educational**: Teach the maximum number of AWS serverless services through a cohesive, real-world project
- **Low operational cost**: Use pay-per-use and on-demand services exclusively, suitable for learning environments
- **White-label adaptability**: Architecture can be reused for any appointment-based business by changing configuration
- **Vibe Coding demonstration**: Show how AI-assisted development (vibe coding) can produce a functional full-stack application, while being transparent about its limitations (not production-ready, potential security flaws)
- **Open source**: MIT licensed, freely usable as a starting point for derivative projects
