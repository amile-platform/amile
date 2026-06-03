import React, { useEffect, useState } from 'react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Legend
} from 'recharts';
import { AlertTriangle, TrendingDown, Users, Target } from 'lucide-react';
import type { EquitySnapshot, AtRiskStudent } from '../../types';
import { getEquityDashboard, getAtRiskStudents } from '../../services/api';

const COLORS = { mastered: '#10b981', proficient: '#3b82f6', developing: '#f59e0b', at_risk: '#ef4444' };
const DEMO_COLORS: Record<string, string> = {
  black: '#8b5cf6', hispanic: '#f59e0b', white: '#3b82f6', asian: '#10b981', low_income: '#ef4444'
};

interface Props { schoolId: string; }

export const EquityDashboard: React.FC<Props> = ({ schoolId }) => {
  const [snapshot, setSnapshot] = useState<EquitySnapshot | null>(null);
  const [atRisk, setAtRisk] = useState<AtRiskStudent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getEquityDashboard(schoolId), getAtRiskStudents(schoolId)])
      .then(([snap, ar]) => {
        setSnapshot(snap);
        setAtRisk(ar.at_risk_students);
      })
      .finally(() => setLoading(false));
  }, [schoolId]);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" /></div>;
  if (!snapshot) return <div className="text-red-500">Failed to load equity data</div>;

  const demoData = Object.entries(snapshot.by_demographic)
    .filter(([, v]) => v !== null)
    .map(([key, value]) => ({ name: key.charAt(0).toUpperCase() + key.slice(1), mastery: Math.round((value as number) * 100), fill: DEMO_COLORS[key] || '#6b7280' }));

  const skillData = Object.entries(snapshot.skill_breakdown).slice(0, 8).map(([code, { skill_name, avg_mastery }]) => ({
    skill: skill_name.length > 18 ? skill_name.substring(0, 18) + '…' : skill_name,
    mastery: Math.round(avg_mastery * 100),
  }));

  return (
    <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{snapshot.school_name}</h1>
          <p className="text-gray-500 text-sm">Equity Dashboard · {snapshot.snapshot_date}</p>
        </div>
        <div className="flex gap-3">
          {snapshot.alerts.map((alert, i) => (
            <div key={i} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${alert.level === 'critical' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'}`}>
              <AlertTriangle size={14} />
              {alert.level === 'critical' ? 'Critical Gap' : 'At-Risk Alert'}
            </div>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Students',      value: snapshot.cohort_size,                          icon: Users,        color: 'blue'  },
          { label: 'Proficiency',   value: `${Math.round(snapshot.proficiency_rate * 100)}%`, icon: Target,   color: 'green' },
          { label: 'Achievement Gap', value: `${Math.round(snapshot.achievement_gap_score * 100)}%`, icon: TrendingDown, color: snapshot.achievement_gap_score >= 0.2 ? 'red' : 'amber' },
          { label: 'At Risk',       value: snapshot.at_risk_count,                        icon: AlertTriangle,color: 'red'   },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className={`w-9 h-9 rounded-lg bg-${color}-100 flex items-center justify-center mb-3`}>
              <Icon size={18} className={`text-${color}-600`} />
            </div>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            <p className="text-sm text-gray-500">{label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Demographic Gap Chart */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-800 mb-4">Mastery by Demographic Group</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={demoData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`} />
              <YAxis type="category" dataKey="name" width={80} />
              <Tooltip formatter={(v) => [`${v}%`, 'Avg Mastery']} />
              <Bar dataKey="mastery" radius={[0, 4, 4, 0]}>
                {demoData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
              {/* Proficiency reference line */}
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-gray-400 mt-2">Proficiency threshold: 70%</p>
        </div>

        {/* Skill Breakdown */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-800 mb-4">Mastery by Skill Area</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={skillData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={50} />
              <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} />
              <Tooltip formatter={(v) => [`${v}%`, 'Avg Mastery']} />
              <Bar dataKey="mastery" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                {skillData.map((entry, i) => (
                  <Cell key={i} fill={entry.mastery >= 70 ? '#10b981' : entry.mastery >= 50 ? '#f59e0b' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* At-Risk Students Table */}
      {atRisk.length > 0 && (
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-800 mb-4">
            At-Risk Students — Proactive Intervention Required
            <span className="ml-2 text-sm font-normal text-gray-400">({atRisk.length} students)</span>
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Student</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Avg Mastery</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Risk Level</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Weakest Skills</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Recommended Action</th>
                </tr>
              </thead>
              <tbody>
                {atRisk.slice(0, 10).map((student) => (
                  <tr key={student.student_id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-3 px-3 font-medium text-gray-900">{student.name}</td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className="h-full bg-red-400 rounded-full" style={{ width: `${student.avg_mastery * 100}%` }} />
                        </div>
                        <span className="text-gray-700">{Math.round(student.avg_mastery * 100)}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${student.risk_level === 'high' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                        {student.risk_level.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-gray-600 text-xs">{student.weakest_skills.slice(0, 2).map(s => s.skill).join(', ')}</td>
                    <td className="py-3 px-3 text-gray-600 text-xs max-w-xs">{student.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
