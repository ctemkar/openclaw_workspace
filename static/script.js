// --- Status Update ---
function updateStatus() {
    fetch('/api/status/all')
        .then(response => {
            if (!response.ok) {
                console.error('Error fetching status:', response.status, response.statusText);
                // Optionally update UI to show error state
                const tradingStatusSpan = document.getElementById('tradingStatus');
                const llmStatusSpan = document.getElementById('llmStatus');
                if(tradingStatusSpan) tradingStatusSpan.textContent = 'API Error';
                if(llmStatusSpan) llmStatusSpan.textContent = 'API Error';
                return Promise.reject(response);
            }
            return response.json();
        })
        .then(data => {
            const tradingStatusSpan = document.getElementById('tradingStatus');
            const llmStatusSpan = document.getElementById('llmStatus');
            const tradingLogsTimestampSpan = document.getElementById('tradingLogsTimestamp'); // Assuming this exists for timestamp

            // Update trading status
            if (tradingStatusSpan) {
                const tradingInfo = data.trading || {};
                tradingStatusSpan.textContent = tradingInfo.status || 'N/A';
                // Update timestamp if available
                if (tradingInfo.last_update && tradingLogsTimestampSpan) {
                    try {
                        tradingLogsTimestampSpan.textContent = `Last update: ${new Date(tradingInfo.last_update).toLocaleString()}`;
                    } catch (e) {
                        console.error("Error formatting timestamp:", tradingInfo.last_update, e);
                        tradingLogsTimestampSpan.textContent = 'Last update: invalid date';
                    }
                }
            }

            // Update LLM status
            if (llmStatusSpan) {
                const llmInfo = data.llm_generator || {};
                llmStatusSpan.textContent = llmInfo.status || 'N/A';
                // Optionally update timestamp for LLM status if a span exists for it
                // const llmLogsTimestampSpan = document.getElementById('llmLogsTimestamp'); // Assuming this exists
                // if (llmInfo.last_update && llmLogsTimestampSpan) {
                //     llmLogsTimestampSpan.textContent = `Last update: ${new Date(llmInfo.last_update).toLocaleString()}`;
                // }
            }
        })
        .catch(error => {
            console.error('Error in updateStatus fetch:', error);
            // Display a global error message or reset status indicators
            const tradingStatusSpan = document.getElementById('tradingStatus');
            const llmStatusSpan = document.getElementById('llmStatus');
            if (tradingStatusSpan) tradingStatusSpan.textContent = 'Error';
            if (llmStatusSpan) llmStatusSpan.textContent = 'Error';
        });
}

// --- Trade Progress Update ---
function updateTradeProgress() {
    fetch('/api/trading/progress')
        .then(response => {
            if (!response.ok) {
                console.error('Error fetching trade progress:', response.status, response.statusText);
                return Promise.reject(response);
            }
            return response.json();
        })
        .then(data => {
            const tradesByStrategy = {};
            // Check if data contains trades and is an array
            if (data && data.trades && Array.isArray(data.trades) && data.trades.length > 0) {
                data.trades.forEach(trade => {
                    const strategyName = trade.strategy_name || 'Unknown Strategy';
                    if (!tradesByStrategy[strategyName]) {
                        tradesByStrategy[strategyName] = [];
                    }
                    tradesByStrategy[strategyName].push(trade);
                });
            }

            // Update the LLM strategies display to include trade progress
            const llmStrategiesContainer = document.getElementById('llmStrategiesContainer');
            // Clear existing strategies to re-render with progress
            llmStrategiesContainer.innerHTML = '<h4>Available Strategies & Trade Progress:</h4>';

            // Re-fetch strategies to combine with progress data
            fetch('/api/llm/strategies')
                .then(response => response.json())
                .then(strategies => {
                    if (strategies && strategies.length > 0) {
                        strategies.forEach(strategy => {
                            const strategyDiv = document.createElement('div');
                            strategyDiv.className = 'strategy-section'; // Added class for styling

                            let progressHtml = '<p><strong>Trade Progress:</strong> No active trades for this strategy.</p>';
                            const strategyName = strategy.strategy_name;
                            
                            if (tradesByStrategy[strategyName] && tradesByStrategy[strategyName].length > 0) {
                                progressHtml = '<h5>Active Trades:</h5>';
                                tradesByStrategy[strategyName].forEach(trade => {
                                    progressHtml += `
                                        <div class="trade-item">
                                            <strong>Symbol:</strong> ${trade.symbol || 'N/A'} | 
                                            <strong>Investment:</strong> $${trade.investment_usd?.toFixed(2) ?? 'N/A'} | 
                                            <strong>Status:</strong> ${trade.status || 'unknown'} | 
                                            <strong>P&L:</strong> $${trade.pnl_usd?.toFixed(2) ?? 'N/A'}
                                        </div>`;
                                });
                            }
                            
                            strategyDiv.innerHTML = `
                                <h4>${strategy.strategy_name} (${strategy.symbol})</h4>
                                <p><strong>LLM Provider:</strong> ${strategy.llm_provider || 'N/A'}</p>
                                <p><strong>Model:</strong> ${strategy.model || 'N/A'}</p>
                                <p><strong>Description:</strong> ${strategy.description}</p>
                                <p><strong>Risk:</strong> Stop Loss ${strategy.risk_parameters?.stop_loss_pct * 100?.toFixed(2)}%, Take Profit ${strategy.risk_parameters?.take_profit_pct * 100?.toFixed(2)}%</p>
                                <p><strong>Rationale:</strong> ${strategy.profit_rationale}</p>
                                ${progressHtml}
                            `;
                            llmStrategiesContainer.appendChild(strategyDiv);
                        });
                    } else {
                        llmStrategiesContainer.innerHTML += '<p>No strategies generated yet. Click "Generate LLM Strategies" to fetch them.</p>';
                    }
                })
                .catch(error => console.error('Error fetching LLM strategies after progress update:', error));
        })
        .catch(error => {
            console.error('Error fetching trade progress:', error);
            // Display an error message if progress cannot be fetched
            document.getElementById('llmStrategiesContainer').innerHTML = '<h4>Available Strategies & Trade Progress:</h4><p>Could not load trade progress. Please check console for errors.</p>';
        });
}

