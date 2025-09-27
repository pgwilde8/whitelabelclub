# ClubLaunch Database Schema Documentation

## 🗄️ Database Overview: psql -h localhost -U adminuser -d white_label_club
- **Database Name:** `white_label_club`
- **Host:** localhost
- **User:** adminuser
- **Connection String:** `postgresql://adminuser:Securepass@localhost/white_label_club`

## 📋 Complete Table List

### Core Tables
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `clubs` | Club/tenant information and branding | id, name, slug, stripe_account_id |
| `platform_users` | Platform administrators (club owners) | id, username, email, stripe_customer_id |
| `club_members` | End-users who join clubs | id, club_id, email, membership_tier |
| `club_roles` | Role-based access control | id, club_id, user_id, role_name |
| `membership_tiers` | Membership levels (Basic, Premium, VIP) | id, club_id, name, price, features |
| `member_subscriptions` | Member subscription tracking | id, member_id, tier_id, status |
| `platform_subscriptions` | Platform subscription plans | id, user_id, stripe_subscription_id |

### Booking System
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `booking_services` | Bookable services offered by clubs | id, club_id, name, price, duration |
| `booking_slots` | Available time slots for booking | id, service_id, start_time, end_time |
| `bookings` | Actual bookings made by members | id, member_id, service_id, status |

### Chat & Communication
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `chat_channels` | Chat rooms within clubs | id, club_id, name, type |
| `chat_messages` | Messages in chat channels | id, channel_id, sender_id, content |
| `message_reactions` | Emoji reactions to messages | id, message_id, user_id, emoji |
| `member_channel_access` | Channel access permissions | id, member_id, channel_id, access_level |

### Payment & Financial
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `payments` | Payment transactions | id, amount, stripe_payment_intent_id, status |
| `donations` | Donation tracking | id, donor_id, club_id, amount |
| `platform_subscriptions` | Platform subscription billing | id, user_id, stripe_subscription_id |

### Media & Content
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `media_files` | File storage metadata | id, club_id, filename, url, file_type |
| `content_pages` | Custom pages created by clubs | id, club_id, title, content, slug |
| `content_media` | Media associated with content | id, content_id, media_id |

### AI Integration
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `ai_conversations` | AI chat conversations | id, club_id, member_id, context |
| `ai_messages` | Individual AI messages | id, conversation_id, role, content |

### Analytics & Monitoring
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `club_analytics` | Club-specific metrics | id, club_id, date, metrics_json |
| `platform_usage` | Platform-wide usage statistics | id, date, user_count, revenue |

### System & Administration
| Table Name | Description | Key Fields |
|------------|-------------|------------|
| `notifications` | User notifications | id, user_id, type, message, read |
| `audit_logs` | System activity logs | id, user_id, action, resource, timestamp |
| `feature_flags` | Feature toggle management | id, name, enabled, club_id |
| `alembic_version` | Database migration tracking | version_num |

## 🔗 Key Relationships

### Club Hierarchy
```
clubs (1) → (many) club_members
clubs (1) → (many) membership_tiers
clubs (1) → (many) booking_services
clubs (1) → (many) chat_channels
clubs (1) → (many) media_files
```

### User Relationships
```
platform_users (1) → (many) clubs (as owner)
club_members (1) → (1) clubs
club_members (1) → (many) bookings
club_members (1) → (many) chat_messages
```

### Stripe Integration
```
clubs.stripe_account_id → Stripe Connect Account
platform_users.stripe_customer_id → Stripe Customer
payments.stripe_payment_intent_id → Stripe Payment Intent
platform_subscriptions.stripe_subscription_id → Stripe Subscription
```

## 💳 Stripe Data Storage

### Clubs Table
- `stripe_account_id` - Stripe Connect account for club payments
- `stripe_onboarding_complete` - Boolean indicating Stripe setup status
- `subscription_status` - Current platform subscription status
- `subscription_plan` - Platform plan (starter/pro/enterprise)
- `subscription_ends_at` - Subscription expiration date

