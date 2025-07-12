-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.admin_analytics (
  id integer NOT NULL DEFAULT nextval('admin_analytics_id_seq'::regclass),
  metric_name character varying NOT NULL,
  metric_value numeric NOT NULL,
  metric_category character varying NOT NULL,
  time_period character varying NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  date date DEFAULT CURRENT_DATE,
  CONSTRAINT admin_analytics_pkey PRIMARY KEY (id)
);
CREATE TABLE public.admin_notifications (
  id integer NOT NULL DEFAULT nextval('admin_notifications_id_seq'::regclass),
  notification_type character varying NOT NULL,
  title character varying NOT NULL,
  message text NOT NULL,
  priority character varying DEFAULT 'medium'::character varying,
  status character varying DEFAULT 'unread'::character varying,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  read_at timestamp without time zone,
  CONSTRAINT admin_notifications_pkey PRIMARY KEY (id)
);
CREATE TABLE public.agora_usage_logs (
  id integer NOT NULL DEFAULT nextval('agora_usage_logs_id_seq'::regclass),
  session_id character varying NOT NULL,
  user_email character varying NOT NULL,
  event_type character varying NOT NULL,
  event_data jsonb DEFAULT '{}'::jsonb,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT agora_usage_logs_pkey PRIMARY KEY (id),
  CONSTRAINT agora_usage_logs_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.ai_insights_cache (
  id integer NOT NULL DEFAULT nextval('ai_insights_cache_id_seq'::regclass),
  insight_type character varying NOT NULL,
  data jsonb NOT NULL,
  expires_at timestamp without time zone NOT NULL,
  is_active boolean DEFAULT true,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT ai_insights_cache_pkey PRIMARY KEY (id)
);
CREATE TABLE public.ai_pricing_recommendations (
  id integer NOT NULL DEFAULT nextval('ai_pricing_recommendations_id_seq'::regclass),
  service_type character varying NOT NULL,
  current_price numeric NOT NULL,
  recommended_price numeric NOT NULL,
  demand_factor numeric DEFAULT 1.0,
  cost_breakdown jsonb DEFAULT '{}'::jsonb,
  ai_recommendation jsonb DEFAULT '{}'::jsonb,
  pricing_rationale text,
  confidence_score numeric DEFAULT 0.5,
  status character varying DEFAULT 'pending'::character varying,
  admin_approved boolean DEFAULT false,
  admin_notes text,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  expires_at timestamp without time zone,
  CONSTRAINT ai_pricing_recommendations_pkey PRIMARY KEY (id),
  CONSTRAINT ai_pricing_recommendations_service_type_fkey FOREIGN KEY (service_type) REFERENCES public.service_types(name)
);
CREATE TABLE public.ai_recommendations (
  id integer NOT NULL DEFAULT nextval('ai_recommendations_id_seq'::regclass),
  recommendation_type character varying NOT NULL,
  title character varying NOT NULL,
  description text NOT NULL,
  expected_revenue_impact numeric,
  implementation_difficulty character varying,
  timeline_weeks integer,
  priority_score numeric,
  priority_level character varying,
  status character varying DEFAULT 'pending'::character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT ai_recommendations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.api_integrations (
  id integer NOT NULL DEFAULT nextval('api_integrations_id_seq'::regclass),
  integration_name character varying NOT NULL UNIQUE,
  api_key_encrypted text,
  configuration jsonb DEFAULT '{}'::jsonb,
  status character varying DEFAULT 'inactive'::character varying,
  last_tested timestamp without time zone,
  test_result jsonb DEFAULT '{}'::jsonb,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT api_integrations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.api_usage_metrics (
  id integer NOT NULL DEFAULT nextval('api_usage_metrics_id_seq'::regclass),
  api_name character varying NOT NULL,
  endpoint character varying NOT NULL,
  user_email character varying,
  request_count integer DEFAULT 1,
  response_time_ms integer,
  status_code integer,
  error_message text,
  request_size_bytes integer,
  response_size_bytes integer,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  date date DEFAULT CURRENT_DATE,
  CONSTRAINT api_usage_metrics_pkey PRIMARY KEY (id)
);
CREATE TABLE public.avatar_generation_queue (
  id integer NOT NULL DEFAULT nextval('avatar_generation_queue_id_seq'::regclass),
  session_id character varying NOT NULL,
  user_email character varying NOT NULL,
  template_id integer NOT NULL,
  prompt text NOT NULL,
  priority integer DEFAULT 5,
  status character varying DEFAULT 'queued'::character varying,
  attempts integer DEFAULT 0,
  error_message text,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  started_at timestamp without time zone,
  completed_at timestamp without time zone,
  CONSTRAINT avatar_generation_queue_pkey PRIMARY KEY (id),
  CONSTRAINT avatar_generation_queue_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.avatar_templates(id),
  CONSTRAINT avatar_generation_queue_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.avatar_sessions (
  id integer NOT NULL DEFAULT nextval('avatar_sessions_id_seq'::regclass),
  session_id character varying NOT NULL UNIQUE,
  user_email character varying NOT NULL,
  template_id integer NOT NULL,
  avatar_prompt text NOT NULL,
  generated_avatar_url character varying,
  status character varying DEFAULT 'pending'::character varying,
  generation_time_seconds numeric,
  quality_score numeric,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT avatar_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT avatar_sessions_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.avatar_templates(id),
  CONSTRAINT avatar_sessions_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.avatar_templates (
  id integer NOT NULL DEFAULT nextval('avatar_templates_id_seq'::regclass),
  template_name character varying NOT NULL UNIQUE,
  avatar_style character varying NOT NULL,
  voice_tone character varying NOT NULL,
  background_style character varying NOT NULL,
  clothing_style character varying NOT NULL,
  description text,
  preview_image_url character varying,
  is_premium boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT avatar_templates_pkey PRIMARY KEY (id)
);
CREATE TABLE public.birth_chart_cache (
  id integer NOT NULL DEFAULT nextval('birth_chart_cache_id_seq'::regclass),
  user_email character varying NOT NULL,
  birth_details_hash character varying NOT NULL UNIQUE,
  birth_details jsonb NOT NULL,
  chart_data jsonb NOT NULL,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  expires_at timestamp without time zone,
  access_count integer DEFAULT 1,
  last_accessed timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT birth_chart_cache_pkey PRIMARY KEY (id),
  CONSTRAINT birth_chart_cache_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.credit_packages (
  id integer NOT NULL DEFAULT nextval('credit_packages_id_seq'::regclass),
  name character varying NOT NULL,
  credits_amount integer NOT NULL,
  price_usd numeric NOT NULL,
  bonus_credits integer DEFAULT 0,
  description text,
  enabled boolean DEFAULT true,
  stripe_product_id character varying,
  stripe_price_id character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT credit_packages_pkey PRIMARY KEY (id)
);
CREATE TABLE public.donations (
  id integer NOT NULL DEFAULT nextval('donations_id_seq'::regclass),
  name character varying NOT NULL,
  tamil_name character varying,
  description text,
  price_usd numeric NOT NULL,
  icon character varying DEFAULT '🪔'::character varying,
  category character varying,
  enabled boolean DEFAULT true,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT donations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.feature_flags (
  id integer NOT NULL DEFAULT nextval('feature_flags_id_seq'::regclass),
  flag_name character varying NOT NULL UNIQUE,
  is_enabled boolean DEFAULT false,
  description text,
  target_audience character varying DEFAULT 'all'::character varying,
  rollout_percentage integer DEFAULT 0,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT feature_flags_pkey PRIMARY KEY (id)
);
CREATE TABLE public.feature_usage_analytics (
  id integer NOT NULL DEFAULT nextval('feature_usage_analytics_id_seq'::regclass),
  feature_name character varying NOT NULL,
  usage_count integer DEFAULT 1,
  user_email character varying,
  session_id character varying,
  metadata jsonb DEFAULT '{}'::jsonb,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  date date DEFAULT CURRENT_DATE,
  CONSTRAINT feature_usage_analytics_pkey PRIMARY KEY (id),
  CONSTRAINT feature_usage_analytics_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.live_chat_sessions (
  id integer NOT NULL DEFAULT nextval('live_chat_sessions_id_seq'::regclass),
  session_id character varying NOT NULL UNIQUE,
  user_email character varying NOT NULL,
  channel_name character varying NOT NULL,
  agora_app_id character varying NOT NULL,
  agora_token character varying NOT NULL,
  user_role character varying DEFAULT 'audience'::character varying,
  session_type character varying DEFAULT 'spiritual_guidance'::character varying,
  mode character varying DEFAULT 'video'::character varying,
  status character varying DEFAULT 'active'::character varying,
  credits_used integer DEFAULT 0,
  duration_minutes integer,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  started_at timestamp without time zone,
  ended_at timestamp without time zone,
  expires_at timestamp without time zone,
  CONSTRAINT live_chat_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT live_chat_sessions_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.marketing_campaigns (
  id integer NOT NULL DEFAULT nextval('marketing_campaigns_id_seq'::regclass),
  campaign_id character varying NOT NULL UNIQUE,
  name character varying NOT NULL,
  description text,
  campaign_type character varying NOT NULL,
  target_audience jsonb,
  budget numeric,
  status character varying DEFAULT 'draft'::character varying,
  start_date timestamp without time zone,
  end_date timestamp without time zone,
  performance_metrics jsonb DEFAULT '{}'::jsonb,
  ai_recommendations jsonb DEFAULT '{}'::jsonb,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT marketing_campaigns_pkey PRIMARY KEY (id)
);
CREATE TABLE public.marketing_insights (
  id integer NOT NULL DEFAULT nextval('marketing_insights_id_seq'::regclass),
  insight_id character varying NOT NULL UNIQUE,
  insight_type character varying NOT NULL,
  title character varying NOT NULL,
  description text NOT NULL,
  data_points jsonb,
  confidence_score numeric,
  actionable_recommendations ARRAY,
  impact_level character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  expires_at timestamp without time zone,
  CONSTRAINT marketing_insights_pkey PRIMARY KEY (id)
);
CREATE TABLE public.monetization_experiments (
  id integer NOT NULL DEFAULT nextval('monetization_experiments_id_seq'::regclass),
  experiment_name character varying NOT NULL,
  experiment_type character varying NOT NULL,
  control_conversion_rate numeric,
  test_conversion_rate numeric,
  control_revenue numeric,
  test_revenue numeric,
  status character varying DEFAULT 'running'::character varying,
  winner character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT monetization_experiments_pkey PRIMARY KEY (id)
);
CREATE TABLE public.monetization_insights (
  id integer NOT NULL DEFAULT nextval('monetization_insights_id_seq'::regclass),
  recommendation_id character varying NOT NULL UNIQUE,
  recommendation_type character varying NOT NULL,
  title character varying NOT NULL,
  description text NOT NULL,
  projected_revenue_increase_percent numeric,
  projected_user_impact character varying,
  confidence_score numeric NOT NULL,
  implementation_effort character varying NOT NULL,
  timeframe_days integer,
  risk_level character varying NOT NULL,
  data_points jsonb,
  status character varying DEFAULT 'pending'::character varying,
  admin_response text,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  expires_at timestamp without time zone,
  CONSTRAINT monetization_insights_pkey PRIMARY KEY (id)
);
CREATE TABLE public.payments (
  id integer NOT NULL DEFAULT nextval('payments_id_seq'::regclass),
  user_email character varying NOT NULL,
  amount numeric NOT NULL,
  currency character varying DEFAULT 'USD'::character varying,
  status character varying DEFAULT 'pending'::character varying,
  payment_method character varying,
  transaction_id character varying,
  product_id character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT payments_pkey PRIMARY KEY (id),
  CONSTRAINT payments_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.performance_analytics (
  id integer NOT NULL DEFAULT nextval('performance_analytics_id_seq'::regclass),
  metric_name character varying NOT NULL,
  metric_value numeric NOT NULL,
  metric_type character varying NOT NULL,
  time_period character varying NOT NULL,
  dimensions jsonb DEFAULT '{}'::jsonb,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  date date DEFAULT CURRENT_DATE,
  CONSTRAINT performance_analytics_pkey PRIMARY KEY (id)
);
CREATE TABLE public.platform_settings (
  id integer NOT NULL DEFAULT nextval('platform_settings_id_seq'::regclass),
  key character varying NOT NULL UNIQUE,
  value jsonb NOT NULL,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT platform_settings_pkey PRIMARY KEY (id)
);
CREATE TABLE public.pricing_config (
  id integer NOT NULL DEFAULT nextval('pricing_config_id_seq'::regclass),
  key character varying NOT NULL UNIQUE,
  value character varying NOT NULL,
  type character varying NOT NULL,
  description text,
  is_active boolean DEFAULT true,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pricing_config_pkey PRIMARY KEY (id)
);
CREATE TABLE public.rag_knowledge_base (
  id integer NOT NULL DEFAULT nextval('rag_knowledge_base_id_seq'::regclass),
  title character varying NOT NULL,
  content text NOT NULL,
  category character varying,
  tags ARRAY,
  embedding_vector ARRAY,
  metadata jsonb DEFAULT '{}'::jsonb,
  source_url character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  is_active boolean DEFAULT true,
  CONSTRAINT rag_knowledge_base_pkey PRIMARY KEY (id)
);
CREATE TABLE public.revenue_analytics (
  id integer NOT NULL DEFAULT nextval('revenue_analytics_id_seq'::regclass),
  revenue_type character varying NOT NULL,
  amount numeric NOT NULL,
  currency character varying DEFAULT 'USD'::character varying,
  service_type character varying,
  user_email character varying,
  transaction_id character varying,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  date date DEFAULT CURRENT_DATE,
  CONSTRAINT revenue_analytics_pkey PRIMARY KEY (id),
  CONSTRAINT revenue_analytics_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.schema_migrations (
  id integer NOT NULL DEFAULT nextval('schema_migrations_id_seq'::regclass),
  migration_name character varying NOT NULL UNIQUE,
  applied_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT schema_migrations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.service_types (
  id integer NOT NULL DEFAULT nextval('service_types_id_seq1'::regclass),
  name character varying NOT NULL UNIQUE,
  display_name character varying NOT NULL,
  description text,
  category character varying,
  duration_minutes integer DEFAULT 15,
  voice_enabled boolean DEFAULT true,
  video_enabled boolean DEFAULT false,
  interactive_enabled boolean DEFAULT false,
  birth_chart_enabled boolean DEFAULT false,
  remedies_enabled boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  service_type character varying,
  guidance boolean DEFAULT false,
  premium boolean DEFAULT false,
  icon character varying DEFAULT '🔮'::character varying,
  gradient_class character varying DEFAULT 'from-purple-500 to-indigo-600'::character varying,
  active boolean DEFAULT true,
  featured boolean DEFAULT false,
  requires_birth_details boolean DEFAULT true,
  ai_enhanced boolean DEFAULT false,
  personalized boolean DEFAULT false,
  includes_remedies boolean DEFAULT false,
  includes_predictions boolean DEFAULT false,
  includes_compatibility boolean DEFAULT false,
  knowledge_domains jsonb DEFAULT '[]'::jsonb,
  persona_modes jsonb DEFAULT '[]'::jsonb,
  base_credits integer DEFAULT 5,
  last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  enabled boolean DEFAULT true,
  price_usd numeric DEFAULT 0,
  service_category character varying,
  avatar_video_enabled boolean DEFAULT false,
  live_chat_enabled boolean DEFAULT false,
  CONSTRAINT service_types_pkey PRIMARY KEY (id)
);
CREATE TABLE public.service_usage_logs (
  id integer NOT NULL DEFAULT nextval('service_usage_logs_id_seq'::regclass),
  user_email character varying NOT NULL,
  service_type character varying NOT NULL,
  session_reference character varying,
  credits_used integer NOT NULL,
  duration_minutes integer,
  cost_breakdown jsonb DEFAULT '{}'::jsonb,
  usage_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  billing_status character varying DEFAULT 'completed'::character varying,
  CONSTRAINT service_usage_logs_pkey PRIMARY KEY (id),
  CONSTRAINT service_usage_logs_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email),
  CONSTRAINT service_usage_logs_service_type_fkey FOREIGN KEY (service_type) REFERENCES public.service_types(name)
);
CREATE TABLE public.session_participants (
  id integer NOT NULL DEFAULT nextval('session_participants_id_seq'::regclass),
  session_id character varying NOT NULL,
  user_email character varying NOT NULL,
  agora_uid integer NOT NULL,
  role character varying DEFAULT 'audience'::character varying,
  joined_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  left_at timestamp without time zone,
  duration_minutes integer,
  CONSTRAINT session_participants_pkey PRIMARY KEY (id),
  CONSTRAINT session_participants_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.sessions (
  id integer NOT NULL DEFAULT nextval('sessions_id_seq'::regclass),
  session_id character varying NOT NULL UNIQUE,
  user_email character varying NOT NULL,
  service_type character varying NOT NULL,
  status character varying DEFAULT 'active'::character varying,
  credits_used integer DEFAULT 0,
  start_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  end_time timestamp without time zone,
  duration_minutes integer,
  birth_details jsonb DEFAULT '{}'::jsonb,
  questions_asked ARRAY,
  ai_responses ARRAY,
  satisfaction_rating integer CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
  feedback text,
  session_data jsonb DEFAULT '{}'::jsonb,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT sessions_pkey PRIMARY KEY (id),
  CONSTRAINT sessions_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email),
  CONSTRAINT sessions_service_type_fkey FOREIGN KEY (service_type) REFERENCES public.service_types(name)
);
CREATE TABLE public.social_campaigns (
  id integer NOT NULL DEFAULT nextval('social_campaigns_id_seq'::regclass),
  campaign_id character varying NOT NULL UNIQUE,
  name character varying NOT NULL,
  platform character varying NOT NULL,
  campaign_type character varying NOT NULL,
  budget numeric,
  target_audience jsonb,
  duration_days integer,
  status character varying DEFAULT 'active'::character varying,
  start_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  end_date timestamp without time zone,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT social_campaigns_pkey PRIMARY KEY (id)
);
CREATE TABLE public.social_content (
  id integer NOT NULL DEFAULT nextval('social_content_id_seq'::regclass),
  content_id character varying NOT NULL UNIQUE,
  title character varying NOT NULL,
  content text NOT NULL,
  content_type character varying NOT NULL,
  platform character varying NOT NULL,
  hashtags text,
  media_urls ARRAY,
  engagement_score numeric,
  performance_metrics jsonb DEFAULT '{}'::jsonb,
  status character varying DEFAULT 'draft'::character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT social_content_pkey PRIMARY KEY (id)
);
CREATE TABLE public.social_posts (
  id integer NOT NULL DEFAULT nextval('social_posts_id_seq'::regclass),
  post_id character varying NOT NULL UNIQUE,
  platform character varying NOT NULL,
  platform_post_id character varying,
  title character varying,
  content text NOT NULL,
  hashtags text,
  media_url character varying,
  scheduled_time timestamp without time zone,
  posted_time timestamp without time zone,
  status character varying DEFAULT 'scheduled'::character varying,
  engagement_metrics jsonb DEFAULT '{}'::jsonb,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT social_posts_pkey PRIMARY KEY (id)
);
CREATE TABLE public.system_configuration (
  id integer NOT NULL DEFAULT nextval('system_configuration_id_seq'::regclass),
  config_key character varying NOT NULL UNIQUE,
  config_value jsonb NOT NULL,
  description text,
  is_sensitive boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT system_configuration_pkey PRIMARY KEY (id)
);
CREATE TABLE public.system_logs (
  id integer NOT NULL DEFAULT nextval('system_logs_id_seq'::regclass),
  log_level character varying NOT NULL,
  component character varying NOT NULL,
  message text NOT NULL,
  details jsonb DEFAULT '{}'::jsonb,
  user_email character varying,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT system_logs_pkey PRIMARY KEY (id),
  CONSTRAINT system_logs_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.user_analytics (
  id integer NOT NULL DEFAULT nextval('user_analytics_id_seq'::regclass),
  user_email character varying NOT NULL,
  event_type character varying NOT NULL,
  event_data jsonb DEFAULT '{}'::jsonb,
  session_id character varying,
  timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  date date DEFAULT CURRENT_DATE,
  CONSTRAINT user_analytics_pkey PRIMARY KEY (id),
  CONSTRAINT user_analytics_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.user_purchases (
  id integer NOT NULL DEFAULT nextval('user_purchases_id_seq'::regclass),
  user_email character varying NOT NULL,
  service_type character varying NOT NULL,
  credits_purchased integer NOT NULL,
  amount_paid numeric NOT NULL,
  currency character varying DEFAULT 'USD'::character varying,
  payment_method character varying,
  transaction_id character varying,
  status character varying DEFAULT 'completed'::character varying,
  purchased_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  expires_at timestamp without time zone,
  CONSTRAINT user_purchases_pkey PRIMARY KEY (id),
  CONSTRAINT user_purchases_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.user_sessions (
  id integer NOT NULL DEFAULT nextval('user_sessions_id_seq'::regclass),
  session_id character varying NOT NULL UNIQUE,
  user_email character varying NOT NULL,
  session_type character varying NOT NULL,
  status character varying DEFAULT 'active'::character varying,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  expires_at timestamp without time zone,
  last_activity timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  ip_address inet,
  user_agent text,
  CONSTRAINT user_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT user_sessions_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.users(email)
);
CREATE TABLE public.users (
  id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  email character varying NOT NULL UNIQUE,
  password_hash character varying NOT NULL,
  full_name character varying,
  phone character varying,
  date_of_birth date,
  birth_time time without time zone,
  birth_location character varying,
  timezone character varying DEFAULT 'Asia/Colombo'::character varying,
  credits integer DEFAULT 0,
  role character varying DEFAULT 'user'::character varying,
  is_active boolean DEFAULT true,
  email_verified boolean DEFAULT false,
  phone_verified boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  last_login_at timestamp without time zone,
  profile_picture_url character varying,
  preferences jsonb DEFAULT '{}'::jsonb,
  birth_chart_data jsonb DEFAULT '{}'::jsonb,
  subscription_status character varying DEFAULT 'free'::character varying,
  subscription_expires_at timestamp without time zone,
  total_sessions integer DEFAULT 0,
  total_spent numeric DEFAULT 0.00,
  CONSTRAINT users_pkey PRIMARY KEY (id)
);