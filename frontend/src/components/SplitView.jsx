import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

const SplitView = ({ left, right, leftTitle = 'Editor', rightTitle = 'Problem' }) => {
  const [leftWidth, setLeftWidth] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const splitViewRef = useRef(null);

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    
    const container = splitViewRef.current;
    if (!container) return;
    
    const containerRect = container.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const x = e.clientX - containerRect.left;
    const newLeftWidth = (x / containerWidth) * 100;
    
    // Set boundaries (10% to 90%)
    const boundedLeftWidth = Math.min(Math.max(10, newLeftWidth), 90);
    setLeftWidth(boundedLeftWidth);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  };

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const toggleLeftPanel = () => {
    setLeftCollapsed(!leftCollapsed);
    if (rightCollapsed) setRightCollapsed(false);
  };

  const toggleRightPanel = () => {
    setRightCollapsed(!rightCollapsed);
    if (leftCollapsed) setLeftCollapsed(false);
  };

  const leftPanelClass = leftCollapsed ? 'panel-collapsed editor-panel' : 'editor-panel';
  const rightPanelClass = rightCollapsed ? 'panel-collapsed problem-panel' : 'problem-panel';

  return (
    <div className="split-container" ref={splitViewRef}>
      <div 
        className={`panel-container ${leftPanelClass}`}
        style={{ flex: leftCollapsed ? '0 0 40px' : `0 0 ${leftWidth}%` }}
      >
        <div className="panel-header">
          <span>{leftTitle}</span>
          <button className="toggle-button" onClick={toggleLeftPanel}>
            {leftCollapsed ? '→' : '←'}
          </button>
        </div>
        {!leftCollapsed && <div className="panel-content">{left}</div>}
      </div>

      <div 
        className="resize-handle" 
        onMouseDown={handleMouseDown}
        style={{ display: leftCollapsed || rightCollapsed ? 'none' : 'flex' }}
      />

      <div 
        className={`panel-container ${rightPanelClass}`}
        style={{ flex: rightCollapsed ? '0 0 40px' : `0 0 ${100 - leftWidth}%` }}
      >
        <div className="panel-header">
          <span>{rightTitle}</span>
          <button className="toggle-button" onClick={toggleRightPanel}>
            {rightCollapsed ? '←' : '→'}
          </button>
        </div>
        {!rightCollapsed && <div className="panel-content">{right}</div>}
      </div>
    </div>
  );
};

SplitView.propTypes = {
  left: PropTypes.node.isRequired,
  right: PropTypes.node.isRequired,
  leftTitle: PropTypes.string,
  rightTitle: PropTypes.string,
};

export default SplitView;
