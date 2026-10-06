CREATE TABLE ai_events (
  id SERIAL PRIMARY KEY,
  tenant_id TEXT,
  user_id TEXT,
  question TEXT,
  answer TEXT,
  created_at TIMESTAMP
);
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_events TO copilot_app;
