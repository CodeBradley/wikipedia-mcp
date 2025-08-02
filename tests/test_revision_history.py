"""
Tests for revision history and user contribution functionality.
"""

import pytest
from unittest.mock import Mock, patch
from wikipedia_mcp.wikipedia_client import WikipediaClient


class TestRevisionHistory:
    """Test revision history related methods."""
    
    def test_get_page_revisions_success(self):
        """Test successful retrieval of page revisions."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'query': {
                'pages': {
                    '12345': {
                        'title': 'Python (programming language)',
                        'pageid': 12345,
                        'revisions': [
                            {
                                'revid': 123456789,
                                'parentid': 123456788,
                                'user': 'WikiUser1',
                                'userid': 1001,
                                'timestamp': '2024-01-01T12:00:00Z',
                                'comment': 'Updated syntax section',
                                'size': 25000,
                                'sha1': 'abc123def456',
                                'minor': False
                            },
                            {
                                'revid': 123456788,
                                'parentid': 123456787,
                                'user': 'WikiUser2',
                                'userid': 1002,
                                'timestamp': '2024-01-01T11:00:00Z',
                                'comment': 'Fixed typo',
                                'size': 24950,
                                'sha1': 'def456ghi789',
                                'minor': True
                            }
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_page_revisions('Python (programming language)', limit=2)
        
        assert result['exists'] is True
        assert result['title'] == 'Python (programming language)'
        assert len(result['revisions']) == 2
        assert result['revisions'][0]['sizediff'] == 50
        assert result['revisions'][1]['sizediff'] is None
    
    def test_get_page_revisions_nonexistent_page(self):
        """Test revision history for non-existent page."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'query': {
                'pages': {
                    '-1': {
                        'title': 'NonExistentPage123',
                        'missing': ''
                    }
                }
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_page_revisions('NonExistentPage123')
        
        assert result['exists'] is False
        assert result['error'] == 'Page does not exist'


class TestUserContributions:
    """Test user contribution related methods."""
    
    def test_get_user_contributions_success(self):
        """Test successful retrieval of user contributions."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'query': {
                'usercontribs': [
                    {
                        'userid': 1001,
                        'user': 'WikiUser1',
                        'pageid': 12345,
                        'revid': 123456789,
                        'parentid': 123456788,
                        'ns': 0,
                        'title': 'Python (programming language)',
                        'timestamp': '2024-01-01T12:00:00Z',
                        'comment': 'Updated syntax section',
                        'size': 25000,
                        'sizediff': 50,
                        'minor': False,
                        'tags': []
                    },
                    {
                        'userid': 1001,
                        'user': 'WikiUser1',
                        'pageid': 54321,
                        'revid': 987654321,
                        'parentid': 987654320,
                        'ns': 0,
                        'title': 'Java (programming language)',
                        'timestamp': '2024-01-01T10:00:00Z',
                        'comment': 'Added example',
                        'size': 30000,
                        'sizediff': 200,
                        'minor': False,
                        'tags': []
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_user_contributions('WikiUser1', limit=2)
        
        assert result['username'] == 'WikiUser1'
        assert result['count'] == 2
        assert len(result['contributions']) == 2
        assert result['contributions'][0]['title'] == 'Python (programming language)'
    
    def test_get_user_info_success(self):
        """Test successful retrieval of user information."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'query': {
                'users': [
                    {
                        'userid': 1001,
                        'name': 'WikiUser1',
                        'registration': '2020-01-01T00:00:00Z',
                        'editcount': 5000,
                        'groups': ['autoconfirmed', 'extendedconfirmed'],
                        'gender': 'unknown',
                        'emailable': True
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_user_info('WikiUser1')
        
        assert result['exists'] is True
        assert result['username'] == 'WikiUser1'
        assert result['userid'] == 1001
        assert result['editcount'] == 5000
        assert 'autoconfirmed' in result['groups']
        assert result['blocked'] is False
    
    def test_get_user_info_nonexistent_user(self):
        """Test user info for non-existent user."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'query': {
                'users': [
                    {
                        'name': 'NonExistentUser123',
                        'missing': ''
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_user_info('NonExistentUser123')
        
        assert result['exists'] is False
        assert result['error'] == 'User does not exist'


class TestRevisionComparison:
    """Test revision comparison functionality."""
    
    def test_compare_revisions_success(self):
        """Test successful comparison of two revisions."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'compare': {
                'fromid': 123456788,
                'fromtimestamp': '2024-01-01T11:00:00Z',
                'fromuser': 'WikiUser2',
                'fromcomment': 'Fixed typo',
                'fromsize': 24950,
                'toid': 123456789,
                'totimestamp': '2024-01-01T12:00:00Z',
                'touser': 'WikiUser1',
                'tocomment': 'Updated syntax section',
                'tosize': 25000,
                'totitle': 'Python (programming language)',
                'diffsize': 50,
                'body': '<tr><td>...</td></tr>'  # Simplified diff HTML
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.compare_revisions(123456788, 123456789)
        
        assert 'error' not in result
        assert result['from_rev']['id'] == 123456788
        assert result['to_rev']['id'] == 123456789
        assert result['diff_size'] == 50
        assert '<tr>' in result['diff_html']


class TestPageCreator:
    """Test page creator functionality."""
    
    def test_get_page_creator_success(self):
        """Test successful retrieval of page creator."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'query': {
                'pages': {
                    '12345': {
                        'title': 'Python (programming language)',
                        'pageid': 12345,
                        'revisions': [
                            {
                                'revid': 1,
                                'user': 'OriginalCreator',
                                'userid': 100,
                                'timestamp': '2001-01-15T00:00:00Z',
                                'comment': 'Created page',
                                'size': 500
                            }
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_page_creator('Python (programming language)')
        
        assert result['exists'] is True
        assert result['creator']['username'] == 'OriginalCreator'
        assert result['creator']['revid'] == 1
        assert result['creator']['initial_size'] == 500


class TestRevisionDetails:
    """Test revision details functionality."""
    
    def test_get_revision_details_success(self):
        """Test successful retrieval of revision details."""
        client = WikipediaClient()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'query': {
                'pages': {
                    '12345': {
                        'title': 'Python (programming language)',
                        'pageid': 12345,
                        'revisions': [
                            {
                                'revid': 123456789,
                                'parentid': 123456788,
                                'user': 'WikiUser1',
                                'userid': 1001,
                                'timestamp': '2024-01-01T12:00:00Z',
                                'comment': 'Updated syntax section',
                                'size': 25000,
                                'sha1': 'abc123def456',
                                'minor': False,
                                'slots': {
                                    'main': {
                                        '*': '{{Infobox programming language...}}'  # Simplified content
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_revision_details(123456789)
        
        assert result['exists'] is True
        assert result['revid'] == 123456789
        assert result['user'] == 'WikiUser1'
        assert result['content'] is not None
        assert '{{Infobox' in result['content']