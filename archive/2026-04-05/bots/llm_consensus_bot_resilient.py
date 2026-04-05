#!/usr/bin/env python3
"""
RESILIENT LLM CONSENSUS BOT
With circuit breakers, graceful degradation, and better error handling
"""

import os
import json
import time
import requests
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Tuple
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'llm_resilient.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================================================
# CIRCUIT BREAKER PATTERN
# ================================================

class CircuitBreaker:
    """Circuit breaker for API calls"""
    
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
        
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"🚨 Circuit breaker OPENED after {self.failure_count} failures")
        
    def can_execute(self) -> bool:
        """Check if call can be executed"""
        if self.state == 'CLOSED':
            return True
            
        if self.state == 'OPEN':
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                if time_since_failure > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    logger.info("🔄 Circuit breaker HALF-OPEN (testing recovery)")
                    return True
            return False
            
        if self.state == 'HALF_OPEN':
            return True
            
        return False

# ================================================
# RESILIENT LLM QUERY
# ================================================

class ResilientLLMQuery:
    """Resilient LLM query with fallbacks and timeouts"""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=120)
        self.model_status = {}  # Track model health
        self.last_successful_model = None
        
    def query_with_resilience(self, model: str, prompt: str, max_retries: int = 2) -> Optional[Dict]:
        """Query LLM with resilience patterns"""
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning(f"⏸️ Circuit breaker blocking query to {model}")
            return None
        
        # Try primary model
        response = self._try_query(model, prompt, max_retries)
        
        if response:
            self.circuit_breaker.record_success()
            self.model_status[model] = 'healthy'
            self.last_successful_model = model
            return response
        
        # Primary model failed, try fallback
        logger.warning(f"⚠️ Primary model {model} failed, trying fallback...")
        fallback_model = self._get_fallback_model(model)
        
        if fallback_model:
            response = self._try_query(fallback_model, prompt, max_retries=1)
            if response:
                logger.info(f"✅ Fallback model {fallback_model} succeeded")
                self.model_status[model] = 'unavailable'
                self.model_status[fallback_model] = 'healthy'
                return response
        
        # All models failed
        self.circuit_breaker.record_failure()
        self.model_status[model] = 'failed'
        logger.error(f"❌ All models failed for query")
        return None
    
    def _try_query(self, model: str, prompt: str, max_retries: int) -> Optional[Dict]:
        """Try query with retries"""
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Retry {attempt}/{max_retries} for {model}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                
                response = self._query_ollama(model, prompt)
                if response:
                    return response
                    
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt} failed for {model}: {e}")
        
        return None
    
    def _query_ollama(self, model: str, prompt: str) -> Optional[Dict]:
        """Query Ollama with timeout"""
        try:
            # Check if model is available
            tags_response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if tags_response.status_code != 200:
                logger.warning("⚠️ Ollama server not responding")
                return None
            
            models = [m['name'] for m in tags_response.json().get('models', [])]
            if model not in models:
                logger.warning(f"⚠️ Model {model} not available in Ollama")
                return None
            
            # Query with timeout
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': 150
                    }
                },
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Ollama API error for {model}: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Timeout querying {model}")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"🔌 Connection error to Ollama for {model}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Error querying {model}: {e}")
            return None
    
    def _get_fallback_model(self, primary_model: str) -> Optional[str]:
        """Get fallback model for primary"""
        fallback_map = {
            'deepseek-r1:latest': 'mistral:latest',
            'qwen2.5-coder:32b': 'llama3.1:latest',
            'glm-4.7-flash:latest': 'llama3:latest',
            'mistral:latest': 'llama3.1:8b',
            'llama3.1:latest': 'llama3:latest',
            'llama3:latest': 'llama3.1:8b',
            'qwen3:latest': 'mistral:latest'
        }
        return fallback_map.get(primary_model)

# ================================================
# GRACEFUL DEGRADATION
# ================================================

