![Project Logo](./images/hotel.png "hotel")

## Overview

Otello is a conversational AI-powered property management system tailored for small-scale hospitality providers such as homestays, boutique hotels, hostels, and Airbnb hosts.

These independent hosts often manage between 1–20 rooms and struggle with clunky spreadsheets, manual WhatsApp chats, and fragmented tools. Enterprise-grade Property Management Systems (PMS) are expensive, overly complex, and not mobile/chat-first. Otello changes that by enabling complete property management through WhatsApp, powered entirely by AI, with no need for dashboards, apps, or technical know-how.


## How it works

### 1. **Chatbot Integration via Twilio + Ngrok**
- We built a chatbot using Twilio's WhatsApp API.
- The bot is served via a FastAPI backend on a local server.
- Ngrok exposes the local server to a public URL, enabling webhook communication from Twilio to our local backend.

### 2. **AI-Driven Query Understanding**
- Incoming messages from hosts or guests are parsed using LangChain + OpenAI GPT-4o.
- We built a RAG-based pipeline to convert natural language into structured MongoDB queries or updates. This automatically inserts bookings, answer availability questions, or update room statuses — all via AI.

### 3. **Fallback to Human Dashboard**
- If the AI can't confidently resolve a query, it escalates to a human host dashboard.
- The host can view the pending query and respond. Otello then sends the response back to WhatsApp automatically.

### 4. **OTA-Ready**
- We’ve architected Otello with extensible API endpoints to connect with Online Travel Agencies (OTAs) like Airbnb, Booking.com, etc., making it a cross-platform assistant.