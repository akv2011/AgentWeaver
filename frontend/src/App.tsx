import Hero from './components/Hero';
import AgentCards from './components/AgentCards';
import LiveTimeline from './components/LiveTimeline';
import About from './components/About';
import Footer from './components/Footer';
import { useWorkflowStream } from './hooks/useWorkflowStream';

export default function App() {
  const { connection, agents, timeline, progress, isRunning, completionTime } = useWorkflowStream();

  function handleWorkflowStarted() {
    // The WS stream will pick up the events automatically.
    // This callback exists for future extension (e.g. scroll to timeline).
  }

  return (
    <main>
      <Hero
        connectionState={connection}
        onWorkflowStarted={handleWorkflowStarted}
      />

      <AgentCards agents={agents} />

      <LiveTimeline
        timeline={timeline}
        progress={progress}
        isRunning={isRunning}
        completionTime={completionTime}
      />

      <About />

      <Footer />
    </main>
  );
}
