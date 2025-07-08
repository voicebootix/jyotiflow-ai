"""
🎯 EXAMPLE: Budget-Intelligent AI Agent Usage
Shows how AI does EVERYTHING possible within your budget - no artificial limitations
"""

import asyncio
from backend.budget_intelligent_orchestrator import budget_intelligent_orchestrator

async def example_budget_intelligent_configuration():
    """
    Example of budget-intelligent configuration through chat interface
    """
    print("🎯 BUDGET-INTELLIGENT AI AGENT EXAMPLE")
    print("=" * 50)
    
    # Example 1: AI Intelligence only budget
    print("\n💬 User: 'Set my AI budget to $100 per month, this is for AI intelligence only'")
    result = await budget_intelligent_orchestrator.configure_budget_via_chat(
        monthly_budget=100.0,
        budget_includes_ads=False
    )
    print(f"🤖 AI Agent Response:")
    print(f"   {result['message']}")
    print(f"   Budget Breakdown:")
    for category, amount in result['budget_breakdown'].items():
        print(f"     {category}: {amount}")
    
    capabilities_plan = result['capabilities_plan']
    print(f"\n📊 AI CAPABILITIES PLAN:")
    print(f"   Daily Capabilities: {len(capabilities_plan['daily_capabilities'])} enabled")
    print(f"   Weekly Capabilities: {len(capabilities_plan['weekly_capabilities'])} enabled")
    print(f"   Monthly Capabilities: {len(capabilities_plan['monthly_capabilities'])} enabled")
    print(f"   Budget Utilization: {capabilities_plan['budget_utilization']:.1%}")
    
    # Example 2: Total marketing budget including ad spend
    print("\n💬 User: 'Set my total marketing budget to $500 per month, this includes ad spend'")
    result = await budget_intelligent_orchestrator.configure_budget_via_chat(
        monthly_budget=500.0,
        budget_includes_ads=True
    )
    print(f"🤖 AI Agent Response:")
    print(f"   {result['message']}")
    print(f"   Budget Breakdown:")
    for category, amount in result['budget_breakdown'].items():
        print(f"     {category}: {amount}")
    
    # Example 3: Budget recommendation
    print("\n💬 User: 'What budget do I need to become #1 spiritual guru globally?'")
    recommendation = await budget_intelligent_orchestrator.get_budget_recommendation_via_chat(
        "What budget do I need to become #1 spiritual guru globally?"
    )
    print(f"🤖 AI Agent Response:\n{recommendation}")
    
    return result

async def example_budget_intelligent_operation():
    """
    Example of daily AI operation with budget intelligence
    """
    print("\n🚀 DAILY BUDGET-INTELLIGENT AI OPERATION")
    print("=" * 50)
    
    # Run daily orchestration
    print("Running daily AI orchestration with budget intelligence...")
    result = await budget_intelligent_orchestrator.orchestrate_with_budget_intelligence()
    
    print(f"\n📊 ORCHESTRATION RESULTS:")
    print(f"   Status: {result['orchestration_status']}")
    print(f"   Budget Utilization: {result['budget_utilization']:.1%}")
    print(f"   Remaining Budget: ${result['remaining_budget']:.2f}")
    
    print(f"\n🧠 AI CAPABILITIES EXECUTED:")
    capabilities_executed = result['capabilities_executed']
    print(f"   Daily Capabilities: {capabilities_executed['daily']} capabilities executed")
    print(f"   Weekly Capabilities: {capabilities_executed['weekly']} capabilities executed")
    print(f"   Monthly Capabilities: {capabilities_executed['monthly']} capabilities executed")
    
    print(f"\n🎯 INTELLIGENCE GATHERED:")
    intelligence = result['intelligence_gathered']
    print(f"   Daily Intelligence: {len(intelligence['daily'])} analyses completed")
    print(f"   Weekly Intelligence: {len(intelligence['weekly'])} analyses completed")
    print(f"   Monthly Intelligence: {len(intelligence['monthly'])} analyses completed")
    
    print(f"\n📋 COMPREHENSIVE STRATEGY:")
    strategy = result['comprehensive_strategy']
    print(f"   Strategy Type: {strategy['comprehensive_strategy']}")
    print(f"   Data Sources: {', '.join(strategy['data_sources'])}")
    
    return result

