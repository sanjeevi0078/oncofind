import React, { useState, useEffect } from 'react';
import type { JargonConcept } from '../data/JargonData';
import { X, ThumbsUp, HelpCircle, Star, Sparkles, CheckCircle2 } from 'lucide-react';

interface JargonModalProps {
  concept: JargonConcept;
  onClose: () => void;
  onSatisfied: (conceptId: number) => void;
  isCompleted: boolean;
  themeColor: string;
  onConfusedTrigger: () => void; // Trigger mascot expression change
  onSatisfiedTrigger: () => void; // Trigger mascot excited/success state
}

export const JargonModal: React.FC<JargonModalProps> = ({
  concept,
  onClose,
  onSatisfied,
  isCompleted,
  themeColor,
  onConfusedTrigger,
  onSatisfiedTrigger,
}) => {
  const [explanationLevel, setExplanationLevel] = useState<1 | 2 | 3>(1);
  const [isPoofing, setIsPoofing] = useState<boolean>(false);

  // Reset explanation level when a new concept is opened
  useEffect(() => {
    setExplanationLevel(1);
    setIsPoofing(false);
  }, [concept]);

  const handleConfused = () => {
    if (explanationLevel < 3) {
      setIsPoofing(true);
      // Wait for the poof animation, then increment level
      setTimeout(() => {
        setExplanationLevel((prev) => (prev + 1) as 1 | 2 | 3);
        setIsPoofing(false);
        onConfusedTrigger();
      }, 300);
    } else {
      // Already at maximum simplification
      onConfusedTrigger();
    }
  };

  const handleSatisfied = () => {
    onSatisfiedTrigger();
    onSatisfied(concept.id);
  };

  const getLevelLabel = () => {
    switch (explanationLevel) {
      case 3:
        return "⚡ Level 3: Cartoon Superhero Analogy";
      case 2:
        return "👶 Level 2: Explain Like I'm 5 (ELI5)";
      case 1:
      default:
        return "📝 Level 1: Tech-Lite Simplified Definition";
    }
  };

  const getExplanationText = () => {
    switch (explanationLevel) {
      case 3:
        return concept.level3;
      case 2:
        return concept.level2;
      case 1:
      default:
        return concept.level1;
    }
  };

  const getCategoryColor = () => {
    switch (concept.category) {
      case 'Advanced':
        return 'bg-purple-200 text-purple-900';
      case 'Intermediate':
        return 'bg-blue-200 text-blue-900';
      case 'Basic':
      default:
        return 'bg-green-200 text-green-900';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      {/* Modal Container */}
      <div 
        className="w-full max-w-2xl brutal-card bg-white overflow-hidden relative"
        style={{ borderTopWidth: '12px', borderTopColor: themeColor }}
      >
        {/* Floating Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 p-2 bg-white border-2 border-black rounded-lg hover:bg-slate-100 hover:translate-y-[-1px] active:translate-y-[2px] transition-all shadow-[2px_2px_0px_#000]"
        >
          <X className="w-5 h-5 text-black" />
        </button>

        {/* Modal Header */}
        <div className="p-6 pb-2">
          <div className="flex items-center gap-3 mb-2">
            <span className={`px-3 py-1 rounded-full text-xs font-black uppercase border-2 border-black ${getCategoryColor()}`}>
              {concept.category}
            </span>
            <span className="text-sm font-bold text-slate-400">
              Concept #{concept.id}
            </span>
            {isCompleted && (
              <span className="flex items-center gap-1 text-green-600 font-extrabold text-xs bg-green-50 px-2 py-0.5 border border-green-500 rounded-lg">
                <CheckCircle2 className="w-3.5 h-3.5" /> MASTERED
              </span>
            )}
          </div>
          <h2 className="text-3xl font-black text-black m-0 leading-tight">
            {concept.name}
          </h2>
        </div>

        {/* Modal Content */}
        <div className="p-6 pt-2">
          {/* Explanation Mode Banner */}
          <div 
            className="px-4 py-2 border-3 border-black rounded-xl font-black text-sm uppercase tracking-wider mb-4 flex items-center justify-between"
            style={{ backgroundColor: `${themeColor}22` }}
          >
            <span>{getLevelLabel()}</span>
            <div className="flex gap-1">
              <Star className={`w-4 h-4 ${explanationLevel >= 1 ? 'fill-black' : 'text-slate-300'}`} />
              <Star className={`w-4 h-4 ${explanationLevel >= 2 ? 'fill-black' : 'text-slate-300'}`} />
              <Star className={`w-4 h-4 ${explanationLevel >= 3 ? 'fill-black' : 'text-slate-300'}`} />
            </div>
          </div>

          {/* Explanation Text Area */}
          <div className="min-h-[160px] flex items-center justify-center bg-slate-50 border-3 border-black rounded-xl p-6 mb-6 relative overflow-hidden">
            {/* Background comic grid lines */}
            <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#000_1px,transparent_1px)] [background-size:16px_16px]"></div>
            
            <p 
              className={`text-lg md:text-xl font-bold text-slate-800 leading-relaxed text-center max-w-lg relative z-10 transition-all duration-300 ${
                isPoofing ? 'animate-poof' : ''
              }`}
            >
              {getExplanationText()}
            </p>

            {/* Sparkle icons for level 3 */}
            {explanationLevel === 3 && (
              <>
                <Sparkles className="absolute top-3 left-3 w-6 h-6 text-yellow-400 animate-pulse" />
                <Sparkles className="absolute bottom-3 right-3 w-6 h-6 text-yellow-400 animate-pulse" />
              </>
            )}
          </div>

          {/* Modal Actions */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 border-t-4 border-black pt-5">
            {/* Still Confused Button */}
            <button
              onClick={handleConfused}
              disabled={explanationLevel === 3}
              className={`brutal-btn px-5 py-3 font-black text-lg ${
                explanationLevel === 3 
                  ? 'bg-slate-200 text-slate-400 border-slate-300 shadow-[2px_2px_0px_#ccc] cursor-not-allowed transform-none' 
                  : 'bg-indigo-500 text-white'
              }`}
            >
              <HelpCircle className="w-5 h-5" />
              {explanationLevel === 3 ? "Simpler impossible!" : "Still Confused... 🤯"}
            </button>

            {/* Satisfied Button */}
            <button
              onClick={handleSatisfied}
              className="brutal-btn brutal-btn-success px-6 py-3 font-black text-lg"
            >
              <ThumbsUp className="w-5 h-5 fill-white" />
              {isCompleted ? "Learn Next Node!" : "Satisfied! 👍"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
