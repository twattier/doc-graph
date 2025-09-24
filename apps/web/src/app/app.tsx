import { Route, Routes } from 'react-router-dom';
import { HomePage } from '../pages/HomePage';
import { Layout } from '../components/Layout';

export function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/about"
          element={
            <div className="p-8">
              <h1 className="text-2xl font-bold mb-4">About DocGraph</h1>
              <p>
                DocGraph is an AI-powered document insight engine that helps you
                extract knowledge from your documents.
              </p>
            </div>
          }
        />
      </Routes>
    </Layout>
  );
}

export default App;