class GracefulTradingSystem:
    """Trading system with graceful degradation"""
    
    def __init__(self):
        self.mode = 'FULL'  # FULL, DEGRADED, MINIMAL
        self.degradation_reasons = []
        self.last_mode_change = datetime.now()
        
    def assess_system_health(self) -> str:
        """Assess system health and adjust mode"""
        old_mode = self.mode
        
        # Check Ollama health
        ollama_healthy = self._check_ollama_health()
        
        # Check model availability
        available_models = self._get_available_models()
        
        # Determine mode
        if not ollama_healthy or len(available_models) < 3:
            self.mode = 'MINIMAL'
            self.degradation_reasons = ['LLM service unavailable']
            logger.warning("🟡 System degraded to MINIMAL mode")
        elif len(available_models) < 5:
            self.mode = 'DEGRADED'
            self.degradation_reasons = [f'Only {len(available_models)} models available']
            logger.info("🟡 System in DEGRADED mode")
        else:
            self.mode = 'FULL'
            self.degradation_reasons = []
            logger.info("🟢 System in FULL mode")
        
        # Log mode change
        if old_mode != self.mode:
            self.last_mode_change = datetime.now()
            logger.info(f"🔄 Mode changed: {old_mode} → {self.mode}")
            if self.degradation_reasons:
                logger.info(f"   Reasons: {', '.join(self.degradation_reasons)}")
        
        return self.mode
    
    def _check_ollama_health(self) -> bool:
        """Check if Ollama is healthy"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
        except:
            pass
        return []
    
    def get_trading_decision(self, analysis_results: Dict) -> Dict:
        """Get trading decision based on current mode"""
        if self.mode == 'FULL':
            return self._full_mode_decision(analysis_results)
        elif self.mode == 'DEGRADED':
            return self._degraded_mode_decision(analysis_results)
        else:  # MINIMAL
            return self._minimal_mode_decision(analysis_results)
    
    def _full_mode_decision(self, analysis: Dict) -> Dict:
        """Full mode: Use all models with CIO analysis"""
        # This would integrate with the existing CIO logic
        return {
            'signal': analysis.get('signal', 'HOLD'),
            'confidence': analysis.get('confidence', 0.5),
            'mode': 'FULL',
            'models_used': analysis.get('models_used', 0),
            'notes': 'Full LLM consensus analysis'
        }
    
    def _degraded_mode_decision(self, analysis: Dict) -> Dict:
        """Degraded mode: Conservative decisions"""
        signal = analysis.get('signal', 'HOLD')
        confidence = analysis.get('confidence', 0.5)
        
        # Be more conservative in degraded mode
        if signal == 'BUY' and confidence < 0.7:
            signal = 'HOLD'
            confidence = 0.5
        
        return {
            'signal': signal,
            'confidence': confidence * 0.8,  # Reduce confidence
            'mode': 'DEGRADED',
            'models_used': analysis.get('models_used', 0),
            'notes': 'Conservative mode: Reduced confidence'
        }
    
    def _minimal_mode_decision(self, analysis: Dict) -> Dict:
        """Minimal mode: Very conservative or no trading"""
        # In minimal mode, only trade with very high confidence
        signal = analysis.get('signal', 'HOLD')
        confidence = analysis.get('confidence', 0.5)
        
        if confidence < 0.8:
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'mode': 'MINIMAL',
            'models_used': analysis.get('models_used', 0),
            'notes': 'Minimal mode: Trading limited'
        }

# ================================================
# MAIN RESILIENT BOT
# ================================================

class ResilientLLMConsensusBot:
    """Main resilient bot class"""
    
    def __init__(self):
        self.resilient_query = ResilientLLMQuery()
        self.graceful_system = GracefulTradingSystem()
        self.cycle_count = 0
        self.last_analysis_time = None
        
        # Configuration
        self.SCAN_INTERVAL = 600  # 10 minutes
        self.CRYPTOS = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT']
        
        # Models to use (prioritized)
        self.MODELS = [
            'mistral:latest',      # Reliable
            'llama3.1:latest',     # Reliable  
            'llama3:latest',       # Reliable
            'deepseek-r1:latest',  # May fail
            'qwen3:latest',        # May fail
        ]
    
    def run(self):
        """Main bot loop"""
        logger.info("="*70)
        logger.info("🛡️ RESILIENT LLM CONSENSUS BOT STARTING")
        logger.info("="*70)
        
        while True:
            self.cycle_count += 1
            cycle_start = datetime.now()
            
            logger.info(f"\n🔄 CYCLE {self.cycle_count} - {cycle_start.strftime('%H:%M:%S')}")
            logger.info("-" * 50)
            
            try:
                # Assess system health
                mode = self.graceful_system.assess_system_health()
                logger.info(f"📊 System Mode: {mode}")
                
                if mode == 'MINIMAL':
                    logger.warning("⚠️ System in MINIMAL mode - limited functionality")
                    # Skip analysis, just wait
                    time.sleep(self.SCAN_INTERVAL)
                    continue
                
                # Get market data
                market_data = self._get_market_data()
                if not market_data:
                    logger.warning("⚠️ No market data available")
                    time.sleep(self.SCAN_INTERVAL)
                    continue
                
                # Analyze each crypto
                for crypto in self.CRYPTOS:
                    if crypto in market_data:
                        self._analyze_crypto(crypto, market_data[crypto])
                
                self.last_analysis_time = datetime.now()
                
                # Calculate sleep time
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(10, self.SCAN_INTERVAL - cycle_duration)
                
                logger.info(f"✅ Cycle completed in {cycle_duration:.1f}s")
                logger.info(f"⏰ Next cycle in {sleep_time:.0f}s")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Cycle error: {e}")
                time.sleep(60)  # Wait before retry
    
    def _get_market_data(self) -> Dict:
        """Get market data from Binance"""
        try:
            # Simple price fetching
            # In production, use ccxt or API
            return {
                'BTC': {'price': 66000 + random.uniform(-1000, 1000), 'change': random.uniform(-5, 5)},
                'ETH': {'price': 2000 + random.uniform(-100, 100), 'change': random.uniform(-5, 5)},
                'SOL': {'price': 80 + random.uniform(-5, 5), 'change': random.uniform(-5, 5)},
                'ADA': {'price': 0.25 + random.uniform(-0.02, 0.02), 'change': random.uniform(-5, 5)},
                'DOT': {'price': 1.2 + random.uniform(-0.1, 0.1), 'change': random.uniform(-5, 5)},
            }
        except:
            return {}
    
    def _analyze_crypto(self, crypto: str, data: Dict):
        """Analyze a single cryptocurrency"""
        price = data.get('price', 0)
        change = data.get('change', 0)
        
        logger.info(f"🔍 Analyzing {crypto}: ${price:.2f} ({change:+.1f}%)")
        
        # Create analysis prompt
        prompt = f"""Analyze {crypto} (Bitcoin) for trading. Current price: ${price:.2f}, 24h change: {change:+.1f}%.
        
