"""
🎯 EXAMPLE: Budget-Configurable AI Agent Usage
Shows how to set budget via chat and run the AI agent
"""

import asyncio
from backend.budget_configurable_orchestrator import budget_orchestrator

async def example_chat_budget_configuration():
    """
    Example of setting budget through chat interface
    """
    print("🎯 BUDGET-CONFIGURABLE AI AGENT EXAMPLE")
    print("=" * 50)
    
    # Example 1: User sets basic budget
    print("\n💬 User: 'Set my AI budget to $75 per month'")
    result = await budget_orchestrator.configure_budget_via_chat(75.0)
    print(f"🤖 AI Agent Response:")
    print(f"   {result['message']}")
    print(f"   Intelligence Level: {result['intelligence_level']}")
    print(f"   Features Enabled: {len(result['enabled_features'])} features")
    print(f"   Expected Improvement: {result['expected_performance_improvement']}")
    
    # Example 2: User asks for budget recommendation
    print("\n💬 User: 'What budget do I need to become #1 spiritual guru?'")
    recommendation = await budget_orchestrator.get_budget_recommendation_via_chat(
        "What budget do I need to become #1 spiritual guru?"
    )
    print(f"🤖 AI Agent Response:\n{recommendation}")
    
    # Example 3: User sets higher budget
    print("\n💬 User: 'Set my budget to $250 per month'")
    result = await budget_orchestrator.configure_budget_via_chat(250.0)
    print(f"🤖 AI Agent Response:")
    print(f"   {result['message']}")
    print(f"   Intelligence Level: {result['intelligence_level']}")
    print(f"   Features Enabled: {len(result['enabled_features'])} features")
    
    return result

async def example_ai_agent_operation():
    """
    Example of daily AI agent operation with budget constraints
    """
    print("\n🚀 DAILY AI AGENT OPERATION")
    print("=" * 50)
    
    # Run daily orchestration
    print("Running daily AI orchestration with budget constraints...")
    result = await budget_orchestrator.orchestrate_with_budget_constraints()
    
    print(f"\n📊 ORCHESTRATION RESULTS:")
    print(f"   Status: {result['orchestration_status']}")
    print(f"   Intelligence Level: {result['intelligence_level']}")
    print(f"   Budget Used: ${result['budget_used']:.2f}")
    print(f"   Budget Remaining: ${result['budget_remaining']:.2f}")
    
    print(f"\n🧠 AI INTELLIGENCE GATHERED:")
    intelligence = result['market_intelligence']
    for key, value in intelligence.items():
        print(f"   {key}: {value}")
    
    print(f"\n📋 AI STRATEGY CREATED:")
    strategy = result['daily_strategy']
    for key, value in strategy.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 AI RECOMMENDATIONS:")
    for rec in result['ai_recommendations']:
        print(f"   • {rec}")
    
    print(f"\n⏭️ NEXT STRATEGIC ACTIONS:")
    for action in result['next_actions']:
        print(f"   • {action}")
    
    return result

async def example_budget_comparison():
    """
    Example showing different capabilities at different budget levels
    """
    print("\n💰 BUDGET LEVEL COMPARISON")
    print("=" * 50)
    
    budgets_to_test = [60, 150, 280, 450]
    
    for budget in budgets_to_test:
        print(f"\n💰 Testing Budget: ${budget}/month")
        result = await budget_orchestrator.configure_budget_via_chat(budget)
        capabilities = result['capabilities']
        
        print(f"   Intelligence Level: {result['intelligence_level']}")
        print(f"   Expected Improvement: {capabilities['automation_enhancement']}")
        print(f"   Strategic Thinking: {capabilities['strategic_thinking']}")
        print(f"   Decision Making: {capabilities['decision_making']}")
        print(f"   Limitations: {', '.join(capabilities.get('limitations', ['None']))}")

async def main():
    """
    Main example execution
    """
    print("🎯 BUDGET-CONFIGURABLE AI AGENT DEMONSTRATION")
    print("🧠 Shows how AI agent works at any budget level")
    print("💬 Includes chat interface examples")
    print("\n" + "=" * 60)
    
    try:
        # Example 1: Chat-based budget configuration
        await example_chat_budget_configuration()
        
        # Example 2: Daily AI agent operation
        await example_ai_agent_operation()
        
        # Example 3: Budget level comparison
        await example_budget_comparison()
        
        print("\n" + "=" * 60)
        print("✅ DEMONSTRATION COMPLETE")
        print("\n🎯 KEY TAKEAWAYS:")
        print("   • AI agent works strategically at ANY budget level")
        print("   • Chat interface makes budget configuration simple")
        print("   • Intelligence scales with budget, but always provides strategic thinking")
        print("   • Integrates with existing automation without duplication")
        print("   • Real performance improvements from day 1")
        
        print("\n💬 READY TO SET YOUR BUDGET?")
        print("   Just say: 'Set my AI budget to $X per month'")
        print("   Or ask: 'What budget do I need for [your goal]?'")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())