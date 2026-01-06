import React from 'react';
import { StockProvider } from './context/StockContext';
import { useStock } from "./context/StockContext";
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';



function App() {
    return (
        <StockProvider>
            <Layout>
                <Dashboard />
            </Layout>
        </StockProvider>
    );
}

export default App;
