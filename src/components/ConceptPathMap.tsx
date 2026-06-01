import React, { useRef, useEffect, useState } from 'react';
import type { JargonConcept } from '../data/JargonData';
import { Lock, Check, Sparkles, Award } from 'lucide-react';
import confetti from 'canvas-confetti';

interface ConceptPathMapProps {
  concepts: JargonConcept[];
  completedIds: number[];
  activeId: number;
  onNodeClick: (concept: JargonConcept) => void;
  themeColor: string;
  triggerUnlockAnimation: { from: number; to: number } | null;
  onUnlockAnimationComplete: () => void;
}

interface NodePosition {
  x: number;
  y: number;
}

export const ConceptPathMap: React.FC<ConceptPathMapProps> = ({
  concepts,
  completedIds,
  activeId,
  onNodeClick,
  themeColor,
  triggerUnlockAnimation,
  onUnlockAnimationComplete,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const activeNodeRef = useRef<HTMLButtonElement>(null);
  
  // Projectile animation states
  const [projectilePos, setProjectilePos] = useState<NodePosition | null>(null);
  const [isShooting, setIsShooting] = useState(false);

  // Layout grid parameters
  const colWidth = 160;
  const rowHeight = 150;
  const numCols = 5;

  // Calculate node position based on index (climbing snake layout)
  const getNodePos = (index: number): NodePosition => {
    const totalRows = Math.ceil(concepts.length / numCols); // 20 rows
    const rowFromBottom = Math.floor(index / numCols);
    const row = totalRows - 1 - rowFromBottom; // Climbing up
    const colInRow = index % numCols;
    
    // Winding factor (snake)
    const isForward = rowFromBottom % 2 === 0;
    const col = isForward ? colInRow : (numCols - 1 - colInRow);

    return {
      x: 90 + col * colWidth,
      y: 90 + row * rowHeight,
    };
  };

  // Bezier curve calculations for roads
  const getBezierCurveD = (fromPos: NodePosition, toPos: NodePosition): { d: string; cx: number; cy: number } => {
    const mx = (fromPos.x + toPos.x) / 2;
    const my = (fromPos.y + toPos.y) / 2;
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    
    // Offset perpendicular to the connection vector to curve it nicely
    const cx = mx - dy * 0.22;
    const cy = my + dx * 0.22;
    
    return {
      d: `M ${fromPos.x} ${fromPos.y} Q ${cx} ${cy} ${toPos.x} ${toPos.y}`,
      cx,
      cy
    };
  };

  // Center active node on load or activeNode change
  useEffect(() => {
    if (activeNodeRef.current) {
      activeNodeRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'center',
      });
    }
  }, [activeId]);

  // Run Bezier projectile animation when triggerUnlockAnimation is fired
  useEffect(() => {
    if (triggerUnlockAnimation) {
      const fromPos = getNodePos(triggerUnlockAnimation.from - 1);
      const toPos = getNodePos(triggerUnlockAnimation.to - 1);
      
      const { cx, cy } = getBezierCurveD(fromPos, toPos);

      setIsShooting(true);
      setProjectilePos(fromPos);

      let progress = 0;
      const duration = 900; // Fast snappy cartoon projectile (0.9s)
      const startTime = performance.now();

      const animateProjectile = (currentTime: number) => {
        const elapsed = currentTime - startTime;
        progress = Math.min(elapsed / duration, 1);

        // Snap-to-finish easing
        const t = 1 - Math.pow(1 - progress, 3); // easeOutCubic

        // Quadratic Bezier interpolation formula
        // B(t) = (1-t)^2 * P0 + 2*(1-t)*t * P1 + t^2 * P2
        const currentX = (1 - t) * (1 - t) * fromPos.x + 2 * (1 - t) * t * cx + t * t * toPos.x;
        const currentY = (1 - t) * (1 - t) * fromPos.y + 2 * (1 - t) * t * cy + t * t * toPos.y;
        
        setProjectilePos({ x: currentX, y: currentY });

        if (progress < 1) {
          requestAnimationFrame(animateProjectile);
        } else {
          // Finished shooting!
          setIsShooting(false);
          setProjectilePos(null);
          
          // Trigger confetti explosion
          const toNodeElement = document.getElementById(`node-btn-${triggerUnlockAnimation.to}`);
          if (toNodeElement) {
            const rect = toNodeElement.getBoundingClientRect();
            confetti({
              particleCount: 100,
              spread: 70,
              origin: {
                x: (rect.left + rect.width / 2) / window.innerWidth,
                y: (rect.top + rect.height / 2) / window.innerHeight,
              },
              colors: [themeColor, '#ff6b6b', '#ffd166', '#4ecdc4', '#6c5ce7'],
              ticks: 200,
            });
          }
          
          onUnlockAnimationComplete();
        }
      };

      requestAnimationFrame(animateProjectile);
    }
  }, [triggerUnlockAnimation]);

  const mapWidth = numCols * colWidth + 120;
  const mapHeight = Math.ceil(concepts.length / numCols) * rowHeight + 120;

  return (
    <div 
      ref={containerRef}
      className="w-full map-viewport relative brutal-card"
    >
      <div 
        className="winding-road-container"
        style={{ width: `${mapWidth}px`, height: `${mapHeight}px` }}
      >
        {/* SVG Winding Curved Roads Overlay */}
        <svg className="svg-overlay" style={{ width: `${mapWidth}px`, height: `${mapHeight}px` }}>
          {concepts.map((concept, index) => {
            if (index === concepts.length - 1) return null;
            const fromPos = getNodePos(index);
            const toPos = getNodePos(index + 1);
            
            const isPathUnlocked = completedIds.includes(concept.id);
            const { d } = getBezierCurveD(fromPos, toPos);

            return (
              <g key={`path-${concept.id}`}>
                {/* Underlay shadow border */}
                <path
                  d={d}
                  fill="none"
                  stroke="#000000"
                  strokeWidth="14"
                  strokeLinecap="round"
                />
                {/* Foreground Path Line */}
                <path
                  d={d}
                  fill="none"
                  className={`path-line ${isPathUnlocked ? 'unlocked' : 'locked'}`}
                  stroke={isPathUnlocked ? themeColor : '#cbd5e1'}
                  strokeWidth={isPathUnlocked ? "8" : "4"}
                  strokeLinecap="round"
                  style={{
                    strokeDasharray: isPathUnlocked ? 'none' : '10, 8'
                  }}
                />
              </g>
            );
          })}
        </svg>

        {/* Animated Projectile */}
        {isShooting && projectilePos && (
          <div 
            className="absolute projectile w-10 h-10 rounded-full border-4 border-black bg-white flex items-center justify-center shadow-[4px_4px_0px_#000]"
            style={{
              left: `${projectilePos.x - 20}px`,
              top: `${projectilePos.y - 20}px`,
              backgroundColor: themeColor,
              color: '#ffffff',
            }}
          >
            <Sparkles className="w-5 h-5 fill-white text-white animate-spin-proj" />
          </div>
        )}

        {/* Node Buttons */}
        {concepts.map((concept, index) => {
          const pos = getNodePos(index);
          const isCompleted = completedIds.includes(concept.id);
          const isActive = activeId === concept.id;
          const isLocked = !isCompleted && !isActive && concept.id > Math.max(...completedIds, 0) + 1;
          
          let nodeClass = 'locked';
          if (isCompleted) nodeClass = 'completed';
          else if (isActive) nodeClass = 'active-unlocked';
          else if (!isLocked) nodeClass = 'unlocked';

          return (
            <button
              key={concept.id}
              id={`node-btn-${concept.id}`}
              ref={isActive ? activeNodeRef : null}
              disabled={isLocked}
              onClick={() => onNodeClick(concept)}
              className={`map-node ${nodeClass}`}
              style={{
                left: `${pos.x - 45}px`,
                top: `${pos.y - 45}px`,
                borderWidth: '5px',
                borderColor: '#000000',
              }}
            >
              {isCompleted ? (
                <Check className="w-8 h-8 stroke-[4px]" />
              ) : isLocked ? (
                <Lock className="w-5 h-5 text-slate-400" />
              ) : concept.id === concepts.length ? (
                <Award className="w-8 h-8 stroke-[3px]" />
              ) : (
                <span className="font-comic text-2xl">{concept.id}</span>
              )}

              {/* Tooltip Label */}
              <span className="absolute -bottom-9 bg-white border-3 border-black rounded-lg px-2 py-0.5 text-xs font-black text-black whitespace-nowrap shadow-[3px_3px_0px_#000] pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                {concept.name}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
