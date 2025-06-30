const ERROR_TTL_DAYS     = 365;     // Number of days after which to automatically delete error reports
const ANALYTICS_TTL_DAYS = 365;     // Number of days after which to automatically delete usage analytics
const TTL_SECONDS        = (days) => 60 * 60 * 24 * days;

// --- error.errors ---
db = db.getSiblingDB("error");
db.errors.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: TTL_SECONDS(ERROR_TTL_DAYS) }
);

// --- error.bug_reports ---
db = db.getSiblingDB("error");
db.bug_reports.createIndex({ timestamp: 1 });

// --- analytics.user_feedbacks ---
db = db.getSiblingDB("analytics");
db.user_feedbacks.createIndex({ timestamp: 1, survey_version: 1 });
db.user_feedbacks.createIndex({ survey_version: 1, timestamp: 1 });

// --- analytics.usage_times ---
db = db.getSiblingDB("analytics");
db.usage_times.createIndex(
  { start_usage: 1 },
  { expireAfterSeconds: TTL_SECONDS(ANALYTICS_TTL_DAYS) }
);
db.usage_times.createIndex({ end_usage: 1 });
db.usage_times.createIndex({ duration_seconds: 1 });

// --- analytics.learning_topics ---
db = db.getSiblingDB("analytics");
db.learning_topics.createIndex({ keyword: 1 });
db.learning_topics.createIndex({ count: 1 });