async def example_budget_comparison():
    """
    Example showing how AI capabilities scale with budget
    """
    print("\n💰 BUDGET SCALING COMPARISON")
    print("=" * 50)
    
    budgets_to_test = [
        (75, False, "AI Intelligence Only - Basic"),
        (150, False, "AI Intelligence Only - Comprehensive"), 
        (300, False, "AI Intelligence Only - Maximum"),
        (500, True, "Total Marketing Budget - Includes Ad Spend"),
        (1000, True, "Total Marketing Budget - Premium")
    ]
    
    for budget, includes_ads, description in budgets_to_test:
        print(f"\n💰 {description}: ${budget}/month")
        result = await budget_intelligent_orchestrator.configure_budget_via_chat(
            monthly_budget=budget,
            budget_includes_ads=includes_ads
        )
        
        capabilities_plan = result['capabilities_plan']
        print(f"   AI Intelligence Budget: ${result['ai_intelligence_budget']:.2f}")
        print(f"   Content Generation Budget: ${result['content_generation_budget']:.2f}")
        print(f"   Daily Capabilities: {len([c for c in capabilities_plan['daily_capabilities'].values() if c.get('enabled', False)])}")
        print(f"   Weekly Capabilities: {len([c for c in capabilities_plan['weekly_capabilities'].values() if c.get('enabled', False)])}")
        print(f"   Monthly Capabilities: {len([c for c in capabilities_plan['monthly_capabilities'].values() if c.get('enabled', False)])}")
        print(f"   Budget Utilization: {capabilities_plan['budget_utilization']:.1%}")
        
        if includes_ads:
            print(f"   Ad Spend Reserve: ${result['budget_breakdown']['Ad Spend Reserve']}")

async def example_chat_interactions():
    """
    Example chat interactions for budget configuration
    """
    print("\n💬 CHAT INTERACTION EXAMPLES")
    print("=" * 50)
    
    chat_examples = [
        "What's the minimum budget for intelligent AI?",
        "Does my budget include ad spend?",
        "Set my budget to $200 per month for AI intelligence only",
        "I want to compete with other spiritual influencers",
        "What budget do I need for global expansion?"
    ]
    
    for query in chat_examples:
        print(f"\n💬 User: '{query}'")
        response = await budget_intelligent_orchestrator.get_budget_recommendation_via_chat(query)
        print(f"🤖 AI Agent: {response}")

async def example_capability_details():
    """
    Example showing detailed capabilities within budget
    """
    print("\n🔍 DETAILED CAPABILITY ANALYSIS")
    print("=" * 50)
    
    # Configure with specific budget
    await budget_intelligent_orchestrator.configure_budget_via_chat(150.0, False)
    
    # Get detailed capabilities plan
    capabilities_plan = await budget_intelligent_orchestrator._calculate_capabilities_within_budget()
    
    print(f"\n📊 DAILY CAPABILITIES (${capabilities_plan['total_daily_cost']:.2f}/day):")
    for capability, details in capabilities_plan['daily_capabilities'].items():
        status = "✅ ENABLED" if details.get('enabled', False) else "❌ DISABLED"
        frequency = details.get('frequency', 'N/A')
        cost = details.get('cost', 0)
        print(f"   {capability}: {status} - {frequency} (${cost:.2f})")
    
    print(f"\n📊 WEEKLY CAPABILITIES (${capabilities_plan['total_weekly_cost']:.2f}/week):")
    for capability, details in capabilities_plan['weekly_capabilities'].items():
        status = "✅ ENABLED" if details.get('enabled', False) else "❌ DISABLED"
        frequency = details.get('frequency', 'N/A')
        cost = details.get('cost', 0)
        print(f"   {capability}: {status} - {frequency} (${cost:.2f})")
    
    print(f"\n📊 MONTHLY CAPABILITIES (${capabilities_plan['total_monthly_cost']:.2f}/month):")
    for capability, details in capabilities_plan['monthly_capabilities'].items():
        status = "✅ ENABLED" if details.get('enabled', False) else "❌ DISABLED"
        frequency = details.get('frequency', 'N/A')
        cost = details.get('cost', 0)
        print(f"   {capability}: {status} - {frequency} (${cost:.2f})")

async def main():
    """
    Main example execution
    """
    print("🎯 BUDGET-INTELLIGENT AI AGENT DEMONSTRATION")
    print("🧠 AI does EVERYTHING possible within your budget")
    print("💰 No artificial feature limitations")
    print("💬 Chat-configurable budget allocation")
    print("\n" + "=" * 60)
    
    try:
        # Example 1: Budget-intelligent configuration
        await example_budget_intelligent_configuration()
        
        # Example 2: Daily AI operation
        await example_budget_intelligent_operation()
        
        # Example 3: Budget scaling comparison
        await example_budget_comparison()
        
        # Example 4: Chat interactions
        await example_chat_interactions()
        
        # Example 5: Detailed capability analysis
        await example_capability_details()
        
        print("\n" + "=" * 60)
        print("✅ DEMONSTRATION COMPLETE")
        print("\n🎯 KEY TAKEAWAYS:")
        print("   • AI does EVERYTHING possible within your budget")
        print("   • No artificial feature limitations")
        print("   • Budget determines frequency/depth, not availability")
        print("   • Chat interface clarifies ad spend vs AI intelligence")
        print("   • Perfect integration with existing automation")
        print("   • Maximum value within your constraints")
        
        print("\n💬 READY TO SET YOUR BUDGET?")
        print("   Budget-intelligent approach examples:")
        print("   • 'Set my AI budget to $100/month for intelligence only'")
        print("   • 'Set my total marketing budget to $500/month including ad spend'")
        print("   • 'What budget do I need for global spiritual leadership?'")
        print("   • 'Show me what AI can do with $X budget'")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())