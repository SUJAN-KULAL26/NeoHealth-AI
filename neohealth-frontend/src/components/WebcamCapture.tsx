import React, { useRef, useState, useEffect } from 'react';
import { Camera, RefreshCw, AlertTriangle } from 'lucide-react';

interface WebcamCaptureProps {
  onCapture: (imageSrc: string) => void;
  onError: (msg: string) => void;
}

export const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture, onError }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const startCamera = async () => {
    setCameraError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'environment' },
        audio: false,
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }
      setIsCameraActive(true);
    } catch (err) {
      console.warn('Camera access error or unsupported:', err);
      const msg = 'Camera access was denied or device has no active video source.';
      setCameraError(msg);
      onError(msg);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    setIsCameraActive(false);
  };

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const capturePhoto = () => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current || document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageSrc = canvas.toDataURL('image/jpeg', 0.92);
      stopCamera();
      onCapture(imageSrc);
    }
  };

  // Fallback demo capture generator if camera permissions are blocked
  const useSimulatedCameraScan = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 600;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      // Draw gradient skin texture
      const grad = ctx.createRadialGradient(300, 300, 50, 300, 300, 300);
      grad.addColorStop(0, '#fcd34d');
      grad.addColorStop(0.5, '#f59e0b');
      grad.addColorStop(1, '#b45309');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 600, 600);

      // Draw mole
      const moleGrad = ctx.createRadialGradient(300, 300, 5, 300, 300, 60);
      moleGrad.addColorStop(0, '#312e81');
      moleGrad.addColorStop(0.7, '#431407');
      moleGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = moleGrad;
      ctx.beginPath();
      ctx.arc(300, 300, 65, 0, Math.PI * 2);
      ctx.fill();

      onCapture(canvas.toDataURL('image/jpeg'));
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', alignItems: 'center' }}>
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: '560px',
        height: '360px',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        background: '#020617',
        border: '1px solid rgba(6, 182, 212, 0.3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 0 30px rgba(0, 0, 0, 0.8)',
      }}>
        {isCameraActive ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
            
            {/* Alignment Target Overlay */}
            <div style={{
              position: 'absolute',
              width: '180px',
              height: '180px',
              border: '2px dashed var(--accent-cyan)',
              borderRadius: '50%',
              boxShadow: '0 0 20px rgba(6, 182, 212, 0.5), inset 0 0 20px rgba(6, 182, 212, 0.2)',
              pointerEvents: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <div style={{ width: '10px', height: '10px', background: 'var(--accent-cyan)', borderRadius: '50%' }} />
            </div>

            <span style={{
              position: 'absolute',
              top: '1rem',
              left: '1rem',
              background: 'rgba(0, 0, 0, 0.65)',
              color: '#38bdf8',
              fontSize: '0.75rem',
              padding: '0.3rem 0.7rem',
              borderRadius: '999px',
              border: '1px solid rgba(6, 182, 212, 0.3)',
            }}>
              ● Live Camera Feed
            </span>
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <AlertTriangle size={40} color="var(--accent-amber)" style={{ marginBottom: '1rem' }} />
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Camera Stream Off or Blocked</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
              {cameraError || 'Allow camera permissions in your browser to capture live scans.'}
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <button onClick={startCamera} className="btn-secondary" style={{ fontSize: '0.85rem' }}>
                <RefreshCw size={14} /> Retry Camera
              </button>
              <button onClick={useSimulatedCameraScan} className="btn-primary" style={{ fontSize: '0.85rem' }}>
                <Camera size={14} /> Capture Simulated Scan
              </button>
            </div>
          </div>
        )}
      </div>

      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {isCameraActive && (
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={capturePhoto} className="btn-primary" style={{ padding: '0.85rem 2rem' }}>
            <Camera size={18} /> Capture Lesion Photo
          </button>
          <button onClick={stopCamera} className="btn-secondary">
            Stop Camera
          </button>
        </div>
      )}
    </div>
  );
};
