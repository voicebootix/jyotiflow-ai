"""
🚀 EXAMPLE: Pre-Launch AI Agent for Guru Brand Building
Shows how AI builds Swami Jyotirananthan's influence before platform launch
"""

import asyncio
from backend.pre_launch_ai_agent import pre_launch_ai_agent, PlatformPhase

async def example_pre_launch_initialization():
    """
    Example of initializing the pre-launch AI agent
    """
    print("🚀 PRE-LAUNCH AI AGENT FOR GURU BRAND BUILDING")
    print("=" * 60)
    
    # Show current platform status
    print(f"\n📊 CURRENT PLATFORM STATUS:")
    print(f"   Phase: {pre_launch_ai_agent.platform_status.current_phase.value}")
    print(f"   Completion: {pre_launch_ai_agent.platform_status.platform_completion_percentage}%")
    print(f"   Branding: {pre_launch_ai_agent.platform_status.branding_status}")
    print(f"   Available Features: {', '.join(pre_launch_ai_agent.platform_status.available_features)}")
    print(f"   Pending Features: {', '.join(pre_launch_ai_agent.platform_status.pending_features)}")
    
    # Show AI strategy based on current phase
    print(f"\n🎯 AI STRATEGY FOR CURRENT PHASE:")
    strategies = pre_launch_ai_agent.pre_launch_strategies
    for strategy_name, strategy_details in strategies.items():
        print(f"   {strategy_name.upper()}: {strategy_details['priority']} priority")
        print(f"     Focus: {strategy_details['focus']}")
        print(f"     Tactics: {len(strategy_details['tactics'])} tactics defined")

async def example_platform_status_updates():
    """
    Example of updating platform status through chat
    """
    print("\n💬 PLATFORM STATUS UPDATES VIA CHAT")
    print("=" * 50)
    
    # Example 1: Update platform completion
    print("\n💬 User: 'Platform is 40% complete'")
    result = await pre_launch_ai_agent.configure_platform_status_via_chat("Platform is 40% complete")
    print(f"🤖 AI Agent Response:")
    print(f"   {result['message']}")
    print(f"   Current Phase: {result['current_phase']}")
    print(f"   Platform Completion: {result['platform_completion']}")
    
    # Example 2: Update to soft launch
    print("\n💬 User: 'We're ready for soft launch with beta users'")
    result = await pre_launch_ai_agent.configure_platform_status_via_chat("We're ready for soft launch with beta users")
    print(f"🤖 AI Agent Response:")
    print(f"   {result['message']}")
    print(f"   Current Phase: {result['current_phase']}")
    print(f"   Strategy Updated: {result['updated_strategy']}")
    
    # Example 3: Branding completion
    print("\n💬 User: 'Branding is finalized and ready'")
    result = await pre_launch_ai_agent.configure_platform_status_via_chat("Branding is finalized and ready")
    print(f"🤖 AI Agent Response:")
    print(f"   {result['message']}")
    print(f"   Branding Status: {result['branding_status']}")
    
    return result

async def example_pre_launch_brand_building():
    """
    Example of daily pre-launch brand building operation
    """
    print("\n🚀 DAILY PRE-LAUNCH BRAND BUILDING")
    print("=" * 50)
    
    # Run pre-launch brand building orchestration
    print("Running daily pre-launch brand building orchestration...")
    result = await pre_launch_ai_agent.orchestrate_pre_launch_brand_building()
    
    print(f"\n📊 ORCHESTRATION RESULTS:")
    print(f"   Status: {result['orchestration_status']}")
    print(f"   Platform Phase: {result['platform_phase']}")
    print(f"   Platform Completion: {result['platform_completion']}")
    
    print(f"\n🧠 BRAND ANALYSIS:")
    brand_analysis = result['brand_analysis']
    print(f"   Spiritual Authority Score: {brand_analysis.get('spiritual_authority_score', 0):.1%}")
    print(f"   Cultural Authenticity Score: {brand_analysis.get('cultural_authenticity_score', 0):.1%}")
    print(f"   Social Media Presence: {brand_analysis.get('social_media_presence', {}).get('presence_strength', 0):.1%}")
    print(f"   Audience Engagement Rate: {brand_analysis.get('audience_engagement', {}).get('engagement_rate', 0):.1%}")
    
    print(f"\n📋 DAILY STRATEGY:")
    daily_strategy = result['daily_strategy']
    print(f"   Primary Focus: {daily_strategy.get('primary_focus', 'brand_building')}")
    print(f"   Platform Mentions: {daily_strategy.get('platform_mentions', 'subtle_teasers')}")
    print(f"   Call to Action: {daily_strategy.get('call_to_action', 'follow_for_guidance')}")
    print(f"   Audience Building: {daily_strategy.get('audience_building', 'aggressive_growth')}")
    
    print(f"\n🎯 CONTENT EXECUTION:")
    content_execution = result['content_execution']
    print(f"   Content Types Created: {content_execution.get('content_types_created', 0)}")
    print(f"   Brand Focus Percentage: {content_execution.get('brand_focus_percentage', 85)}%")
    
    print(f"\n📈 SOCIAL GROWTH RESULTS:")
    social_growth = result['social_growth_results']
    print(f"   Growth Focus: {social_growth.get('growth_focus', 'spiritual_community')}")
    print(f"   Target Demographics: {', '.join(social_growth.get('target_demographics', []))}")
    
    print(f"\n🏆 AUTHORITY BUILDING:")
    authority_building = result['authority_building']
    print(f"   Authority Building: {authority_building.get('authority_building', 'in_progress')}")
    print(f"   Progress: {authority_building.get('progress', 'strong')}")
    
    print(f"\n🔮 PLATFORM PREPARATION:")
    platform_prep = result['platform_preparation']
    print(f"   Platform Prep: {platform_prep.get('platform_prep', 'subtle_teasers')}")
    print(f"   Intensity: {platform_prep.get('intensity', 'low')}")
    
    print(f"\n⏭️ NEXT PHASE RECOMMENDATIONS:")
    for rec in result['next_phase_recommendations']:
        print(f"   • {rec}")
    
    return result

