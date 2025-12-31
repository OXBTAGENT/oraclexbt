"""
OracleXBT Training System
Run the agent through various scenarios to test and improve responses
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from agent import PredictionMarketAgent

class OracleTrainer:
    """Training system for OracleXBT"""
    
    def __init__(self):
        self.agent = PredictionMarketAgent()
        self.training_results = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log_result(self, test_name: str, passed: bool, response: str, notes: str = ""):
        """Log a training result"""
        result = {
            "test": test_name,
            "passed": passed,
            "response": response[:200] + "..." if len(response) > 200 else response,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        self.training_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if notes:
            print(f"   Note: {notes}")
    
    def test_market_analysis(self):
        """Test market analysis capabilities"""
        print("\n📊 Testing Market Analysis...")
        
        scenarios = [
            {
                "name": "Election Market Analysis",
                "prompt": "Analyze the Trump 2024 election market. What does the data tell us?",
                "keywords": ["odds", "probability", "market", "price", "volume"]
            },
            {
                "name": "Crypto Market Analysis", 
                "prompt": "What do prediction markets show about Bitcoin hitting $100k?",
                "keywords": ["bitcoin", "btc", "price", "market"]
            },
            {
                "name": "Cross-Platform Comparison",
                "prompt": "Compare odds for Trump winning across Polymarket and Kalshi",
                "keywords": ["polymarket", "kalshi", "compare", "odds"]
            }
        ]
        
        for scenario in scenarios:
            response = self.agent.chat(scenario["prompt"])
            
            # Check if response includes key elements
            has_keywords = any(kw.lower() in response.lower() for kw in scenario["keywords"])
            has_numbers = any(char.isdigit() for char in response)
            is_substantive = len(response) > 50
            
            passed = has_keywords and has_numbers and is_substantive
            notes = f"Keywords: {has_keywords}, Numbers: {has_numbers}, Length: {len(response)}"
            
            self.log_result(scenario["name"], passed, response, notes)
    
    def test_arbitrage_detection(self):
        """Test arbitrage opportunity detection"""
        print("\n⚖️ Testing Arbitrage Detection...")
        
        scenarios = [
            {
                "name": "Find Arbitrage Opportunities",
                "prompt": "Search for arbitrage opportunities across all platforms right now",
                "expected_elements": ["platform", "price", "spread", "%"]
            },
            {
                "name": "Explain Arbitrage Risk",
                "prompt": "What are the risks in prediction market arbitrage?",
                "expected_elements": ["risk", "settlement", "liquidity", "fee"]
            }
        ]
        
        for scenario in scenarios:
            response = self.agent.chat(scenario["prompt"])
            
            has_elements = sum(1 for elem in scenario["expected_elements"] 
                             if elem.lower() in response.lower())
            
            passed = has_elements >= 2
            notes = f"Found {has_elements}/{len(scenario['expected_elements'])} expected elements"
            
            self.log_result(scenario["name"], passed, response, notes)
    
    def test_data_retrieval(self):
        """Test real-time data retrieval"""
        print("\n🔍 Testing Data Retrieval...")
        
        scenarios = [
            {
                "name": "Get Current Markets",
                "prompt": "What are the top 3 prediction markets by volume right now?",
                "should_use_tools": True
            },
            {
                "name": "Get Specific Market Data",
                "prompt": "Get the current odds for Trump winning the 2024 election on Polymarket",
                "should_use_tools": True
            },
            {
                "name": "Historical Price Data",
                "prompt": "Show me how Trump 2024 odds have changed in the past week",
                "should_use_tools": True
            }
        ]
        
        for scenario in scenarios:
            response = self.agent.chat(scenario["prompt"])
            
            # Check if agent used tools and got real data
            has_specific_numbers = any(char in response for char in ['%', '$', '¢'])
            has_data = len(response) > 100
            
            passed = has_specific_numbers and has_data
            notes = f"Has numbers: {has_specific_numbers}, Substantive: {has_data}"
            
            self.log_result(scenario["name"], passed, response, notes)
    
    def test_tweet_generation(self):
        """Test tweet generation without posting"""
        print("\n🐦 Testing Tweet Generation...")
        
        scenarios = [
            {
                "name": "Market Update Tweet",
                "prompt": "Compose a market update tweet about current Bitcoin prediction markets (don't post it, just show me)",
                "max_length": 280,
                "should_have": ["bitcoin", "market"]
            },
            {
                "name": "Analysis Tweet",
                "prompt": "Compose a tweet analyzing election market trends (don't post, just compose)",
                "max_length": 280,
                "should_have": ["election", "odds"]
            },
            {
                "name": "Data Share Tweet",
                "prompt": "Create a tweet sharing interesting prediction market data (don't post)",
                "max_length": 280,
                "should_have": ["%"]
            }
        ]
        
        for scenario in scenarios:
            response = self.agent.chat(scenario["prompt"])
            
            # Extract potential tweet text (look for quotes or short text)
            tweet_length = len(response) if len(response) < 300 else 280
            has_required = all(term.lower() in response.lower() for term in scenario["should_have"])
            no_hashtags = response.count('#') <= 1  # Allow max 1 hashtag
            
            passed = tweet_length <= 280 and has_required and no_hashtags
            notes = f"Length: {tweet_length}, Has required: {has_required}, Hashtags: {response.count('#')}"
            
            self.log_result(scenario["name"], passed, response, notes)
    
    def test_reply_generation(self):
        """Test intelligent reply generation"""
        print("\n💬 Testing Reply Generation...")
        
        scenarios = [
            {
                "name": "Reply to Market Discussion",
                "tweet": "Polymarket shows Trump at 65% to win. Thoughts?",
                "prompt": "Generate a reply to this tweet: 'Polymarket shows Trump at 65% to win. Thoughts?' (don't post, just compose)",
                "should_add_value": True
            },
            {
                "name": "Reply with Data",
                "tweet": "Prediction markets are looking interesting today",
                "prompt": "Generate a reply with specific data to: 'Prediction markets are looking interesting today' (don't post)",
                "should_add_value": True
            }
        ]
        
        for scenario in scenarios:
            response = self.agent.chat(scenario["prompt"])
            
            # Check if reply adds value
            has_numbers = any(char.isdigit() for char in response)
            is_professional = not any(word in response.lower() for word in ['awesome', 'amazing', 'wow', '!!!'])
            length_ok = 50 < len(response) < 280
            
            passed = has_numbers and is_professional and length_ok
            notes = f"Has data: {has_numbers}, Professional: {is_professional}, Length: {len(response)}"
            
            self.log_result(scenario["name"], passed, response, notes)
    
    def test_knowledge_application(self):
        """Test application of training knowledge"""
        print("\n🧠 Testing Knowledge Application...")
        
        scenarios = [
            {
                "name": "Identify Market Pattern",
                "prompt": "What pattern do you typically see in election markets as election day approaches?",
                "expected_concepts": ["volatility", "volume", "narrowing", "price"]
            },
            {
                "name": "Trading Strategy",
                "prompt": "Explain a mean reversion strategy in prediction markets",
                "expected_concepts": ["mean", "revert", "overreact", "return"]
            },
            {
                "name": "Platform Comparison",
                "prompt": "What are the key differences between Polymarket and Kalshi?",
                "expected_concepts": ["crypto", "cftc", "regulated", "liquidity"]
            }
        ]
        
        for scenario in scenarios:
            response = self.agent.chat(scenario["prompt"])
            
            concepts_found = sum(1 for concept in scenario["expected_concepts"]
                               if concept.lower() in response.lower())
            
            passed = concepts_found >= 2
            notes = f"Found {concepts_found}/{len(scenario['expected_concepts'])} expected concepts"
            
            self.log_result(scenario["name"], passed, response, notes)
    
    def test_error_handling(self):
        """Test handling of edge cases"""
        print("\n🛡️ Testing Error Handling...")
        
        scenarios = [
            {
                "name": "Unknown Market",
                "prompt": "What are the odds for the alien invasion in 2025?",
                "should_handle_gracefully": True
            },
            {
                "name": "Ambiguous Request",
                "prompt": "Tell me about markets",
                "should_ask_clarification": True
            }
        ]
        
        for scenario in scenarios:
            response = self.agent.chat(scenario["prompt"])
            
            # Should handle gracefully without errors
            handles_well = len(response) > 20 and ("not" in response.lower() or "?" in response)
            
            passed = handles_well
            notes = f"Handled gracefully: {handles_well}"
            
            self.log_result(scenario["name"], passed, response, notes)
    
    def run_full_training(self):
        """Run complete training suite"""
        print("=" * 60)
        print("🤖 OracleXBT Training Session")
        print(f"Session ID: {self.session_id}")
        print("=" * 60)
        
        # Run all tests
        self.test_market_analysis()
        self.test_arbitrage_detection()
        self.test_data_retrieval()
        self.test_tweet_generation()
        self.test_reply_generation()
        self.test_knowledge_application()
        self.test_error_handling()
        
        # Generate summary
        self.print_summary()
        
        # Save results
        self.save_results()
    
    def print_summary(self):
        """Print training summary"""
        print("\n" + "=" * 60)
        print("📊 Training Summary")
        print("=" * 60)
        
        total = len(self.training_results)
        passed = sum(1 for r in self.training_results if r["passed"])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed > 0:
            print("\n⚠️ Failed Tests:")
            for result in self.training_results:
                if not result["passed"]:
                    print(f"  • {result['test']}: {result['notes']}")
        
        print("\n" + "=" * 60)
        
        if passed / total >= 0.8:
            print("🎉 Training Results: EXCELLENT")
            print("Agent is performing well and ready for autonomous operation!")
        elif passed / total >= 0.6:
            print("✅ Training Results: GOOD")
            print("Agent is functional but could use some refinement.")
        else:
            print("⚠️ Training Results: NEEDS IMPROVEMENT")
            print("Consider reviewing failed tests and refining prompts.")
    
    def save_results(self):
        """Save training results to file"""
        filename = f"training_results_{self.session_id}.json"
        
        summary = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.training_results),
            "passed": sum(1 for r in self.training_results if r["passed"]),
            "failed": sum(1 for r in self.training_results if not r["passed"]),
            "results": self.training_results
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Run training"""
    trainer = OracleTrainer()
    trainer.run_full_training()

if __name__ == "__main__":
    main()
