import React from 'react';
import { LoadingScreen } from '../components/LoadingScreen';

interface ProcessingProps {
  progress: number;
  processingStep: number;
  processingLabel: string;
}

export const Processing: React.FC<ProcessingProps> = ({
  progress,
  processingStep,
  processingLabel,
}) => {
  return (
    <div style={{ padding: '2rem 0' }}>
      <LoadingScreen
        progress={progress}
        currentStep={processingStep}
        stepLabel={processingLabel}
      />
    </div>
  );
};