Provide analysis in this exact format:
BUY_SCORE: [1-10]
SELL_SCORE: [1-10]
COMMENT: [Brief analysis mentioning if bullish/bearish/neutral]

Example:
BUY_SCORE: 7
SELL_SCORE: 3
COMMENT: Bullish trend with strong support at $65,000."""
        
        # Query models
        model_results = []
        successful_models = 0
        
        for model in self.MODELS:
            if successful_models >= 3:  # Limit to 3 models in degraded mode
                break
                
            result = self.resilient_query.query_with_resilience(model, prompt)
            if result:
                successful_models += 1
                analysis = self._parse_response(result.get('response', ''))
                if analysis:
                    model_results.append({
                        'model': model,
                        'buy_score': analysis['buy_score'],
                        'sell_score': analysis['sell_score'],
                        'comment': analysis['comment']
                    })
        
        if not model_results:
            logger.warning(f"   ⚠️ No model responses for {crypto}")
            return
        
        # Calculate consensus
        avg_buy = np.mean([r['buy_score'] for r in model_results])
        avg_sell = np.mean([r['sell_score'] for r in model_results])
        
        signal = 'HOLD'
        if avg_buy - avg_sell > 2:
            signal = 'BUY'
        elif avg_sell - avg_buy > 2:
            signal = 'SELL'
        
        confidence = min(0.99, abs(avg_buy - avg_sell) / 10)
        
        # Get trading decision based on system mode
        analysis_data = {
            'signal': signal,
            'confidence': confidence,
            'models_used': len(model_results),
            'avg_buy': avg_buy,
            'avg_sell': avg_sell
        }
        
        decision = self.graceful_system.get_trading_decision(analysis_data)
        
        # Log decision
        status_symbol = "🟢" if decision['signal'] == 'BUY' else "🔴" if decision['signal'] == 'SELL' else "🟡"
        logger.info(f"   {status_symbol} Decision: {decision['signal']} (Confidence: {decision['confidence']:.2f})")
        logger.info(f"   Mode: {decision['mode']}, Models: {decision['models_used']}")
        
        # Save decision
        self._save_decision(crypto, price, decision, model_results)
    
    def _parse_response(self, response: str) -> Optional[Dict]:
        """Parse LLM response"""
        try:
            lines = response.strip().split('\n')
            buy_score = 5
            sell_score = 5
            comment = "No analysis"
            
            for line in lines:
                line = line.strip()
                if line.startswith('BUY_SCORE:'):
                    try:
                        buy_score = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('SELL_SCORE:'):
                    try:
                        sell_score = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('COMMENT:'):
                    comment = line.split(':', 1)[1].strip()
            
            # Validate scores
            buy_score = max(1, min(10, buy_score))
            sell_score = max(1, min(10, sell_score))
            
            return {
                'buy_score': buy_score,
                'sell_score': sell_score,
                'comment': comment
            }
        except:
            return None
    
    def _save_decision(self, crypto: str, price: float, decision: Dict, model_results: List):
        """Save decision to file"""
        try:
            decision_file = os.path.join(BASE_DIR, 'resilient_decisions.json')
            
            # Load existing decisions
            if os.path.exists(decision_file):
                with open(decision_file, 'r') as f:
                    decisions = json.load(f)
            else:
                decisions = []
            
            # Add new decision
            decision_record = {
                'crypto': crypto,
                'timestamp': datetime.now().isoformat(),
                'price': price,
                'signal': decision['signal'],
                'confidence': decision['confidence'],
                'mode': decision['mode'],
                'models_used': decision['models_used'],
                'model_results': model_results
            }
            
            decisions.append(decision_record)
            
            # Keep only last 100 decisions
            if len(decisions) > 100:
                decisions = decisions[-100:]
            
            with open(decision_file, 'w') as f:
                json.dump(decisions, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving decision: {e}")

# ================================================
# MAIN EXECUTION
# ================================================

if __name__ == "__main__":
    bot = ResilientLLMConsensusBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Resilient bot stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()