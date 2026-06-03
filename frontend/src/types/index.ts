// Core AMILE type definitions

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'teacher' | 'admin' | 'district';
}

export interface KnowledgeState {
  skill_code: string;
  skill_name: string;
  grade: number;
  mastery: number;
  proficient: boolean;
  status: 'mastered' | 'proficient' | 'developing' | 'at_risk';
}

export interface EquitySnapshot {
  school_id: string;
  school_name: string;
  snapshot_date: string;
  cohort_size: number;
  overall_avg: number;
  proficiency_rate: number;
  by_demographic: {
    black: number | null;
    hispanic: number | null;
    white: number | null;
    asian: number | null;
    low_income: number | null;
  };
  achievement_gap_score: number;
  at_risk_count: number;
  skill_breakdown: Record<string, { skill_name: string; avg_mastery: number }>;
  alerts: Array<{ level: 'critical' | 'warning' | 'info'; message: string }>;
}

export interface AtRiskStudent {
  student_id: string;
  name: string;
  avg_mastery: number;
  risk_level: 'high' | 'medium';
  recommendation: string;
  weakest_skills: Array<{ skill: string; mastery: number }>;
}

export interface MathSkill {
  code: string;
  name: string;
  grade: number;
  difficulty: number;
}

export interface AnswerResult {
  is_correct: boolean;
  mastery_before: number;
  mastery_after: number;
  skill_name: string;
  misconception: {
    tag: string;
    description: string;
    teacher_alert: string;
  } | null;
  encouragement: string;
}
