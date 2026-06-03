import React, { useState, useEffect } from 'react';
import { submitAnswer, getSkills } from '../../services/api';
import type { MathSkill, AnswerResult } from '../../types';
import { CheckCircle, XCircle, Lightbulb, TrendingUp } from 'lucide-react';

interface Props { studentId: string; }

export const PracticeSession: React.FC<Props> = ({ studentId }) => {
  const [skills, setSkills] = useState<MathSkill[]>([]);
  const [selectedSkill, setSelectedSkill] = useState<MathSkill | null>(null);
  const [answer, setAnswer] = useState<boolean | null>(null);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sessionCount, setSessionCount] = useState(0);

  useEffect(() => {
    getSkills().then(d => { setSkills(d.skills); setSelectedSkill(d.skills[0]); });
  }, []);

  const handleSubmit = async (isCorrect: boolean) => {
    if (!selectedSkill) return;
    setSubmitting(true);
    try {
      const r = await submitAnswer({
        student_id: studentId,
        skill_code: selectedSkill.code,
        is_correct: isCorrect,
        response_time_secs: 30,
        hint_used: false,
      });
      setResult(r);
      setAnswer(isCorrect);
      setSessionCount(c => c + 1);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Practice Session</h2>
        <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">{sessionCount} answered</span>
      </div>

      {/* Skill selector */}
      <div>
        <label className="text-sm text-gray-600 font-medium">Select skill to practice:</label>
        <select
          className="mt-1 w-full border border-gray-200 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          onChange={e => setSelectedSkill(skills.find(s => s.code === e.target.value) || null)}
          value={selectedSkill?.code || ''}
        >
          {skills.map(s => <option key={s.code} value={s.code}>{s.name} (Grade {s.grade})</option>)}
        </select>
      </div>

      {/* Practice card */}
      {selectedSkill && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-500 to-blue-600 p-5">
            <p className="text-white/80 text-sm">{selectedSkill.code}</p>
            <h3 className="text-white text-xl font-bold mt-1">{selectedSkill.name}</h3>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-white/70 text-xs">Difficulty:</span>
              <div className="flex gap-1">
                {[1,2,3,4,5].map(i => (
                  <div key={i} className={`w-3 h-3 rounded-full ${i <= Math.round(selectedSkill.difficulty * 5) ? 'bg-white' : 'bg-white/30'}`} />
                ))}
              </div>
            </div>
          </div>

          <div className="p-5">
            <div className="bg-gray-50 rounded-xl p-4 mb-5 border border-gray-100">
              <p className="text-gray-600 text-sm mb-2 flex items-center gap-2"><Lightbulb size={14} className="text-amber-500" /> Sample problem:</p>
              <p className="text-gray-800 font-medium">
                {selectedSkill.name === 'Linear Equations'
                  ? 'Solve for x: 3x + 7 = -2. What is the value of x?'
                  : selectedSkill.name === 'Statistical Analysis'
                  ? 'The data set {4, 7, 7, 9, 12} has a median of?'
                  : `Apply your knowledge of ${selectedSkill.name} to solve the next challenge.`}
              </p>
            </div>

            {/* For demo: student self-reports correct/incorrect */}
            {!result ? (
              <div className="space-y-3">
                <p className="text-sm text-gray-500 text-center">Did you get the answer correct?</p>
                <div className="flex gap-3">
                  <button onClick={() => handleSubmit(true)} disabled={submitting}
                    className="flex-1 flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white py-3 rounded-xl font-medium transition-colors disabled:opacity-50">
                    <CheckCircle size={18} /> Yes, I got it!
                  </button>
                  <button onClick={() => handleSubmit(false)} disabled={submitting}
                    className="flex-1 flex items-center justify-center gap-2 bg-red-400 hover:bg-red-500 text-white py-3 rounded-xl font-medium transition-colors disabled:opacity-50">
                    <XCircle size={18} /> Not quite
                  </button>
                </div>
              </div>
            ) : (
              <div className={`rounded-xl p-4 ${result.is_correct ? 'bg-emerald-50 border border-emerald-100' : 'bg-red-50 border border-red-100'}`}>
                <div className="flex items-center gap-2 mb-3">
                  {result.is_correct ? <CheckCircle className="text-emerald-500" size={20} /> : <XCircle className="text-red-400" size={20} />}
                  <p className={`font-semibold ${result.is_correct ? 'text-emerald-700' : 'text-red-700'}`}>{result.encouragement}</p>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <TrendingUp size={14} className="text-blue-500" />
                  <span className="text-gray-600">Mastery: {Math.round(result.mastery_before * 100)}% → <strong>{Math.round(result.mastery_after * 100)}%</strong></span>
                </div>
                {result.misconception && (
                  <div className="mt-3 bg-amber-50 rounded-lg p-3 border border-amber-100">
                    <p className="text-xs font-semibold text-amber-700 mb-1">💡 Common Mistake Detected</p>
                    <p className="text-xs text-amber-600">{result.misconception.description}</p>
                  </div>
                )}
                <button onClick={() => { setResult(null); setAnswer(null); }}
                  className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-lg text-sm font-medium transition-colors">
                  Next Question →
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
