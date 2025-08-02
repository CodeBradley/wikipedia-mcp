#!/usr/bin/env python3
"""
Advanced Wikipedia Controversy Detection Example

This example demonstrates how to use the new Wikipedia MCP tools to detect
and analyze controversies, edit wars, and significant editing patterns.

The tools work together to provide comprehensive analysis:
1. Statistical spike detection using z-scores
2. Weighted significance scoring for individual edits
3. Talk page analysis for community discussions
4. User behavior analysis and contribution patterns
"""

from wikipedia_mcp.wikipedia_client import WikipediaClient
import json
from datetime import datetime, timedelta


def analyze_controversy(client, article_title, time_period_days=365):
    """
    Comprehensive controversy analysis for a Wikipedia article.
    
    Args:
        client: WikipediaClient instance
        article_title: Title of the article to analyze
        time_period_days: Number of days to look back (default: 1 year)
    """
    print(f"\n🔍 ANALYZING: {article_title}")
    print("=" * 60)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=time_period_days)
    start_datetime = start_date.isoformat() + "Z"
    end_datetime = end_date.isoformat() + "Z"
    
    # Step 1: Detect edit activity spikes
    print("\n📊 STEP 1: Detecting Edit Activity Spikes")
    print("-" * 40)
    
    activity_analysis = client.analyze_edit_activity(
        article_title,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        window_size="day",
        z_threshold=2.0  # 2 standard deviations = top 2.5%
    )
    
    if not activity_analysis.get('exists'):
        print(f"❌ Article '{article_title}' not found or no data available")
        return
    
    stats = activity_analysis['statistics']
    print(f"📈 Analysis Period: {activity_analysis['analysis_period']}")
    print(f"📊 Total Windows Analyzed: {stats['total_windows']}")
    print(f"📝 Total Revisions: {stats['total_revisions_analyzed']}")
    print(f"🎯 Spikes Detected: {activity_analysis['spikes_detected']}")
    
    print(f"\n📊 Edit Statistics:")
    print(f"   • Average: {stats['edit_statistics']['mean']} edits/day")
    print(f"   • Std Dev: {stats['edit_statistics']['stdev']}")
    print(f"   • Range: {stats['edit_statistics']['min']}-{stats['edit_statistics']['max']}")
    
    # Display detected spikes
    if activity_analysis['spikes']:
        print(f"\n🚨 DETECTED SPIKES:")
        for i, spike in enumerate(activity_analysis['spikes'][:5], 1):
            print(f"   {i}. {spike['window']} ({spike['significance']} significance)")
            print(f"      • {spike['edit_count']} edits (z-score: {spike['edit_z_score']})")
            print(f"      • {spike['editor_count']} editors (z-score: {spike['editor_z_score']})")
            print(f"      • Key editors: {', '.join(spike['editors'][:3])}{'...' if len(spike['editors']) > 3 else ''}")
    
    # Step 2: Analyze significant revisions
    print(f"\n🎯 STEP 2: Analyzing Significant Revisions")
    print("-" * 40)
    
    significant_revisions = client.get_significant_revisions(
        article_title,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        limit=10,
        min_significance=0.5
    )
    
    if significant_revisions.get('exists'):
        print(f"📊 {significant_revisions['significant_revisions_found']} significant revisions found")
        print(f"🔥 Top {len(significant_revisions['top_revisions'])} most significant:")
        
        for i, rev in enumerate(significant_revisions['top_revisions'][:5], 1):
            factors = rev['significance_factors']
            print(f"\n   {i}. Revision {rev['revid']} (Score: {rev['significance_score']})")
            print(f"      • User: {rev['user']} ({factors['user_experience_level']} edits)")
            print(f"      • Time: {rev['timestamp']}")
            print(f"      • Size change: {factors['size_change_bytes']:+d} bytes")
            print(f"      • Comment: {rev['comment'][:80]}{'...' if len(rev['comment']) > 80 else ''}")
            
            if factors['has_discussion_keywords']:
                print(f"      • 💬 Contains discussion keywords")
    
    # Step 3: Analyze talk page
    print(f"\n💬 STEP 3: Talk Page Analysis")
    print("-" * 40)
    
    talk_page = client.get_talk_page(article_title)
    
    if talk_page.get('exists'):
        meta = talk_page['metadata']
        print(f"📄 Talk page found: {talk_page['title']}")
        print(f"📏 Size: {meta['size']:,} characters")
        print(f"📑 Sections: {meta['section_count']}")
        print(f"🔄 Recent revisions: {meta['recent_revisions']}")
        
        if meta['discussion_threads']:
            print(f"💭 Discussion topics:")
            for thread in meta['discussion_threads'][:5]:
                print(f"   • {thread}")
            if len(meta['discussion_threads']) > 5:
                print(f"   • ... and {len(meta['discussion_threads']) - 5} more")
    else:
        print(f"❌ No talk page found for '{article_title}'")
    
    # Step 4: Summary and insights
    print(f"\n🎯 STEP 4: Summary and Insights")
    print("-" * 40)
    
    # Calculate controversy score
    controversy_indicators = 0
    insights = []
    
    if activity_analysis['spikes_detected'] > 0:
        controversy_indicators += min(activity_analysis['spikes_detected'], 3)
        insights.append(f"🚨 {activity_analysis['spikes_detected']} edit spike(s) detected")
    
    if significant_revisions.get('exists') and significant_revisions['significant_revisions_found'] > 5:
        controversy_indicators += 2
        insights.append(f"⚡ {significant_revisions['significant_revisions_found']} significant revisions")
    
    if talk_page.get('exists') and talk_page['metadata']['recent_revisions'] > 10:
        controversy_indicators += 1
        insights.append(f"💬 Active talk page with {talk_page['metadata']['recent_revisions']} recent revisions")
    
    # Determine controversy level
    if controversy_indicators >= 5:
        level = "🔥 HIGH"
        color = "HIGH CONTROVERSY"
    elif controversy_indicators >= 3:
        level = "⚠️  MODERATE"
        color = "MODERATE ACTIVITY"
    elif controversy_indicators >= 1:
        level = "📈 LOW"
        color = "SOME ACTIVITY"
    else:
        level = "✅ MINIMAL"
        color = "STABLE"
    
    print(f"🏆 CONTROVERSY LEVEL: {level}")
    print(f"📊 Score: {controversy_indicators}/6")
    
    if insights:
        print(f"\n💡 KEY INSIGHTS:")
        for insight in insights:
            print(f"   • {insight}")
    
    return {
        'controversy_level': level,
        'score': controversy_indicators,
        'spikes': activity_analysis['spikes_detected'],
        'significant_revisions': significant_revisions.get('significant_revisions_found', 0),
        'talk_page_active': talk_page.get('exists', False)
    }