### Platform Subscriptions Table
- `stripe_subscription_id` - Stripe subscription ID
- `stripe_customer_id` - Stripe customer ID
- `stripe_price_id` - Stripe price ID for billing
- `plan_name` - Human-readable plan name
- `amount` - Subscription amount in cents
- `billing_cycle` - Monthly/yearly billing
- `status` - Subscription status (active, cancelled, etc.)
- `current_period_start/end` - Billing period dates

### Payments Table
- `stripe_payment_intent_id` - Stripe payment intent ID
- `stripe_charge_id` - Stripe charge ID
- `amount` - Payment amount in cents
- `currency` - Payment currency (USD)
- `status` - Payment status (succeeded, failed, pending)

## 🔐 Security Features

### Data Encryption
- `openai_api_key_encrypted` - Encrypted OpenAI API keys using Fernet
- `ENCRYPTION_KEY` - 32-byte base64 encryption key in environment

### Access Control
- Role-based permissions via `club_roles` table
- Channel-specific access via `member_channel_access`
- Club-level feature toggles via `feature_flags`

## 📊 Analytics & Monitoring

### Club Analytics
- Member growth tracking
- Revenue metrics
- Engagement statistics
- Booking analytics

### Platform Usage
- Total active users
- Platform revenue
- Feature usage statistics
- Performance metrics

## 🚀 Migration Management

### Alembic Integration
- Version-controlled schema changes
- Automated migration scripts
- Rollback capabilities
- Environment-specific configurations

### Current Migration
- `0001_initial_migration_with_all_tables.py` - Initial schema creation

## 🔧 Maintenance Commands

### Database Connection
```bash
psql -h localhost -U adminuser -d white_label_club
```

### Club Onboarding Monitoring Queries
```sql
-- 1. View Platform Users (Club Owners)
SELECT id, email, first_name, last_name, created_at, is_active
FROM platform_users 
ORDER BY created_at DESC;

-- Count total platform users
SELECT COUNT(*) as total_platform_users FROM platform_users;

-- 2. View All Clubs
SELECT c.id, c.name, c.slug, c.created_at, 
       c.stripe_onboarding_complete, c.subscription_status, c.subscription_plan
FROM clubs c
ORDER BY c.created_at DESC;

-- See clubs with their owners (through club_roles)
SELECT c.id, c.name, c.slug, c.created_at,
       c.stripe_onboarding_complete, c.subscription_status,
       p.email as owner_email, p.first_name, p.last_name,
       cr.role
FROM clubs c
JOIN club_roles cr ON c.id = cr.club_id
JOIN platform_users p ON cr.user_id = p.id
WHERE cr.role = 'owner'
ORDER BY c.created_at DESC;

-- 3. Club Member Growth
SELECT c.name as club_name, 
       COUNT(cm.id) as member_count,
       c.slug as club_slug
FROM clubs c
LEFT JOIN club_members cm ON c.id = cm.club_id
GROUP BY c.id, c.name, c.slug
ORDER BY member_count DESC;

-- Recent club member signups
SELECT cm.email, cm.display_name, c.name as club_name, cm.created_at, cm.member_tier
FROM club_members cm
JOIN clubs c ON cm.club_id = c.id
ORDER BY cm.created_at DESC
LIMIT 10;

-- 4. Platform Subscriptions
SELECT p.email, ps.plan_name, ps.status, ps.amount, ps.created_at
FROM platform_subscriptions ps
JOIN platform_users p ON ps.user_id = p.id
ORDER BY ps.created_at DESC;

-- 5. Stripe Integration Status
SELECT name, slug, stripe_onboarding_complete, 
       CASE WHEN stripe_account_id IS NOT NULL THEN 'Yes' ELSE 'No' END as has_stripe_account,
       subscription_status, subscription_plan
FROM clubs
ORDER BY created_at DESC;

-- Recent payments
SELECT p.amount, p.status, p.currency, c.name as club_name, p.created_at
FROM payments p
JOIN clubs c ON p.club_id = c.id
ORDER BY p.created_at DESC
LIMIT 10;

-- 6. Platform Health Summary
SELECT 
  (SELECT COUNT(*) FROM platform_users) as total_platform_users,
  (SELECT COUNT(*) FROM clubs) as total_clubs,
  (SELECT COUNT(*) FROM club_members) as total_club_members,
  (SELECT COUNT(*) FROM clubs WHERE stripe_onboarding_complete = true) as clubs_with_stripe,
  (SELECT COUNT(*) FROM club_roles WHERE role = 'owner') as total_club_owners;

-- 7. Recent Activity (Last 7 Days)
SELECT 
  'Platform User' as type, email as name, created_at
FROM platform_users 
WHERE created_at >= NOW() - INTERVAL '7 days'
UNION ALL
SELECT 
  'Club' as type, name, created_at
FROM clubs 
WHERE created_at >= NOW() - INTERVAL '7 days'
UNION ALL
SELECT 
  'Club Member' as type, email, created_at
FROM club_members 
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### Sample Test Data Creation
```sql
-- Create a test platform user (club owner)
INSERT INTO platform_users (id, email, password_hash, first_name, last_name, is_active)
VALUES (
  gen_random_uuid(),
  'testowner@example.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsIAbnCl8', -- "password"
  'Test',
  'Owner',
  true
);

