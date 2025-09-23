{% extends "base.html" %}

{% block content %}
<div class="container">
  <h1>🚀 WHITE-LABEL CLUB PLATFORM – MASTER PROJECT PROMPT</h1>

  <h2>Objective</h2>
  <p>Build a multi-tenant, API-powered white-label web service where paying users can launch their own branded "club" — complete with a chat room, booking system, Stripe Express payments, and more.</p>

  <h2>💡 Core Product Concept</h2>
  <ul>
    <li>Create their own private community ("club")</li>
    <li>Launch it under your domain or a custom domain</li>
    <li>Access their own branded dashboard</li>
    <li>Rent access to your core API</li>
    <li>Collect payments, bookings, and donations through Stripe Express</li>
    <li>Use AI Assistants and Chat to manage their communities</li>
  </ul>

  <h2>🧩 CORE FEATURES TO BUILD</h2>
  <h3>🧭 Onboarding Wizard</h3>
  <ul>
    <li>Stripe Express Connect integration (merchant-of-record)</li>
    <li>Enter OpenAI API key for AI Assistant</li>
    <li>Club branding: name, logo, color, description</li>
    <li>Booking setup: service types, time slots, prices</li>
    <li>Member access tiers (Free / Premium / VIP)</li>
  </ul>

  <h3>🌐 Domain Options</h3>
  <ul>
    <li>Support subdomains (clubname.yourplatform.com)</li>
    <li>Optional custom domain via DNS (with instructions or verification)</li>
    <li>Auto SSL via Cloudflare or Let’s Encrypt</li>
  </ul>

  <h3>👥 Club Features</h3>
  <ul>
    <li><strong>Booking System:</strong> Calendar view, rescheduling, payments</li>
    <li><strong>Built-in Chat Room:</strong> Real-time, moderated, optional tiers</li>
    <li><strong>AI Assistant:</strong> Connects to owner's OpenAI key</li>
    <li><strong>Donation System:</strong> Stripe Express with donor display</li>
  </ul>

  <h3>📂 Media Manager</h3>
  <ul>
    <li>Upload videos, images, documents to Spaces/S3</li>
    <li>Control visibility by membership tier</li>
    <li>Members cannot upload</li>
  </ul>

  <h3>📊 Admin Dashboard (Owner View)</h3>
  <ul>
    <li>Booking history, chat stats, donations</li>
    <li>Manage members & tiers</li>
    <li>Edit content, branding, features</li>
    <li>Toggle features (chat, bookings, AI, donations)</li>
    <li>See OpenAI token usage (optional)</li>
  </ul>

  <h3>🧠 AI Tools (Optional Tiered Upgrade)</h3>
  <ul>
    <li>Club-specific AI chat with context</li>
    <li>Q&A bot trained on uploaded PDFs or FAQs</li>
    <li>AI Recommendations: services, content, upsells</li>
  </ul>

  <h3>📧 Messaging & Notifications</h3>
  <ul>
    <li>In-app notifications (chat mentions, new booking)</li>
    <li>Announcements from admins</li>
    <li>Optional email integration (Brevo, SendGrid)</li>
  </ul>

  <h3>💬 Public Member Pages (Optional)</h3>
  <ul>
    <li>Profile pages with badges, booking history</li>
    <li>Display name, joined date, role/tier</li>
  </ul>

  <h3>🔐 Platform Admin View (Super Admin Panel)</h3>
  <ul>
    <li>Manage clubs (view/delete/suspend)</li>
    <li>Manage Stripe accounts (via Connect)</li>
    <li>Monitor usage (API calls, AI usage)</li>
    <li>View domains, support requests</li>
    <li>Generate invoices, reports</li>
  </ul>

  <h2>💰 Pricing & Monetization Model</h2>
  <ul>
    <li>Base plan: $67/month (1 club)</li>
    <li>Add-ons: custom domain ($5/mo), extra storage, more clubs</li>
    <li>Optional platform fee from bookings/donations</li>
  </ul>

  <h2>📦 Tech Stack Suggestions</h2>
  <ul>
    <li><strong>Backend:</strong> FastAPI, PostgreSQL, Redis</li>
    <li><strong>Frontend:</strong> Jinja (you), or React/Tailwind</li>
    <li><strong>Real-time:</strong> WebSockets or Socket.IO</li>
    <li><strong>Auth:</strong> JWT, OAuth (Stripe, OpenAI)</li>
    <li><strong>Hosting:</strong> DigitalOcean, Vercel, Docker</li>
    <li><strong>Storage:</strong> DO Spaces / AWS S3</li>
    <li><strong>Payments:</strong> Stripe Express Connect</li>
    <li><strong>AI:</strong> OpenAI API (GPT-4 or 3.5)</li>
  </ul>

  <h2>🛠 Developer Tasks Breakdown</h2>
  <ul>
    <li>Build onboarding wizard with Stripe & OpenAI</li>
    <li>Implement white-labeled multi-tenant system</li>
    <li>Build per-club booking + chat modules</li>
    <li>Enable domain & branding customizations</li>
    <li>Connect APIs (Stripe, OpenAI, optional CDN)</li>
    <li>Launch secure admin interface</li>
    <li>Create documentation for users</li>
  </ul>

  <p>This prompt provides everything a senior full-stack dev or agency needs to start the MVP. Expand with gamification, referrals, or mobile apps later.</p>
</div>
{% endblock %}

DATABASE_URL=postgresql+asyncpg://adminuser:Securepass@localhost/white_label_club

               List of relations
 Schema |       Name       | Type  |   Owner   
--------+------------------+-------+-----------
 public | alembic_version  | table | adminuser
 public | club_members     | table | adminuser
 public | club_roles       | table | adminuser
 public | clubs            | table | adminuser
 public | membership_tiers | table | adminuser
 public | platform_users   | table | adminuser
(6 rows)