async def example_phase_specific_recommendations():
    """
    Example of getting phase-specific recommendations via chat
    """
    print("\n💬 PHASE-SPECIFIC RECOMMENDATIONS")
    print("=" * 50)
    
    chat_queries = [
        "What should we focus on now?",
        "When should we launch the platform?",
        "Are we ready for product marketing?",
        "What's our current platform status?"
    ]
    
    for query in chat_queries:
        print(f"\n💬 User: '{query}'")
        response = await pre_launch_ai_agent.get_platform_status_recommendation(query)
        print(f"🤖 AI Agent:\n{response}")

async def example_phase_progression():
    """
    Example showing how AI adapts as platform develops through phases
    """
    print("\n🎯 PHASE PROGRESSION EXAMPLE")
    print("=" * 50)
    
    phases_to_test = [
        ("Platform is 30% complete", "PRE_LAUNCH"),
        ("Platform is 75% complete", "SOFT_LAUNCH"),
        ("Platform is 95% complete", "PLATFORM_READY")
    ]
    
    for status_update, expected_phase in phases_to_test:
        print(f"\n📊 TESTING PHASE: {expected_phase}")
        print(f"💬 Status Update: '{status_update}'")
        
        # Update platform status
        result = await pre_launch_ai_agent.configure_platform_status_via_chat(status_update)
        print(f"✅ Phase Updated: {result['current_phase']}")
        
        # Get strategy recommendation for this phase
        recommendation = await pre_launch_ai_agent.get_platform_status_recommendation("What should we focus on now?")
        print(f"🎯 AI Recommendation:")
        print(f"   {recommendation.split('Primary Objectives:')[0] if 'Primary Objectives:' in recommendation else recommendation}")

async def example_content_strategy_by_phase():
    """
    Example showing how content strategy changes by phase
    """
    print("\n📝 CONTENT STRATEGY BY PHASE")
    print("=" * 50)
    
    # Reset to pre-launch
    await pre_launch_ai_agent.configure_platform_status_via_chat("Platform is 25% complete")
    
    # Show content strategy for each phase
    phases = [
        ("PRE_LAUNCH", "Platform is 25% complete"),
        ("SOFT_LAUNCH", "Platform is 75% complete"),
        ("PLATFORM_READY", "Platform is 95% complete")
    ]
    
    for phase_name, status_update in phases:
        print(f"\n🎯 {phase_name} CONTENT STRATEGY:")
        await pre_launch_ai_agent.configure_platform_status_via_chat(status_update)
        
        # Run orchestration to see strategy
        result = await pre_launch_ai_agent.orchestrate_pre_launch_brand_building()
        strategy = result['daily_strategy']
        
        print(f"   Primary Focus: {strategy.get('primary_focus', 'N/A')}")
        print(f"   Platform Mentions: {strategy.get('platform_mentions', 'N/A')}")
        print(f"   Call to Action: {strategy.get('call_to_action', 'N/A')}")
        print(f"   Audience Building: {strategy.get('audience_building', 'N/A')}")
        
        if 'content_strategy' in strategy:
            print(f"   Content Strategy:")
            for content_type, frequency in strategy['content_strategy'].items():
                print(f"     {content_type}: {frequency}")

async def main():
    """
    Main example execution showing pre-launch AI agent in action
    """
    print("🚀 PRE-LAUNCH AI AGENT DEMONSTRATION")
    print("🧠 Building Swami Jyotirananthan's influence before platform launch")
    print("📱 Phase-aware strategy that adapts to platform development")
    print("🎯 Brand building FIRST, product marketing LATER")
    print("\n" + "=" * 70)
    
    try:
        # Example 1: Pre-launch initialization
        await example_pre_launch_initialization()
        
        # Example 2: Platform status updates
        await example_platform_status_updates()
        
        # Example 3: Daily brand building operation
        await example_pre_launch_brand_building()
        
        # Example 4: Phase-specific recommendations
        await example_phase_specific_recommendations()
        
        # Example 5: Phase progression
        await example_phase_progression()
        
        # Example 6: Content strategy by phase
        await example_content_strategy_by_phase()
        
        print("\n" + "=" * 70)
        print("✅ PRE-LAUNCH AI AGENT DEMONSTRATION COMPLETE")
        print("\n🎯 KEY TAKEAWAYS:")
        print("   • AI understands current platform development phase")
        print("   • Focuses on building guru's brand and influence FIRST")
        print("   • Adapts strategy as platform develops")
        print("   • Builds spiritual authority and Tamil cultural community")
        print("   • Prepares audience for platform launch")
        print("   • Transitions to product marketing when platform is ready")
        
        print("\n💬 READY TO START BUILDING INFLUENCE?")
        print("   Current phase commands:")
        print("   • 'Platform is X% complete'")
        print("   • 'Start building guru's influence now'")
        print("   • 'Focus on brand building in pre-launch'")
        print("   • 'What should we focus on now?'")
        
        print("\n🚀 DEPLOYMENT READY:")
        print("   1. Deploy pre-launch AI agent")
        print("   2. Set current platform status")
        print("   3. Start building Swami Jyotirananthan's influence")
        print("   4. Monitor brand growth and community building")
        print("   5. Transition to platform marketing when ready")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")

if __name__ == "__main__":
    # Run the pre-launch AI agent example
    asyncio.run(main())