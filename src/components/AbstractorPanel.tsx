import React from 'react';
import type { JargonConcept } from '../data/JargonData';
import { BookOpen, Sparkles, Trophy } from 'lucide-react';

interface AbstractorPanelProps {
  completedConcepts: JargonConcept[];
  totalConceptsCount: number;
  themeColor: string;
}

export const AbstractorPanel: React.FC<AbstractorPanelProps> = ({
  completedConcepts,
  totalConceptsCount,
  themeColor,
}) => {
  const progressPercent = Math.round((completedConcepts.length / totalConceptsCount) * 100);

  // Generate a story summary based on completed concepts
  const getStorySummary = () => {
    if (completedConcepts.length === 0) {
      return "Start your journey by decoding the first concept! Your custom domain narrative will write itself here as you advance.";
    }

    return (
      <div className="flex flex-wrap gap-2 text-lg font-medium text-black leading-relaxed">
        {completedConcepts.map((concept, index) => {
          let connectorText = "";
          if (index === 0) {
            connectorText = "We begin with the";
          } else if (index === 1) {
            connectorText = ", which communicates with the";
          } else if (index === 2) {
            connectorText = ", located via its unique";
          } else if (index === 3) {
            connectorText = ", by sending an";
          } else if (index === 4) {
            connectorText = ", and receiving an";
          } else if (index === 5) {
            connectorText = ". To make addresses human-readable, we use";
          } else if (index === 6) {
            connectorText = ", directing traffic to specific software via a";
          } else if (index === 7) {
            connectorText = ", found at a full";
          } else if (index === 8) {
            connectorText = " under a friendly";
          } else if (index === 9) {
            connectorText = ", established over an active";
          } else {
            connectorText = index % 2 === 0 ? " ➔ Next, we build on this with" : " ➔ which is reinforced by";
          }

          return (
            <span key={concept.id} className="inline-flex flex-wrap items-center">
              <span className="text-slate-500 mr-1.5 font-normal">{connectorText}</span>
              <span 
                className="px-2 py-0.5 rounded-lg border-2 border-black font-bold text-sm"
                style={{ backgroundColor: `${themeColor}22` }}
              >
                {concept.name}
              </span>
            </span>
          );
        })}
        <span className="text-slate-500">.</span>
      </div>
    );
  };

  return (
    <div className="p-6 brutal-card bg-white max-w-4xl mx-auto my-6">
      {/* Header Info */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b-4 border-black pb-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 border-2 border-black rounded-lg bg-yellow-200 shadow-[2px_2px_0px_#000]">
            <BookOpen className="w-6 h-6 text-black" />
          </div>
          <div>
            <h2 className="text-2xl font-black m-0 text-black">The Abstractor</h2>
            <p className="text-sm font-semibold text-slate-500 m-0">Connecting concepts into a single picture</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="font-extrabold text-sm block">REALM MASTERY</span>
            <span className="font-black text-xl text-indigo-600">{completedConcepts.length} / {totalConceptsCount}</span>
          </div>
          <div className="w-32 h-6 border-3 border-black rounded-full overflow-hidden bg-slate-100 p-0.5 shadow-[2px_2px_0px_#000] relative">
            <div 
              className="h-full rounded-full transition-all duration-500 ease-out"
              style={{ 
                width: `${Math.max(progressPercent, 4)}%`, 
                backgroundColor: themeColor 
              }}
            ></div>
          </div>
          <span className="font-black text-lg">{progressPercent}%</span>
        </div>
      </div>

      {/* Story Board / Narrative */}
      <div className="bg-orange-50 border-3 border-black rounded-xl p-5 shadow-[4px_4px_0px_#000] relative overflow-hidden mb-6">
        <div className="absolute top-2 right-2 opacity-10">
          <Sparkles className="w-20 h-20 text-orange-400" />
        </div>
        <h3 className="text-lg font-black text-orange-800 uppercase tracking-wider mb-2 flex items-center gap-2">
          <Sparkles className="w-5 h-5" /> Cumulative Tech Storyline
        </h3>
        {getStorySummary()}
      </div>

      {/* Concept Comic Strips */}
      {completedConcepts.length > 0 && (
        <div>
          <h3 className="text-md font-bold uppercase text-slate-500 mb-3">Knowledge Comic Strip</h3>
          <div className="flex gap-4 overflow-x-auto pb-4 pt-1 px-1">
            {completedConcepts.map((concept, idx) => (
              <div 
                key={concept.id} 
                className="flex-shrink-0 w-48 brutal-card p-4 relative"
                style={{ borderTopWidth: '8px', borderTopColor: themeColor }}
              >
                <div className="absolute top-2 right-2 bg-black text-white text-xs font-black px-2 py-0.5 rounded-full">
                  #{idx + 1}
                </div>
                <div className="font-black text-lg mb-1 mt-2 text-black line-clamp-1">{concept.name}</div>
                <div className="text-xs font-bold text-slate-400 mb-2 uppercase">{concept.category}</div>
                <p className="text-xs font-medium text-slate-700 leading-snug line-clamp-4">
                  {concept.level2}
                </p>
              </div>
            ))}
            <div className="flex-shrink-0 w-48 border-4 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center p-4 text-center text-slate-400">
              <Trophy className="w-8 h-8 mb-2" />
              <span className="text-xs font-bold uppercase">Unlock {totalConceptsCount - completedConcepts.length} More!</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
