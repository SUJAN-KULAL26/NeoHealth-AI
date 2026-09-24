import React from 'react';
import { LoadingScreen } from '../components/LoadingScreen';

interface ProcessingProps {
  progress: number;
  processingStep: number;
  processingLabel: string;
  onCancel?: () => void;
}

export const Processing: React.FC<ProcessingProps> = ({
  progress,
  processingStep,
  processingLabel,
  onCancel,
}) => {
  return (
    <div style={{ padding: '2rem 0' }}>
      <LoadingScreen
        progress={progress}
        currentStep={processingStep}
        stepLabel={processingLabel}
        onCancel={onCancel}
      />
    </div>
  );
};