-- Create a test club
INSERT INTO clubs (id, name, slug, description, subscription_status, subscription_plan)
VALUES (
  gen_random_uuid(),
  'Test Fitness Club',
  'test-fitness',
  'A test club for onboarding verification',
  'trial',
  'basic'
);

-- Link the club owner to the club
INSERT INTO club_roles (id, club_id, user_id, role)
SELECT 
  gen_random_uuid(),
  c.id,
  p.id,
  'owner'
FROM clubs c, platform_users p
WHERE c.slug = 'test-fitness' AND p.email = 'testowner@example.com';

-- Create test club members
INSERT INTO club_members (id, club_id, email, display_name, member_tier, status)
SELECT 
  gen_random_uuid(),
  c.id,
  'member1@example.com',
  'Test Member 1',
  'free',
  'active'
FROM clubs c WHERE c.slug = 'test-fitness';

INSERT INTO club_members (id, club_id, email, display_name, member_tier, status)
SELECT 
  gen_random_uuid(),
  c.id,
  'member2@example.com',
  'Test Member 2',
  'premium',
  'active'
FROM clubs c WHERE c.slug = 'test-fitness';
```

### Clear Test Data
```sql
-- Remove all test data (use with caution!)
DELETE FROM club_members WHERE email LIKE '%@example.com';
DELETE FROM club_roles WHERE club_id IN (SELECT id FROM clubs WHERE slug = 'test-fitness');
DELETE FROM clubs WHERE slug = 'test-fitness';
DELETE FROM platform_users WHERE email LIKE '%@example.com';
```

### Migration Commands
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

## 📈 Performance Considerations

### Indexes
- Primary keys on all tables (UUID)
- Unique constraints on slugs and emails
- Foreign key indexes for relationships

### Optimization
- JSON fields for flexible feature storage
- Timestamp indexing for analytics queries
- Efficient foreign key relationships

## 🛡️ Data Integrity

### Constraints
- Foreign key constraints with CASCADE deletes
- Unique constraints on critical fields
- Not null constraints on required fields
- Check constraints for status fields

### Backup Strategy
- Regular PostgreSQL dumps
- Point-in-time recovery capability
- Environment-specific backups

---

**Last Updated:** September 23, 2025  
**Database Version:** PostgreSQL 14.19  
**Migration Status:** Up to date with Alembic

                  List of relations
 Schema |          Name          | Type  |   Owner   
--------+------------------------+-------+-----------
 public | ai_conversations       | table | adminuser
 public | ai_messages            | table | adminuser
 public | alembic_version        | table | adminuser
 public | audit_logs             | table | adminuser
 public | booking_services       | table | adminuser
 public | booking_slots          | table | adminuser
 public | bookings               | table | adminuser
 public | chat_channels          | table | adminuser
 public | chat_messages          | table | adminuser
 public | club_analytics         | table | adminuser
 public | club_members           | table | adminuser
 public | club_roles             | table | adminuser