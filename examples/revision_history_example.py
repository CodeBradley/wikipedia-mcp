#!/usr/bin/env python3
"""
Example demonstrating Wikipedia revision history and user contribution tools.

This example shows how to:
1. Get revision history for a page
2. Find who created the page
3. Compare revisions
4. Get user information and contributions
"""

from wikipedia_mcp.wikipedia_client import WikipediaClient


def main():
    # Initialize the Wikipedia client
    client = WikipediaClient()
    
    # Example 1: Get revision history for a page
    print("=== Example 1: Getting revision history ===")
    article_title = "Python (programming language)"
    
    revisions = client.get_page_revisions(article_title, limit=5)
    if revisions['exists']:
        print(f"Recent revisions for '{revisions['title']}':")
        for i, rev in enumerate(revisions['revisions'], 1):
            print(f"\n{i}. Revision {rev['revid']}:")
            print(f"   - User: {rev.get('user', 'Unknown')}")
            print(f"   - Time: {rev.get('timestamp', 'Unknown')}")
            print(f"   - Comment: {rev.get('comment', 'No comment')}")
            print(f"   - Size change: {rev.get('sizediff', 'N/A')} bytes")
    else:
        print(f"Error: {revisions.get('error', 'Unknown error')}")
    
    # Example 2: Find who created the page
    print("\n\n=== Example 2: Finding page creator ===")
    creator_info = client.get_page_creator(article_title)
    if creator_info['exists']:
        creator = creator_info['creator']
        print(f"Page '{creator_info['title']}' was created by:")
        print(f"   - Username: {creator['username']}")
        print(f"   - Created on: {creator['timestamp']}")
        print(f"   - Initial size: {creator['initial_size']} bytes")
        print(f"   - First revision ID: {creator['revid']}")
    else:
        print(f"Error: {creator_info.get('error', 'Unknown error')}")
    
    # Example 3: Get user information
    print("\n\n=== Example 3: Getting user information ===")
    username = "Jimbo Wales"  # Wikipedia co-founder
    
    user_info = client.get_user_info(username)
    if user_info['exists']:
        print(f"User information for '{user_info['username']}':")
        print(f"   - User ID: {user_info['userid']}")
        print(f"   - Registration: {user_info.get('registration', 'Unknown')}")
        print(f"   - Edit count: {user_info['editcount']:,}")
        print(f"   - Groups: {', '.join(user_info['groups'])}")
        print(f"   - Blocked: {'Yes' if user_info['blocked'] else 'No'}")
    else:
        print(f"Error: {user_info.get('error', 'Unknown error')}")
    
    # Example 4: Get user contributions
    print("\n\n=== Example 4: Getting user contributions ===")
    test_username = "WikiUser1"  # Example username
    
    contributions = client.get_user_contributions(test_username, limit=3)
    if contributions.get('contributions'):
        print(f"Recent contributions by '{contributions['username']}':")
        for i, contrib in enumerate(contributions['contributions'], 1):
            print(f"\n{i}. Edit to '{contrib['title']}':")
            print(f"   - Time: {contrib['timestamp']}")
            print(f"   - Comment: {contrib.get('comment', 'No comment')}")
            print(f"   - Size change: {contrib.get('sizediff', 0):+d} bytes")
    else:
        print(f"No contributions found for '{test_username}'")
    
    # Example 5: Compare revisions (if we have at least 2 revisions)
    print("\n\n=== Example 5: Comparing revisions ===")
    if revisions['exists'] and len(revisions['revisions']) >= 2:
        # Compare the two most recent revisions
        newer_rev = revisions['revisions'][0]['revid']
        older_rev = revisions['revisions'][1]['revid']
        
        comparison = client.compare_revisions(older_rev, newer_rev)
        if 'error' not in comparison:
            print(f"Comparison between revisions {older_rev} and {newer_rev}:")
            print(f"   - Page: {comparison['title']}")
            print(f"   - Size change: {comparison['diff_size']:+d} bytes")
            print(f"   - From user: {comparison['from_rev']['user']}")
            print(f"   - To user: {comparison['to_rev']['user']}")
            # Note: diff_html contains HTML markup, usually displayed in a browser
            print("   - Diff available (HTML format)")
        else:
            print(f"Error comparing revisions: {comparison['error']}")
    else:
        print("Not enough revisions to compare")


if __name__ == "__main__":
    main()