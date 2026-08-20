import { useScreening } from './hooks/useScreening';
import { Navbar } from './components/Navbar';
import { Home } from './pages/Home';
import { Screening } from './pages/Screening';
import { Processing } from './pages/Processing';
import { Results } from './pages/Results';
import { UncertainResult } from './pages/UncertainResult';
import { History } from './pages/History';

export function App() {
  const {
    activePage,
    setActivePage,
    input,
    result,
    error,
    setError,
    processingStep,
    processingLabel,
    progress,
    history,
    setImageInput,
    startAnalysis,
    resetScreening,
    loadHistoryItem,
    removeHistoryItem,
    clearAllHistory,
  } = useScreening();

  const handleStartNewScreening = () => {
    resetScreening();
    setActivePage('screening');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Navigation Shell */}
      <Navbar
        activePage={activePage}
        onNavigate={(page) => setActivePage(page)}
        onNewScreening={handleStartNewScreening}
        historyCount={history.length}
      />

      {/* Main Page Container */}
      <main style={{ flex: 1, maxWidth: '1280px', width: '100%', margin: '0 auto', padding: '2rem 1.5rem' }}>
        {activePage === 'home' && (
          <Home
            onStartScreening={handleStartNewScreening}
            onViewHistory={() => setActivePage('history')}
          />
        )}

        {activePage === 'screening' && (
          <Screening
            input={input}
            error={error}
            onSetImageInput={setImageInput}
            onConfirmAndStart={(bodySite, notes) => {
              startAnalysis(bodySite, notes);
            }}
            onCancelInput={() => resetScreening()}
            onDismissError={() => setError(null)}
            onNavigateHome={() => setActivePage('home')}
          />
        )}

        {activePage === 'processing' && (
          <Processing
            progress={progress}
            processingStep={processingStep}
            processingLabel={processingLabel}
          />
        )}

        {activePage === 'results' && result && (
          <Results
            result={result}
            onNewScreening={handleStartNewScreening}
            onNavigateHome={() => setActivePage('home')}
          />
        )}

        {activePage === 'uncertain' && result && (
          <UncertainResult
            result={result}
            onRetake={handleStartNewScreening}
            onNavigateHome={() => setActivePage('home')}
          />
        )}

        {activePage === 'history' && (
          <History
            history={history}
            onSelectHistoryItem={(item) => loadHistoryItem(item)}
            onDeleteItem={(id) => removeHistoryItem(id)}
            onClearAll={clearAllHistory}
            onNewScreening={handleStartNewScreening}
          />
        )}
      </main>

      {/* Global Footer */}
      <footer style={{
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        background: 'rgba(7, 10, 18, 0.95)',
        padding: '1.5rem 2rem',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-subtle)',
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            © {new Date().getFullYear()} NeoHealth AI. Clinical Decision Support System.
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <span>Privacy Policy</span>
            <span>Clinical Model Spec</span>
            <span>Terms of Use</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