// --- Initial Load and Periodic Updates ---
document.addEventListener('DOMContentLoaded', () => {
    const tradingStatusSpan = document.getElementById('tradingStatus');
    const llmStatusSpan = document.getElementById('llmStatus');
    const tradingLogsPre = document.getElementById('tradingLogs');
    const llmLogsPre = document.getElementById('llmLogs');
    const statusUpdatesPre = document.getElementById('statusUpdates'); // Assuming this exists for general status updates
    const tradingLogsTimestampSpan = document.getElementById('tradingLogsTimestamp'); // Assuming this exists for timestamp

    const startTradingBtn = document.getElementById('startTradingBtn');
    const stopTradingBtn = document.getElementById('stopTradingBtn');
    const generateLlmStrategiesBtn = document.getElementById('generateLlmStrategiesBtn'); // Assuming this exists

    // --- Status Update Function (NOW DEFINED) ---
    if (!window.updateStatus) { // Define updateStatus only if it doesn't exist globally
        window.updateStatus = function() {
            fetch('/api/status/all')
                .then(response => {
                    if (!response.ok) {
                        console.error('Error fetching status:', response.status, response.statusText);
                        // Optionally update UI to show error state
                        if(tradingStatusSpan) tradingStatusSpan.textContent = 'API Error';
                        if(llmStatusSpan) llmStatusSpan.textContent = 'API Error';
                        return Promise.reject(response);
                    }
                    return response.json();
                })
                .then(data => {
                    // Update trading status
                    if (tradingStatusSpan) {
                        const tradingInfo = data.trading || {};
                        tradingStatusSpan.textContent = tradingInfo.status || 'N/A';
                        // Update timestamp if available
                        if (tradingInfo.last_update && tradingLogsTimestampSpan) {
                            try {
                                // Directly use the date string, assume it's ISO format
                                tradingLogsTimestampSpan.textContent = `Last update: ${new Date(tradingInfo.last_update).toLocaleString()}`;
                            } catch (e) {
                                console.error("Error formatting timestamp:", tradingInfo.last_update, e);
                                tradingLogsTimestampSpan.textContent = 'Last update: invalid date';
                            }
                        }
                    }

                    // Update LLM status
                    if (llmStatusSpan) {
                        const llmInfo = data.llm_generator || {};
                        llmStatusSpan.textContent = llmInfo.status || 'N/A';
                        // Optionally update timestamp for LLM status if a span exists for it
                        // const llmLogsTimestampSpan = document.getElementById('llmLogsTimestamp');
                        // if (llmInfo.last_update && llmLogsTimestampSpan) {
                        //     llmLogsTimestampSpan.textContent = `Last update: ${new Date(llmInfo.last_update).toLocaleString()}`;
                        // }
                    }
                })
                .catch(error => {
                    console.error('Error in updateStatus fetch:', error);
                    // Display a global error message or reset status indicators
                    if(tradingStatusSpan) tradingStatusSpan.textContent = 'Error';
                    if(llmStatusSpan) llmStatusSpan.textContent = 'Error';
                });
        }
    }

    // --- LLM Strategies Update (modified to combine with progress) ---
    function updateStrategiesAndProgress() {
        updateTradeProgress(); // This function now handles fetching and displaying strategies with their progress
    }

    // --- Event Listeners ---
    if (startTradingBtn) {
        startTradingBtn.addEventListener('click', () => {
            fetch('/api/trading/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => console.log('Start trading response:', data))
                .catch(error => console.error('Error starting trading:', error));
        });
    }
    if (stopTradingBtn) {
        stopTradingBtn.addEventListener('click', () => {
            fetch('/api/trading/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => console.log('Stop trading response:', data))
                .catch(error => console.error('Error stopping trading:', error));
        });
    }
    if (generateLlmStrategiesBtn) {
        generateLlmStrategiesBtn.addEventListener('click', updateStrategiesAndProgress);
    }

    // --- Initial Load ---
    updateStatus(); // Call the defined updateStatus function
    // updateLogs(); // Assuming these functions exist elsewhere or are not critical initially
    // updateMarketData();
    updateStrategiesAndProgress(); // Call the combined function for initial load

    // --- Auto-refresh data periodically ---
    setInterval(updateStatus, 5000); // Refresh status every 5 seconds
    // setInterval(updateLogs, 10000);
    // setInterval(updateMarketData, 30000);
    setInterval(updateStrategiesAndProgress, 60000); // Refresh strategies and progress every minute

    // ... (rest of the existing code, potentially including chart rendering if Chart.js is used) ...
});

// Placeholder for Chart.js if needed
if (typeof Chart === 'undefined') {
    console.warn("Chart.js not found. Charts will not be rendered.");
}

// Define updateLogs, updateMarketData if they exist and are needed for initial load/intervals
function updateLogs() {
    // Placeholder: Implement fetching and displaying logs
    console.log("updateLogs called");
}

function updateMarketData() {
    // Placeholder: Implement fetching and displaying market data
    console.log("updateMarketData called");
}
