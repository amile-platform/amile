import React, { useEffect, useState } from 'react';
import { getKnowledgeMap } from '../../services/api';
import type { KnowledgeState } from '../../types';

const STATUS_CONFIG = {
  mastered:   { label: 'Mastered',   color: 'bg-emerald-500', text: 'text-emerald-700', bg: 'bg-emerald-50' },
  proficient: { label: 'Proficient', color: 'bg-blue-500',    text: 'text-blue-700',    bg: 'bg-blue-50'    },
  developing: { label: 'Developing', color: 'bg-amber-400',   text: 'text-amber-700',   bg: 'bg-amber-50'   },
  at_risk:    { label: 'At Risk',    color: 'bg-red-400',     text: 'text-red-700',     bg: 'bg-red-50'     },
};

interface Props { studentId: string; }

export const KnowledgeMap: React.FC<Props> = ({ studentId }) => {
  const [data, setData] = useState<{ knowledge_map: KnowledgeState[]; overall_mastery: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getKnowledgeMap(studentId).then(setData).finally(() => setLoading(false));
  }, [studentId]);

  if (loading) return <div className="animate-pulse">Loading knowledge map...</div>;
  if (!data) return <div className="text-red-500">Could not load knowledge map.</div>;

  const grouped = data.knowledge_map.reduce<Record<number, KnowledgeState[]>>((acc, ks) => {
    (acc[ks.grade] = acc[ks.grade] || []).push(ks);
    return acc;
  }, {});

  return (
    <div className="p-6 space-y-6">
      {/* Overall progress */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white">
        <p className="text-blue-100 text-sm mb-1">Overall Mathematics Mastery</p>
        <div className="flex items-end gap-3">
          <span className="text-5xl font-bold">{Math.round(data.overall_mastery * 100)}%</span>
          <span className="text-blue-200 mb-1">{data.overall_mastery >= 0.7 ? '🎉 Proficient!' : data.overall_mastery >= 0.5 ? '📈 Making progress' : '💪 Keep going!'}</span>
        </div>
        <div className="mt-3 h-3 bg-blue-900/40 rounded-full overflow-hidden">
          <div className="h-full bg-white/80 rounded-full transition-all duration-700" style={{ width: `${data.overall_mastery * 100}%` }} />
        </div>
      </div>

      {/* By grade level */}
      {Object.entries(grouped).sort(([a], [b]) => Number(a) - Number(b)).map(([grade, skills]) => (
        <div key={grade}>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Grade {grade} Skills</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {skills.map((skill) => {
              const cfg = STATUS_CONFIG[skill.status];
              return (
                <div key={skill.skill_code} className={`${cfg.bg} rounded-xl p-4 border border-transparent hover:shadow-md transition-shadow`}>
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-medium text-gray-800 text-sm">{skill.skill_name}</p>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cfg.text} ${cfg.bg}`}>{cfg.label}</span>
                  </div>
                  <div className="h-2 bg-white/60 rounded-full overflow-hidden">
                    <div className={`h-full ${cfg.color} rounded-full transition-all duration-500`} style={{ width: `${skill.mastery * 100}%` }} />
                  </div>
                  <p className="text-right text-xs text-gray-500 mt-1">{Math.round(skill.mastery * 100)}%</p>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};
