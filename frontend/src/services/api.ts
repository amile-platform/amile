import axios from 'axios';
import type { KnowledgeState, EquitySnapshot, AtRiskStudent, MathSkill, AnswerResult } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE_URL });

// Knowledge Tracing
export const getKnowledgeMap = (studentId: string): Promise<{ knowledge_map: KnowledgeState[]; overall_mastery: number }> =>
  api.get(`/students/${studentId}/knowledge-map`).then(r => r.data);

export const submitAnswer = (payload: {
  student_id: string; skill_code: string; is_correct: boolean;
  response_time_secs: number; hint_used: boolean;
}): Promise<AnswerResult> =>
  api.post('/submit-answer', payload).then(r => r.data);

// Equity Dashboard
export const getEquityDashboard = (schoolId: string): Promise<EquitySnapshot> =>
  api.get(`/schools/${schoolId}/equity-dashboard`).then(r => r.data);

export const getAtRiskStudents = (schoolId: string): Promise<{ at_risk_students: AtRiskStudent[] }> =>
  api.get(`/schools/${schoolId}/at-risk`).then(r => r.data);

// Skills
export const getSkills = (): Promise<{ skills: MathSkill[] }> =>
  api.get('/skills').then(r => r.data);

// Stats
export const getDemoStats = () => api.get('/demo/stats').then(r => r.data);