def main():
    """Run controversy analysis on example articles."""
    client = WikipediaClient()
    
    print("🔍 WIKIPEDIA CONTROVERSY DETECTION SYSTEM")
    print("=========================================")
    print("This example demonstrates advanced analysis capabilities:")
    print("• Statistical spike detection using z-scores")
    print("• Weighted significance scoring for edits")
    print("• Talk page discussion analysis")
    print("• Comprehensive controversy assessment")
    
    # Example articles with different controversy levels
    test_articles = [
        "Python (programming language)",  # Generally stable tech article
        "Climate change",                 # Potentially controversial topic
        "Artificial intelligence",        # Current events, some debate
    ]
    
    results = {}
    
    for article in test_articles:
        try:
            results[article] = analyze_controversy(client, article, time_period_days=90)
        except Exception as e:
            print(f"\n❌ Error analyzing '{article}': {e}")
            results[article] = None
    
    # Final comparison
    print(f"\n📊 COMPARATIVE ANALYSIS")
    print("=" * 60)
    print(f"{'Article':<30} {'Level':<15} {'Score':<8} {'Spikes':<8} {'Significant':<12}")
    print("-" * 75)
    
    for article, result in results.items():
        if result:
            print(f"{article[:29]:<30} {result['controversy_level'][:14]:<15} "
                  f"{result['score']:<8} {result['spikes']:<8} {result['significant_revisions']:<12}")
    
    print(f"\n✅ Analysis complete! Use these tools to:")
    print("• Identify controversial topics and time periods")
    print("• Research edit wars and vandalism patterns")
    print("• Study community discussions and conflict resolution")
    print("• Track how articles evolve during breaking news")


if __name__ == "__main__":
    main()