import type { RiskLevel } from '../types/screening';

export interface ValidationResult {
  isValid: boolean;
  error?: string;
  warning?: string;
}

export const MAX_FILE_SIZE_MB = 15;
export const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp'];

/**
 * Validates medical image file size, format, and type.
 */
export function validateImageFile(file: File): ValidationResult {
  if (!file) {
    return { isValid: false, error: 'No image file selected.' };
  }

  if (!ALLOWED_FILE_TYPES.includes(file.type.toLowerCase())) {
    return {
      isValid: false,
      error: `Unsupported file format (${file.type || 'unknown'}). Please upload JPEG, PNG, or WebP medical images.`,
    };
  }

  const fileSizeMb = file.size / (1024 * 1024);
  if (fileSizeMb > MAX_FILE_SIZE_MB) {
    return {
      isValid: false,
      error: `File size exceeds ${MAX_FILE_SIZE_MB}MB limit (Current: ${fileSizeMb.toFixed(1)}MB). Please choose a smaller image.`,
    };
  }

  if (fileSizeMb < 0.01) {
    return {
      isValid: false,
      error: 'File appears to be corrupted or empty (0 KB).',
    };
  }

  return { isValid: true };
}

/**
 * Formats percentage value cleanly.
 */
export function formatPercentage(value: number): string {
  return `${Math.min(100, Math.max(0, Math.round(value)))}%`;
}

/**
 * Formats timestamp into readable medical report date format.
 */
export function formatDate(timestamp: string | Date): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  if (isNaN(date.getTime())) return 'Invalid Date';
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date);
}

/**
 * Returns color hex for given risk level.
 */
export function getRiskColor(risk: RiskLevel): string {
  switch (risk) {
    case 'low':
      return '#10b981'; // Emerald Green
    case 'moderate':
      return '#f59e0b'; // Amber / Orange
    case 'high':
      return '#ef4444'; // Red
    case 'uncertain':
      return '#a855f7'; // Purple / Violet
    default:
      return '#6b7280';
  }
}

/**
 * Generates an interactive Grad-CAM heatmap overlay onto a canvas from an input image URL.
 */
export function generateMockHeatmap(imageSrc: string): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width || 600;
      canvas.height = img.height || 600;
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        resolve(imageSrc);
        return;
      }

      // Draw original image first as base
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Create a transparent overlay canvas for activation heatmap
      const overlayCanvas = document.createElement('canvas');
      overlayCanvas.width = canvas.width;
      overlayCanvas.height = canvas.height;
      const oCtx = overlayCanvas.getContext('2d');

      if (oCtx) {
        const cx = canvas.width * 0.48;
        const cy = canvas.height * 0.52;
        const r1 = Math.min(canvas.width, canvas.height) * 0.35;

        // Primary hot spot (Red/Yellow activation region)
        const radGrad1 = oCtx.createRadialGradient(cx, cy, 0, cx, cy, r1);
        radGrad1.addColorStop(0, 'rgba(255, 0, 0, 0.9)');
        radGrad1.addColorStop(0.3, 'rgba(255, 120, 0, 0.8)');
        radGrad1.addColorStop(0.6, 'rgba(255, 230, 0, 0.6)');
        radGrad1.addColorStop(0.85, 'rgba(0, 220, 255, 0.35)');
        radGrad1.addColorStop(1, 'rgba(0, 50, 255, 0)');

        oCtx.fillStyle = radGrad1;
        oCtx.beginPath();
        oCtx.arc(cx, cy, r1, 0, Math.PI * 2);
        oCtx.fill();

        // Secondary focus spot
        const cx2 = canvas.width * 0.62;
        const cy2 = canvas.height * 0.38;
        const r2 = Math.min(canvas.width, canvas.height) * 0.2;

        const radGrad2 = oCtx.createRadialGradient(cx2, cy2, 0, cx2, cy2, r2);
        radGrad2.addColorStop(0, 'rgba(255, 0, 80, 0.85)');
        radGrad2.addColorStop(0.4, 'rgba(255, 180, 0, 0.7)');
        radGrad2.addColorStop(1, 'rgba(0, 200, 200, 0)');

        oCtx.fillStyle = radGrad2;
        oCtx.beginPath();
        oCtx.arc(cx2, cy2, r2, 0, Math.PI * 2);
        oCtx.fill();

        // Blend overlay onto main canvas
        ctx.globalAlpha = 0.85;
        ctx.drawImage(overlayCanvas, 0, 0);
      }

      resolve(canvas.toDataURL('image/png'));
    };

    img.onerror = () => {
      resolve(imageSrc);
    };

    img.src = imageSrc;
  });
}
