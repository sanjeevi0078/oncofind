import React from 'react';

export type MascotState = 'idle' | 'explaining' | 'confused' | 'success' | 'complete';

interface MascotProps {
  state: MascotState;
  text?: string;
  themeColor?: string;
}

export const Mascot: React.FC<MascotProps> = ({ state, text, themeColor = '#ff6b6b' }) => {
  // Get Jargy's cartoon remarks based on state
  const getBubbleText = () => {
    if (text) return text;
    switch (state) {
      case 'confused':
        return "Oops! Did I use too many big words? Let me run it through my Super-Simplifier 3000! 🤖💥";
      case 'success':
        return "BEEP BOOP! Target unlocked! Let's shoot some knowledge to the next terminal! 🚀✨";
      case 'complete':
        return "INCREDIBLE! You've mastered this technical realm! I bestow upon you the Royal Wizard Hat! 🧙‍♂️🏆";
      case 'explaining':
        return "Ah, a fine piece of jargon! Let me search my archives for the easiest explanation...";
      case 'idle':
      default:
        return "Hey there, Tech Cadet! Pick a node on the path below, and let's translate some wizard jargon! 🗺️";
    }
  };

  // Determine eyes and mouth paths based on state
  const renderFace = () => {
    switch (state) {
      case 'confused':
        return (
          <>
            {/* Spiral/Dizzy Eyes */}
            <path d="M25,35 A5,5 0 1,0 35,35 A5,5 0 1,0 25,35 M22,35 L38,35 M30,27 L30,43" stroke="#000" strokeWidth="3" fill="none" strokeLinecap="round" />
            <path d="M65,35 A5,5 0 1,0 75,35 A5,5 0 1,0 65,35 M62,35 L78,35 M70,27 L70,43" stroke="#000" strokeWidth="3" fill="none" strokeLinecap="round" />
            {/* Wavy Mouth */}
            <path d="M40,55 Q45,50 50,55 T60,55" stroke="#000" strokeWidth="3" fill="none" strokeLinecap="round" />
          </>
        );
      case 'success':
      case 'complete':
        return (
          <>
            {/* Happy Wink / Stars */}
            <path d="M22,32 L34,42 M34,32 L22,42" stroke="#000" strokeWidth="4" strokeLinecap="round" />
            <path d="M65,38 Q70,30 75,38" stroke="#000" strokeWidth="4" fill="none" strokeLinecap="round" />
            {/* Giant Laughing Mouth */}
            <path d="M38,50 Q50,62 62,50 Z" fill="#ff6b6b" stroke="#000" strokeWidth="3" strokeLinecap="round" />
            {/* Tongue */}
            <path d="M44,55 Q50,51 56,55 Q50,62 44,55" fill="#ffffff" />
          </>
        );
      case 'explaining':
        return (
          <>
            {/* Smart Glasses Eyes */}
            <rect x="18" y="28" width="22" height="16" rx="4" fill="none" stroke="#000" strokeWidth="4" />
            <rect x="60" y="28" width="22" height="16" rx="4" fill="none" stroke="#000" strokeWidth="4" />
            <line x1="40" y1="35" x2="60" y2="35" stroke="#000" strokeWidth="4" />
            {/* Happy Eyes inside glasses */}
            <circle cx="29" cy="36" r="3" fill="#000" />
            <circle cx="71" cy="36" r="3" fill="#000" />
            {/* Smug Smile */}
            <path d="M42,52 Q52,58 58,50" stroke="#000" strokeWidth="3" fill="none" strokeLinecap="round" />
          </>
        );
      case 'idle':
      default:
        return (
          <>
            {/* Normal Happy Eyes */}
            <path d="M22,35 Q30,25 38,35" stroke="#000" strokeWidth="4" fill="none" strokeLinecap="round" />
            <path d="M62,35 Q70,25 78,35" stroke="#000" strokeWidth="4" fill="none" strokeLinecap="round" />
            {/* Cute Smile */}
            <path d="M40,50 Q50,58 60,50" stroke="#000" strokeWidth="3" fill="none" strokeLinecap="round" />
          </>
        );
    }
  };

  return (
    <div className="flex flex-col md:flex-row items-center gap-6 p-6 brutal-card bg-amber-50 relative overflow-visible max-w-4xl mx-auto my-6">
      {/* Cartoon Character Render */}
      <div className="relative w-40 h-40 flex-shrink-0 animate-float">
        {/* Shadow under Jargy */}
        <div className="absolute -bottom-2 left-4 right-4 h-4 bg-black opacity-20 rounded-full blur-sm"></div>

        <svg viewBox="0 0 100 100" className="w-full h-full overflow-visible">
          {/* Antennas */}
          <line x1="50" y1="20" x2="50" y2="5" stroke="#000" strokeWidth="4" />
          <circle cx="50" cy="5" r="5" fill={themeColor} stroke="#000" strokeWidth="3" />
          
          <line x1="40" y1="20" x2="30" y2="8" stroke="#000" strokeWidth="3" />
          <circle cx="30" cy="8" r="4" fill="#000" />

          {/* Party Hat (for completed state) */}
          {state === 'complete' && (
            <path d="M35,22 L50,-10 L65,22 Z" fill="#ff6b6b" stroke="#000" strokeWidth="3" strokeLinejoin="round" />
          )}

          {/* Robot Ears */}
          <rect x="5" y="35" width="8" height="20" rx="3" fill="#000" stroke="#000" strokeWidth="2" />
          <rect x="87" y="35" width="8" height="20" rx="3" fill="#000" stroke="#000" strokeWidth="2" />

          {/* Main Monitor Head */}
          <rect x="10" y="20" width="80" height="60" rx="16" fill={themeColor} stroke="#000" strokeWidth="4" />
          
          {/* Inner Screen */}
          <rect x="16" y="25" width="68" height="42" rx="10" fill="#ffffff" stroke="#000" strokeWidth="3" />

          {/* Face Elements */}
          {renderFace()}

          {/* Cheeks */}
          <circle cx="22" cy="46" r="4" fill="#ff6b6b" opacity="0.5" />
          <circle cx="78" cy="46" r="4" fill="#ff6b6b" opacity="0.5" />

          {/* Robot Body & Cute Bowtie */}
          <path d="M40,80 L60,80 L55,90 L45,90 Z" fill="#000" />
          <path d="M42,88 L58,88 L50,80 Z" fill="#ff6b6b" stroke="#000" strokeWidth="2" />
          <circle cx="50" cy="88" r="3" fill="#ffffff" />
        </svg>
      </div>

      {/* Comic Speech Bubble */}
      <div className="flex-grow w-full md:w-auto">
        <div className="relative bg-white border-4 border-black rounded-2xl p-5 shadow-[6px_6px_0px_#000] min-h-[80px] flex items-center">
          {/* Speech Bubble Arrow pointing left (md+) or top (sm) */}
          <div className="absolute top-1/2 -left-[16px] -translate-y-1/2 w-0 h-0 border-t-[10px] border-t-transparent border-r-[16px] border-r-black border-b-[10px] border-b-transparent hidden md:block"></div>
          <div className="absolute top-1/2 -left-[10px] -translate-y-1/2 w-0 h-0 border-t-[8px] border-t-transparent border-r-[12px] border-r-white border-b-[8px] border-b-transparent hidden md:block"></div>
          
          <div className="absolute -top-[16px] left-1/2 -translate-x-1/2 w-0 h-0 border-l-[10px] border-l-transparent border-b-[16px] border-b-black border-r-[10px] border-r-transparent md:hidden"></div>
          <div className="absolute -top-[10px] left-1/2 -translate-x-1/2 w-0 h-0 border-l-[8px] border-l-transparent border-b-[12px] border-b-white border-r-[8px] border-r-transparent md:hidden"></div>

          <p className="font-semibold text-lg md:text-xl leading-relaxed text-black m-0 font-comic">
            {getBubbleText()}
          </p>
        </div>
      </div>
    </div>
  );
};
