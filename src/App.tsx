import { useState, useEffect } from 'react';
import { JARGON_SETS, type JargonConcept } from './data/JargonData';
import { Mascot, type MascotState } from './components/Mascot';
import { ConceptPathMap } from './components/ConceptPathMap';
import { AbstractorPanel } from './components/AbstractorPanel';
import { Globe, Brain, Shield, RefreshCw, Trophy } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function App() {
  // Main states
  const [selectedSetId, setSelectedSetId] = useState<string>('web-sorcery');
  const [completedIdsBySet, setCompletedIdsBySet] = useState<Record<string, number[]>>({
    'web-sorcery': [],
    'ai-ml': [],
    'cyber-guardians': [],
  });
  const [activeIdBySet, setActiveIdBySet] = useState<Record<string, number>>({
    'web-sorcery': 1,
    'ai-ml': 1,
    'cyber-guardians': 1,
  });

  const [selectedConcept, setSelectedConcept] = useState<JargonConcept | null>(null);
  
  // Mascot states
  const [mascotState, setMascotState] = useState<MascotState>('idle');
  const [mascotText, setMascotText] = useState<string>('');

  // Path unlock animation trigger
  const [unlockAnimation, setUnlockAnimation] = useState<{ from: number; to: number } | null>(null);

  const currentSet = JARGON_SETS.find((s) => s.id === selectedSetId) || JARGON_SETS[0];
  const completedIds = completedIdsBySet[selectedSetId] || [];
  const activeId = activeIdBySet[selectedSetId] || 1;

  // Mascot welcome dialog when set changes
  useEffect(() => {
    setMascotState('idle');
    setMascotText(`Welcome to ${currentSet.name}! I'm Jargy, your jargon translator. Select Node 1 to begin our climb! 🗺️`);
  }, [selectedSetId]);

  // Load progress from LocalStorage on mount
  useEffect(() => {
    const savedCompleted = localStorage.getItem('jargon_completed_sets');
    const savedActive = localStorage.getItem('jargon_active_sets');
    if (savedCompleted) {
      try {
        setCompletedIdsBySet(JSON.parse(savedCompleted));
      } catch (e) {
        console.error(e);
      }
    }
    if (savedActive) {
      try {
        setActiveIdBySet(JSON.parse(savedActive));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  // Save progress to LocalStorage helper
  const saveProgress = (newCompleted: Record<string, number[]>, newActive: Record<string, number>) => {
    localStorage.setItem('jargon_completed_sets', JSON.stringify(newCompleted));
    localStorage.setItem('jargon_active_sets', JSON.stringify(newActive));
  };

  const handleNodeClick = (concept: JargonConcept) => {
    setSelectedConcept(concept);
    setMascotState('explaining');
    setMascotText(`Decoding "${concept.name}"... Click 'Still Confused' if my translation is too heavy!`);
  };

  const handleSatisfied = (conceptId: number) => {
    const isNewCompletion = !completedIds.includes(conceptId);
    
    if (isNewCompletion) {
      const nextCompleted = [...completedIds, conceptId];
      const nextActiveId = conceptId + 1;
      
      const newCompletedSets = {
        ...completedIdsBySet,
        [selectedSetId]: nextCompleted,
      };

      const newActiveSets = {
        ...activeIdBySet,
        [selectedSetId]: nextActiveId,
      };

      setCompletedIdsBySet(newCompletedSets);
      
      // Close modal first to let user watch the map animation
      setSelectedConcept(null);

      // Trigger the path shooting animation in ConceptPathMap
      if (conceptId < currentSet.concepts.length) {
        setTimeout(() => {
          setUnlockAnimation({ from: conceptId, to: nextActiveId });
        }, 200);
      } else {
        // Realm fully completed!
        confetti({
          particleCount: 150,
          spread: 80,
          origin: { y: 0.6 }
        });
        setMascotState('complete');
        setMascotText(`WOOHOO! You've decoded all 100 concepts in ${currentSet.name}! You are officially a master! 🧙‍♂️🏆`);
      }

      saveProgress(newCompletedSets, newActiveSets);
    } else {
      // Just reviewing an already completed node
      setSelectedConcept(null);
      setMascotState('idle');
    }
  };

  const handleUnlockAnimationComplete = () => {
    const nextActiveId = (unlockAnimation?.to || activeId);
    
    const newActiveSets = {
      ...activeIdBySet,
      [selectedSetId]: nextActiveId,
    };
    
    setActiveIdBySet(newActiveSets);
    setUnlockAnimation(null);
    setMascotState('idle');
    
    saveProgress(completedIdsBySet, newActiveSets);
  };

  const resetRealm = () => {
    if (window.confirm(`Are you sure you want to reset all your progress in ${currentSet.name}?`)) {
      const newCompletedSets = {
        ...completedIdsBySet,
        [selectedSetId]: [],
      };
      const newActiveSets = {
        ...activeIdBySet,
        [selectedSetId]: 1,
      };
      setCompletedIdsBySet(newCompletedSets);
      setActiveIdBySet(newActiveSets);
      saveProgress(newCompletedSets, newActiveSets);
      setMascotState('idle');
      setMascotText(`Realm reset! Ready to climb again from Node 1? Let's go! 🗺️`);
    }
  };

  const renderTabIcon = (iconName: string) => {
    switch (iconName) {
      case 'Brain':
        return <Brain className="w-5 h-5" />;
      case 'Shield':
        return <Shield className="w-5 h-5" />;
      case 'Globe':
      default:
        return <Globe className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen pb-16 px-4 md:px-8">
      {/* Cartoon Header */}
      <header className="max-w-7xl mx-auto pt-8 pb-6 flex flex-col md:flex-row items-center justify-between gap-4 border-b-6 border-black mb-8">
        <div className="text-center md:text-left">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-black m-0 flex items-center justify-center md:justify-start gap-2">
            JargonQuest <span className="animate-bounce-slow">🗺️</span>
          </h1>
          <p className="text-md font-extrabold text-slate-600 mt-1">
            Unlock 300 technical concepts sequentially, from scratch to senior wizard!
          </p>
        </div>

        {/* Action Controls */}
        <button 
          onClick={resetRealm}
          className="brutal-btn brutal-btn-gray px-4 py-2 text-sm"
        >
          <RefreshCw className="w-4 h-4" /> Reset Realm
        </button>
      </header>

      {/* Domain Selection Tabs */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {JARGON_SETS.map((set) => {
            const isSelected = set.id === selectedSetId;
            const completedCount = completedIdsBySet[set.id]?.length || 0;
            const percent = Math.round((completedCount / set.concepts.length) * 100);

            return (
              <button
                key={set.id}
                onClick={() => setSelectedSetId(set.id)}
                className="brutal-card p-4 flex items-center justify-between text-left cursor-pointer transition-all duration-200"
                style={{
                  backgroundColor: isSelected ? set.themeColor : '#ffffff',
                  transform: isSelected ? 'translate(4px, 4px)' : 'none',
                  boxShadow: isSelected ? '4px 4px 0px #000' : '8px 8px 0px #000',
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 border-2 border-black rounded-lg bg-white shadow-[2px_2px_0px_#000]">
                    {renderTabIcon(set.icon)}
                  </div>
                  <div>
                    <h3 className="font-black text-lg m-0 text-black leading-tight">{set.name}</h3>
                    <span className="text-xs font-bold text-slate-600 block mt-0.5">
                      {set.concepts.length} sequential concepts
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="font-black text-xs block text-slate-700">COMPLETED</span>
                  <span className="font-extrabold text-sm text-black">
                    {completedCount}/{set.concepts.length} ({percent}%)
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Split Panel Dashboard Layout */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Panel: Jargy & Narrative Abstractor */}
        <div className="lg:col-span-5 flex flex-col gap-6 w-full">
          <div className="w-full">
            <Mascot 
              state={mascotState} 
              text={mascotText} 
              themeColor={currentSet.themeColor} 
            />
          </div>
          
          <div className="w-full">
            <AbstractorPanel
              completedConcepts={currentSet.concepts.filter((c) => completedIds.includes(c.id))}
              totalConceptsCount={currentSet.concepts.length}
              themeColor={currentSet.themeColor}
            />
          </div>
        </div>

        {/* Right Panel: Scrollable Level Road Map */}
        <main className="lg:col-span-7 flex flex-col gap-6 w-full">
          <div className="flex items-center justify-between px-2">
            <div>
              <h2 className="text-2xl font-black text-black m-0 uppercase tracking-wide">
                The Path of Mastery
              </h2>
              <span className="text-xs font-bold text-slate-500">
                💡 Click unlocked or active nodes to explore. Complete them in order to clear the road.
              </span>
            </div>
            <div className="flex items-center gap-2 bg-white border-3 border-black px-3 py-1.5 rounded-xl shadow-[3px_3px_0px_#000]">
              <Trophy className="w-5 h-5 text-yellow-500 fill-yellow-500" />
              <span className="font-black text-xs uppercase text-slate-700">Active Node: {activeId}</span>
            </div>
          </div>

          <div className="w-full">
            <ConceptPathMap
              concepts={currentSet.concepts}
              completedIds={completedIds}
              activeId={activeId}
              onNodeClick={handleNodeClick}
              themeColor={currentSet.themeColor}
              triggerUnlockAnimation={unlockAnimation}
              onUnlockAnimationComplete={handleUnlockAnimationComplete}
            />
          </div>
        </main>
      </div>

      {/* Modal Popup for Explanations */}
      {selectedConcept && (
        <div className="relative">
          <JargonModalInner 
            concept={selectedConcept}
            onClose={() => {
              setSelectedConcept(null);
              setMascotState('idle');
              setMascotText(`Exploration paused! What is our next move, Tech Cadet? 🗺️`);
            }}
            onSatisfied={handleSatisfied}
            isCompleted={completedIds.includes(selectedConcept.id)}
            themeColor={currentSet.themeColor}
            onConfusedTrigger={() => {
              setMascotState('confused');
              setMascotText(`Beep Boop! Initiating ELI5 Simplifier protocols. Let me explain this like a child's toy! 🧸`);
            }}
            onSatisfiedTrigger={() => {
              setMascotState('success');
              setMascotText(`Success! Splendidly understood. Projectile initialized to activate the next terminal! 🚀`);
            }}
          />
        </div>
      )}
    </div>
  );
}

// Inline wrapper for Modal to prevent fast imports problems
import { JargonModal } from './components/JargonModal';
function JargonModalInner(props: React.ComponentProps<typeof JargonModal>) {
  return <JargonModal {...props} />;
}
