export type RiskLevel = 'low' | 'moderate' | 'high' | 'uncertain';

export type DiseaseClass =
  | 'Jaundice'
  | 'Atopic Dermatitis'
  | 'Impetigo'
  | 'Cradle Cap'
  | 'Neonatal Acne'
  | 'Normal';

export interface ClassProbability {
  id: string;
  label: DiseaseClass;
  category: string; // Infant health condition | Skin condition | Bacterial skin infection | Infant scalp condition | Infant skin condition | Healthy/normal appearance
  probability: number; // 0 - 100
  riskLevel: RiskLevel;
  description: string;
}

export interface GradCAMData {
  originalImage: string;
  heatmapOverlay: string; // Base64 data URL or generated heat map
  regionsOfInterest: {
    x: number;
    y: number;
    radius: number;
    label: string;
    intensity: number; // 0 - 1
  }[];
  opacityDefault: number;
}

export interface Recommendation {
  id: string;
  title: string;
  detail: string;
  urgency: 'info' | 'warning' | 'urgent';
  actionText?: string;
}

export interface ScreeningResult {
  id: string;
  timestamp: string;
  primaryPrediction: DiseaseClass;
  category: string;
  confidenceScore: number; // 0 - 100
  riskLevel: RiskLevel;
  probabilities: ClassProbability[];
  gradCAM: GradCAMData;
  recommendations: Recommendation[];
  bodySite: string;
  patientNotes?: string;
  isUncertain: boolean;
  uncertaintyReason?: string;
  diagnosticSummary: string;
  clinicalSignificance: string;
}

export interface ScreeningInput {
  file?: File;
  imageSrc: string;
  source: 'upload' | 'webcam' | 'preset';
  presetCondition?: DiseaseClass;
  bodySite: string;
  patientNotes?: string;
  timestamp: string;
}

export type ScreeningStatus = 'idle' | 'input' | 'processing' | 'results' | 'uncertain' | 'error';

export interface ProcessingStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed';
  progress: number; // 0 - 100
}

export interface ScreeningHistoryItem {
  id: string;
  date: string;
  imageSrc: string;
  primaryPrediction: DiseaseClass;
  category: string;
  confidenceScore: number;
  riskLevel: RiskLevel;
  bodySite: string;
  result: ScreeningResult;
}
