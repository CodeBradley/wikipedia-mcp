"""
Wikipedia API client implementation.
"""

import logging
import wikipediaapi
import requests
from typing import Dict, List, Optional, Any
import functools

logger = logging.getLogger(__name__)

class WikipediaClient:
    """Client for interacting with the Wikipedia API."""

    # Language variant mappings - maps variant codes to their base language
    LANGUAGE_VARIANTS = {
        'zh-hans': 'zh',  # Simplified Chinese
        'zh-hant': 'zh',  # Traditional Chinese
        'zh-tw': 'zh',    # Traditional Chinese (Taiwan)
        'zh-hk': 'zh',    # Traditional Chinese (Hong Kong)
        'zh-mo': 'zh',    # Traditional Chinese (Macau)
        'zh-cn': 'zh',    # Simplified Chinese (China)
        'zh-sg': 'zh',    # Simplified Chinese (Singapore)
        'zh-my': 'zh',    # Simplified Chinese (Malaysia)
        # Add more language variants as needed
        # Serbian variants
        'sr-latn': 'sr',  # Serbian Latin
        'sr-cyrl': 'sr',  # Serbian Cyrillic
        # Norwegian variants
        'no': 'nb',       # Norwegian Bokmål (default)
        # Kurdish variants  
        'ku-latn': 'ku',  # Kurdish Latin
        'ku-arab': 'ku',  # Kurdish Arabic
    }

    # Country/locale to language code mappings
    COUNTRY_TO_LANGUAGE = {
        # English-speaking countries
        'US': 'en', 'USA': 'en', 'United States': 'en',
        'UK': 'en', 'GB': 'en', 'United Kingdom': 'en',
        'CA': 'en', 'Canada': 'en',
        'AU': 'en', 'Australia': 'en',
        'NZ': 'en', 'New Zealand': 'en',
        'IE': 'en', 'Ireland': 'en',
        'ZA': 'en', 'South Africa': 'en',
        
        # Chinese-speaking countries/regions
        'CN': 'zh-hans', 'China': 'zh-hans',
        'TW': 'zh-tw', 'Taiwan': 'zh-tw',
        'HK': 'zh-hk', 'Hong Kong': 'zh-hk',
        'MO': 'zh-mo', 'Macau': 'zh-mo',
        'SG': 'zh-sg', 'Singapore': 'zh-sg',
        'MY': 'zh-my', 'Malaysia': 'zh-my',
        
        # Major European countries
        'DE': 'de', 'Germany': 'de',
        'FR': 'fr', 'France': 'fr',
        'ES': 'es', 'Spain': 'es',
        'IT': 'it', 'Italy': 'it',
        'PT': 'pt', 'Portugal': 'pt',
        'NL': 'nl', 'Netherlands': 'nl',
        'PL': 'pl', 'Poland': 'pl',
        'RU': 'ru', 'Russia': 'ru',
        'UA': 'uk', 'Ukraine': 'uk',
        'TR': 'tr', 'Turkey': 'tr',
        'GR': 'el', 'Greece': 'el',
        'SE': 'sv', 'Sweden': 'sv',
        'NO': 'no', 'Norway': 'no',
        'DK': 'da', 'Denmark': 'da',
        'FI': 'fi', 'Finland': 'fi',
        'IS': 'is', 'Iceland': 'is',
        'CZ': 'cs', 'Czech Republic': 'cs',
        'SK': 'sk', 'Slovakia': 'sk',
        'HU': 'hu', 'Hungary': 'hu',
        'RO': 'ro', 'Romania': 'ro',
        'BG': 'bg', 'Bulgaria': 'bg',
        'HR': 'hr', 'Croatia': 'hr',
        'SI': 'sl', 'Slovenia': 'sl',
        'RS': 'sr', 'Serbia': 'sr',
        'BA': 'bs', 'Bosnia and Herzegovina': 'bs',
        'MK': 'mk', 'Macedonia': 'mk',
        'AL': 'sq', 'Albania': 'sq',
        'MT': 'mt', 'Malta': 'mt',
        
        # Asian countries
        'JP': 'ja', 'Japan': 'ja',
        'KR': 'ko', 'South Korea': 'ko',
        'IN': 'hi', 'India': 'hi',
        'TH': 'th', 'Thailand': 'th',
        'VN': 'vi', 'Vietnam': 'vi',
        'ID': 'id', 'Indonesia': 'id',
        'PH': 'tl', 'Philippines': 'tl',
        'BD': 'bn', 'Bangladesh': 'bn',
        'PK': 'ur', 'Pakistan': 'ur',
        'LK': 'si', 'Sri Lanka': 'si',
        'MM': 'my', 'Myanmar': 'my',
        'KH': 'km', 'Cambodia': 'km',
        'LA': 'lo', 'Laos': 'lo',
        'MN': 'mn', 'Mongolia': 'mn',
        'KZ': 'kk', 'Kazakhstan': 'kk',
        'UZ': 'uz', 'Uzbekistan': 'uz',
        'AF': 'fa', 'Afghanistan': 'fa',
        
        # Middle Eastern countries
        'IR': 'fa', 'Iran': 'fa',
        'SA': 'ar', 'Saudi Arabia': 'ar',
        'AE': 'ar', 'UAE': 'ar',
        'EG': 'ar', 'Egypt': 'ar',
        'IQ': 'ar', 'Iraq': 'ar',
        'SY': 'ar', 'Syria': 'ar',
        'JO': 'ar', 'Jordan': 'ar',
        'LB': 'ar', 'Lebanon': 'ar',
        'IL': 'he', 'Israel': 'he',
        
        # African countries
        'MA': 'ar', 'Morocco': 'ar',
        'DZ': 'ar', 'Algeria': 'ar',
        'TN': 'ar', 'Tunisia': 'ar',
        'LY': 'ar', 'Libya': 'ar',
        'SD': 'ar', 'Sudan': 'ar',
        'ET': 'am', 'Ethiopia': 'am',
        'KE': 'sw', 'Kenya': 'sw',
        'TZ': 'sw', 'Tanzania': 'sw',
        'NG': 'ha', 'Nigeria': 'ha',
        'GH': 'en', 'Ghana': 'en',
        
        # Latin American countries
        'MX': 'es', 'Mexico': 'es',
        'AR': 'es', 'Argentina': 'es',
        'CO': 'es', 'Colombia': 'es',
        'VE': 'es', 'Venezuela': 'es',
        'PE': 'es', 'Peru': 'es',
        'CL': 'es', 'Chile': 'es',
        'EC': 'es', 'Ecuador': 'es',
        'BO': 'es', 'Bolivia': 'es',
        'PY': 'es', 'Paraguay': 'es',
        'UY': 'es', 'Uruguay': 'es',
        'CR': 'es', 'Costa Rica': 'es',
        'PA': 'es', 'Panama': 'es',
        'GT': 'es', 'Guatemala': 'es',
        'HN': 'es', 'Honduras': 'es',
        'SV': 'es', 'El Salvador': 'es',
        'NI': 'es', 'Nicaragua': 'es',
        'CU': 'es', 'Cuba': 'es',
        'DO': 'es', 'Dominican Republic': 'es',
        'BR': 'pt', 'Brazil': 'pt',
        
        # Additional countries
        'BY': 'be', 'Belarus': 'be',
        'EE': 'et', 'Estonia': 'et',
        'LV': 'lv', 'Latvia': 'lv',
        'LT': 'lt', 'Lithuania': 'lt',
        'GE': 'ka', 'Georgia': 'ka',
        'AM': 'hy', 'Armenia': 'hy',
        'AZ': 'az', 'Azerbaijan': 'az',
    }

    def __init__(self, language: str = "en", country: Optional[str] = None, enable_cache: bool = False):
        """Initialize the Wikipedia client.
        
        Args:
            language: The language code for Wikipedia (default: "en" for English).
                     Supports language variants like 'zh-hans', 'zh-tw', etc.
            country: The country/locale code (e.g., 'US', 'CN', 'TW'). 
                    If provided, overrides language parameter.
            enable_cache: Whether to enable caching for API calls (default: False).
        """
        # Resolve country to language if country is provided
        if country:
            resolved_language = self._resolve_country_to_language(country)
            self.original_input = country
            self.input_type = "country"
            self.resolved_language = resolved_language
            # Maintain backward compatibility
            self.original_language = resolved_language
        else:
            self.original_input = language
            self.input_type = "language"
            self.resolved_language = language
            # Maintain backward compatibility
            self.original_language = language
        
        self.enable_cache = enable_cache
        self.user_agent = "WikipediaMCPServer/0.1.0 (https://github.com/rudra-ravi/wikipedia-mcp)"
        
        # Parse language and variant
        self.base_language, self.language_variant = self._parse_language_variant(self.resolved_language)
        
        # Use base language for API and library initialization
        self.wiki = wikipediaapi.Wikipedia(
            user_agent=self.user_agent,
            language=self.base_language,
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        self.api_url = f"https://{self.base_language}.wikipedia.org/w/api.php"
        
        if self.enable_cache:
            self.search = functools.lru_cache(maxsize=128)(self.search)
            self.get_article = functools.lru_cache(maxsize=128)(self.get_article)
            self.get_summary = functools.lru_cache(maxsize=128)(self.get_summary)
            self.get_sections = functools.lru_cache(maxsize=128)(self.get_sections)
            self.get_links = functools.lru_cache(maxsize=128)(self.get_links)
            self.get_related_topics = functools.lru_cache(maxsize=128)(self.get_related_topics)
            self.summarize_for_query = functools.lru_cache(maxsize=128)(self.summarize_for_query)
            self.summarize_section = functools.lru_cache(maxsize=128)(self.summarize_section)
            self.extract_facts = functools.lru_cache(maxsize=128)(self.extract_facts)

    def _resolve_country_to_language(self, country: str) -> str:
        """Resolve country/locale code to language code.
        
        Args:
            country: The country/locale code (e.g., 'US', 'CN', 'Taiwan').
            
        Returns:
            The corresponding language code.
            
        Raises:
            ValueError: If the country code is not supported.
        """
        # Normalize country code (upper case, handle common variations)
        country_upper = country.upper().strip()
        country_title = country.title().strip()
        
        # Try exact matches first
        if country_upper in self.COUNTRY_TO_LANGUAGE:
            return self.COUNTRY_TO_LANGUAGE[country_upper]
        
        # Try title case
        if country_title in self.COUNTRY_TO_LANGUAGE:
            return self.COUNTRY_TO_LANGUAGE[country_title]
        
        # Try original case
        if country in self.COUNTRY_TO_LANGUAGE:
            return self.COUNTRY_TO_LANGUAGE[country]
        
        # Provide helpful error message with suggestions
        available_countries = list(self.COUNTRY_TO_LANGUAGE.keys())
        # Get first 10 country codes for suggestions
        country_codes = [c for c in available_countries if len(c) <= 3][:10]
        
        raise ValueError(
            f"Unsupported country/locale: '{country}'. "
            f"Supported country codes include: {', '.join(country_codes)}. "
            f"Use --language parameter for direct language codes instead."
        )

    def _parse_language_variant(self, language: str) -> tuple[str, Optional[str]]:
        """Parse language code and extract base language and variant.
        
        Args:
            language: The language code, possibly with variant (e.g., 'zh-hans', 'zh-tw').
            
        Returns:
            A tuple of (base_language, variant) where variant is None if not a variant.
        """
        if language in self.LANGUAGE_VARIANTS:
            base_language = self.LANGUAGE_VARIANTS[language]
            return base_language, language
        else:
            return language, None
    
    def _add_variant_to_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add language variant parameter to API request parameters if needed.
        
        Args:
            params: The API request parameters.
            
        Returns:
            Updated parameters with variant if applicable.
        """
        if self.language_variant:
            params = params.copy()
            params['variant'] = self.language_variant
        return params

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Wikipedia for articles matching a query.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of search results.
        """
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'utf8': 1,
            'srsearch': query,
            'srlimit': limit
        }
        
        # Add variant parameter if needed
        params = self._add_variant_to_params(params)
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('query', {}).get('search', []):
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'pageid': item.get('pageid', 0),
                    'wordcount': item.get('wordcount', 0),
                    'timestamp': item.get('timestamp', '')
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return []

    def get_article(self, title: str) -> Dict[str, Any]:
        """Get the full content of a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article.
            
        Returns:
            A dictionary containing the article information.
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                return {
                    'title': title,
                    'exists': False,
                    'error': 'Page does not exist'
                }
            
            # Get sections
            sections = self._extract_sections(page.sections)
            
            # Get categories
            categories = [cat for cat in page.categories.keys()]
            
            # Get links
            links = [link for link in page.links.keys()]
            
            return {
                'title': page.title,
                'pageid': page.pageid,
                'summary': page.summary,
                'text': page.text,
                'url': page.fullurl,
                'sections': sections,
                'categories': categories,
                'links': links[:100],  # Limit to 100 links to avoid too much data
                'exists': True
            }
        except Exception as e:
            logger.error(f"Error getting Wikipedia article: {e}")
            return {
                'title': title,
                'exists': False,
                'error': str(e)
            }

    def get_summary(self, title: str) -> str:
        """Get a summary of a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article.
            
        Returns:
            The article summary.
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                return f"No Wikipedia article found for '{title}'."
            
            return page.summary
        except Exception as e:
            logger.error(f"Error getting Wikipedia summary: {e}")
            return f"Error retrieving summary for '{title}': {str(e)}"

    def get_sections(self, title: str) -> List[Dict[str, Any]]:
        """Get the sections of a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article.
            
        Returns:
            A list of sections.
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                return []
            
            return self._extract_sections(page.sections)
        except Exception as e:
            logger.error(f"Error getting Wikipedia sections: {e}")
            return []

    def get_links(self, title: str) -> List[str]:
        """Get the links in a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article.
            
        Returns:
            A list of links.
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                return []
            
            return [link for link in page.links.keys()]
        except Exception as e:
            logger.error(f"Error getting Wikipedia links: {e}")
            return []

    def get_related_topics(self, title: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get topics related to a Wikipedia article based on links and categories.
        
        Args:
            title: The title of the Wikipedia article.
            limit: Maximum number of related topics to return.
            
        Returns:
            A list of related topics.
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                return []
            
            # Get links from the page
            links = list(page.links.keys())
            
            # Get categories
            categories = list(page.categories.keys())
            
            # Combine and limit
            related = []
            
            # Add links first
            for link in links[:limit]:
                link_page = self.wiki.page(link)
                if link_page.exists():
                    related.append({
                        'title': link,
                        'summary': link_page.summary[:200] + '...' if len(link_page.summary) > 200 else link_page.summary,
                        'url': link_page.fullurl,
                        'type': 'link'
                    })
                
                if len(related) >= limit:
                    break
            
            # Add categories if we still have room
            remaining = limit - len(related)
            if remaining > 0:
                for category in categories[:remaining]:
                    # Remove "Category:" prefix if present
                    clean_category = category.replace("Category:", "")
                    related.append({
                        'title': clean_category,
                        'type': 'category'
                    })
            
            return related
        except Exception as e:
            logger.error(f"Error getting related topics: {e}")
            return []

    def _extract_sections(self, sections, level=0) -> List[Dict[str, Any]]:
        """Extract sections recursively.
        
        Args:
            sections: The sections to extract.
            level: The current section level.
            
        Returns:
            A list of sections.
        """
        result = []
        
        for section in sections:
            section_data = {
                'title': section.title,
                'level': level,
                'text': section.text,
                'sections': self._extract_sections(section.sections, level + 1)
            }
            result.append(section_data)
        
        return result

    def summarize_for_query(self, title: str, query: str, max_length: int = 250) -> str:
        """
        Get a summary of a Wikipedia article tailored to a specific query.
        This is a simplified implementation that returns a snippet around the query.
        
        Args:
            title: The title of the Wikipedia article.
            query: The query to focus the summary on.
            max_length: The maximum length of the summary.
            
        Returns:
            A query-focused summary.
        """
        try:
            page = self.wiki.page(title)
            if not page.exists():
                return f"No Wikipedia article found for '{title}'."

            text_content = page.text
            query_lower = query.lower()
            text_lower = text_content.lower()

            start_index = text_lower.find(query_lower)
            if start_index == -1:
                # If query not found, return the beginning of the summary or article text
                summary_part = page.summary[:max_length]
                if not summary_part:
                    summary_part = text_content[:max_length]
                return summary_part + "..." if len(summary_part) >= max_length else summary_part


            # Try to get context around the query
            context_start = max(0, start_index - (max_length // 2))
            context_end = min(len(text_content), start_index + len(query) + (max_length // 2))
            
            snippet = text_content[context_start:context_end]
            
            if len(snippet) > max_length:
                snippet = snippet[:max_length]

            return snippet + "..." if len(snippet) >= max_length or context_end < len(text_content) else snippet

        except Exception as e:
            logger.error(f"Error generating query-focused summary for '{title}': {e}")
            return f"Error generating query-focused summary for '{title}': {str(e)}"

    def summarize_section(self, title: str, section_title: str, max_length: int = 150) -> str:
        """
        Get a summary of a specific section of a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article.
            section_title: The title of the section to summarize.
            max_length: The maximum length of the summary.
            
        Returns:
            A summary of the specified section.
        """
        try:
            page = self.wiki.page(title)
            if not page.exists():
                return f"No Wikipedia article found for '{title}'."

            target_section = None
            
            # Helper function to find the section
            def find_section_recursive(sections_list, target_title):
                for sec in sections_list:
                    if sec.title.lower() == target_title.lower():
                        return sec
                    # Check subsections
                    found_in_subsection = find_section_recursive(sec.sections, target_title)
                    if found_in_subsection:
                        return found_in_subsection
                return None

            target_section = find_section_recursive(page.sections, section_title)

            if not target_section or not target_section.text:
                return f"Section '{section_title}' not found or is empty in article '{title}'."
            
            summary = target_section.text[:max_length]
            return summary + "..." if len(target_section.text) > max_length else summary
            
        except Exception as e:
            logger.error(f"Error summarizing section '{section_title}' for article '{title}': {e}")
            return f"Error summarizing section '{section_title}': {str(e)}"

    def extract_facts(self, title: str, topic_within_article: Optional[str] = None, count: int = 5) -> List[str]:
        """
        Extract key facts from a Wikipedia article.
        This is a simplified implementation returning the first few sentences of the summary
        or a relevant section if topic_within_article is provided.
        
        Args:
            title: The title of the Wikipedia article.
            topic_within_article: Optional topic/section to focus fact extraction.
            count: The number of facts to extract.
            
        Returns:
            A list of key facts (strings).
        """
        try:
            page = self.wiki.page(title)
            if not page.exists():
                return [f"No Wikipedia article found for '{title}'."]

            text_to_process = ""
            if topic_within_article:
                # Try to find the section text
                def find_section_text_recursive(sections_list, target_title):
                    for sec in sections_list:
                        if sec.title.lower() == target_title.lower():
                            return sec.text
                        found_in_subsection = find_section_text_recursive(sec.sections, target_title)
                        if found_in_subsection:
                            return found_in_subsection
                    return None
                
                section_text = find_section_text_recursive(page.sections, topic_within_article)
                if section_text:
                    text_to_process = section_text
                else:
                    # Fallback to summary if specific topic section not found
                    text_to_process = page.summary
            else:
                text_to_process = page.summary
            
            if not text_to_process:
                return ["No content found to extract facts from."]

            # Basic sentence splitting (can be improved with NLP libraries like nltk or spacy)
            sentences = [s.strip() for s in text_to_process.split('.') if s.strip()]
            
            facts = []
            for sentence in sentences[:count]:
                if sentence: # Ensure not an empty string after strip
                    facts.append(sentence + ".") # Add back the period
            
            return facts if facts else ["Could not extract facts from the provided text."]

        except Exception as e:
            logger.error(f"Error extracting key facts for '{title}': {e}")
            return [f"Error extracting key facts for '{title}': {str(e)}"]

    def get_page_revisions(self, title: str, limit: int = 50) -> Dict[str, Any]:
        """Get the revision history of a Wikipedia page.
        
        Args:
            title: The title of the Wikipedia article.
            limit: Maximum number of revisions to return (default: 50).
            
        Returns:
            A dictionary containing revision history.
        """
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'titles': title,
            'utf8': 1,
            'rvlimit': limit,
            'rvprop': 'ids|timestamp|user|userid|comment|size|sha1|flags',
            'rvdir': 'older'  # Get newest revisions first
        }
        
        # Add variant parameter if needed
        params = self._add_variant_to_params(params)
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            page_id = list(pages.keys())[0] if pages else None
            
            if not page_id or page_id == '-1':
                return {
                    'title': title,
                    'exists': False,
                    'error': 'Page does not exist'
                }
            
            page_data = pages[page_id]
            revisions = page_data.get('revisions', [])
            
            # Process revisions to add size change info
            for i, rev in enumerate(revisions):
                if i < len(revisions) - 1:
                    rev['sizediff'] = rev['size'] - revisions[i + 1]['size']
                else:
                    # For the oldest revision in this batch, we can't calculate size diff
                    rev['sizediff'] = None
            
            return {
                'title': page_data.get('title', title),
                'pageid': page_data.get('pageid'),
                'revisions': revisions,
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting page revisions: {e}")
            return {
                'title': title,
                'exists': False,
                'error': str(e)
            }

    def get_user_contributions(self, username: str, limit: int = 50) -> Dict[str, Any]:
        """Get contributions made by a specific user.
        
        Args:
            username: The username to get contributions for.
            limit: Maximum number of contributions to return (default: 50).
            
        Returns:
            A dictionary containing user contributions.
        """
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'usercontribs',
            'ucuser': username,
            'uclimit': limit,
            'ucprop': 'ids|title|timestamp|comment|size|sizediff|flags|tags',
            'ucdir': 'older'  # Get newest contributions first
        }
        
        # Add variant parameter if needed
        params = self._add_variant_to_params(params)
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            contributions = data.get('query', {}).get('usercontribs', [])
            
            return {
                'username': username,
                'contributions': contributions,
                'count': len(contributions)
            }
            
        except Exception as e:
            logger.error(f"Error getting user contributions: {e}")
            return {
                'username': username,
                'contributions': [],
                'error': str(e)
            }

    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get detailed information about a Wikipedia user.
        
        Args:
            username: The username to get information for.
            
        Returns:
            A dictionary containing user information.
        """
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'users',
            'ususers': username,
            'usprop': 'blockinfo|groups|editcount|registration|emailable|gender'
        }
        
        # Add variant parameter if needed
        params = self._add_variant_to_params(params)
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            users = data.get('query', {}).get('users', [])
            
            if not users:
                return {
                    'username': username,
                    'exists': False,
                    'error': 'User not found'
                }
            
            user_data = users[0]
            
            # Check if user exists (missing = user doesn't exist)
            if 'missing' in user_data:
                return {
                    'username': username,
                    'exists': False,
                    'error': 'User does not exist'
                }
            
            return {
                'username': user_data.get('name', username),
                'userid': user_data.get('userid'),
                'registration': user_data.get('registration'),
                'editcount': user_data.get('editcount', 0),
                'groups': user_data.get('groups', []),
                'gender': user_data.get('gender', 'unknown'),
                'emailable': user_data.get('emailable', False),
                'blocked': 'blockid' in user_data,
                'blockreason': user_data.get('blockreason'),
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {
                'username': username,
                'exists': False,
                'error': str(e)
            }

    def compare_revisions(self, from_rev: int, to_rev: int) -> Dict[str, Any]:
        """Compare two revisions of a Wikipedia page.
        
        Args:
            from_rev: The older revision ID.
            to_rev: The newer revision ID.
            
        Returns:
            A dictionary containing the comparison results.
        """
        params = {
            'action': 'compare',
            'format': 'json',
            'fromrev': from_rev,
            'torev': to_rev,
            'prop': 'diff|diffsize|rel|ids|title|user|comment|size'
        }
        
        # Add variant parameter if needed
        params = self._add_variant_to_params(params)
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            compare_data = data.get('compare', {})
            
            if 'error' in data:
                return {
                    'error': data['error'].get('info', 'Unknown error'),
                    'from_rev': from_rev,
                    'to_rev': to_rev
                }
            
            return {
                'from_rev': {
                    'id': compare_data.get('fromid'),
                    'timestamp': compare_data.get('fromtimestamp'),
                    'user': compare_data.get('fromuser'),
                    'comment': compare_data.get('fromcomment'),
                    'size': compare_data.get('fromsize')
                },
                'to_rev': {
                    'id': compare_data.get('toid'),
                    'timestamp': compare_data.get('totimestamp'),
                    'user': compare_data.get('touser'),
                    'comment': compare_data.get('tocomment'),
                    'size': compare_data.get('tosize')
                },
                'title': compare_data.get('totitle'),
                'diff_size': compare_data.get('diffsize'),
                'diff_html': compare_data.get('body', '')  # HTML diff content
            }
            
        except Exception as e:
            logger.error(f"Error comparing revisions: {e}")
            return {
                'error': str(e),
                'from_rev': from_rev,
                'to_rev': to_rev
            }

    def get_page_creator(self, title: str) -> Dict[str, Any]:
        """Get information about who created a Wikipedia page.
        
        Args:
            title: The title of the Wikipedia article.
            
        Returns:
            A dictionary containing page creator information.
        """
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'titles': title,
            'utf8': 1,
            'rvlimit': 1,
            'rvprop': 'ids|timestamp|user|userid|comment|size',
            'rvdir': 'newer'  # Get the first (oldest) revision
        }
        
        # Add variant parameter if needed
        params = self._add_variant_to_params(params)
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            page_id = list(pages.keys())[0] if pages else None
            
            if not page_id or page_id == '-1':
                return {
                    'title': title,
                    'exists': False,
                    'error': 'Page does not exist'
                }
            
            page_data = pages[page_id]
            revisions = page_data.get('revisions', [])
            
            if not revisions:
                return {
                    'title': title,
                    'exists': True,
                    'error': 'No revision data available'
                }
            
            first_revision = revisions[0]
            
            return {
                'title': page_data.get('title', title),
                'pageid': page_data.get('pageid'),
                'creator': {
                    'username': first_revision.get('user'),
                    'userid': first_revision.get('userid'),
                    'timestamp': first_revision.get('timestamp'),
                    'comment': first_revision.get('comment', ''),
                    'initial_size': first_revision.get('size', 0),
                    'revid': first_revision.get('revid')
                },
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting page creator: {e}")
            return {
                'title': title,
                'exists': False,
                'error': str(e)
            }

    def get_revision_details(self, revid: int) -> Dict[str, Any]:
        """Get detailed information about a specific revision.
        
        Args:
            revid: The revision ID to get details for.
            
        Returns:
            A dictionary containing revision details.
        """
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'revids': revid,
            'rvprop': 'ids|timestamp|user|userid|comment|size|sha1|flags|content',
            'rvslots': 'main'
        }
        
        # Add variant parameter if needed
        params = self._add_variant_to_params(params)
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            
            if not pages:
                return {
                    'revid': revid,
                    'exists': False,
                    'error': 'Revision not found'
                }
            
            page_id = list(pages.keys())[0]
            page_data = pages[page_id]
            
            if 'missing' in page_data:
                return {
                    'revid': revid,
                    'exists': False,
                    'error': 'Page does not exist'
                }
            
            revisions = page_data.get('revisions', [])
            
            if not revisions:
                return {
                    'revid': revid,
                    'exists': False,
                    'error': 'Revision not found'
                }
            
            revision = revisions[0]
            
            # Extract content if available
            content = None
            if 'slots' in revision and 'main' in revision['slots']:
                content = revision['slots']['main'].get('*', None)
            
            return {
                'revid': revision.get('revid'),
                'parentid': revision.get('parentid'),
                'title': page_data.get('title'),
                'pageid': page_data.get('pageid'),
                'timestamp': revision.get('timestamp'),
                'user': revision.get('user'),
                'userid': revision.get('userid'),
                'comment': revision.get('comment', ''),
                'size': revision.get('size', 0),
                'sha1': revision.get('sha1'),
                'minor': revision.get('minor', False),
                'content': content,
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting revision details: {e}")
            return {
                'revid': revid,
                'exists': False,
                'error': str(e)
            }

    def get_talk_page(self, title: str) -> Dict[str, Any]:
        """Get the content and metadata of a Wikipedia talk page.
        
        Args:
            title: The title of the Wikipedia article (talk page will be auto-derived).
            
        Returns:
            A dictionary containing talk page content and metadata.
        """
        # Convert article title to talk page title
        if title.startswith('Talk:'):
            talk_title = title
        else:
            talk_title = f"Talk:{title}"
        
        try:
            # Get talk page content
            page = self.wiki.page(talk_title)
            
            if not page.exists():
                return {
                    'title': talk_title,
                    'article_title': title,
                    'exists': False,
                    'error': 'Talk page does not exist'
                }
            
            # Extract discussion sections
            sections = self._extract_sections(page.sections)
            section_titles = [section['title'] for section in sections if section['title']]
            
            # Get talk page revisions for activity analysis
            revisions_result = self.get_page_revisions(talk_title, limit=10)
            recent_activity = len(revisions_result.get('revisions', [])) if revisions_result.get('exists') else 0
            
            return {
                'title': talk_title,
                'article_title': title,
                'raw_content': page.text,
                'summary': page.summary,
                'url': page.fullurl,
                'metadata': {
                    'section_count': len(sections),
                    'discussion_threads': section_titles,
                    'last_modified': revisions_result.get('revisions', [{}])[0].get('timestamp') if revisions_result.get('revisions') else None,
                    'recent_revisions': recent_activity,
                    'categories': [cat for cat in page.categories.keys()],
                    'size': len(page.text)
                },
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting talk page: {e}")
            return {
                'title': talk_title,
                'article_title': title,
                'exists': False,
                'error': str(e)
            }

    def analyze_edit_activity(self, title: str, start_datetime: Optional[str] = None, 
                            end_datetime: Optional[str] = None, window_size: str = "day",
                            z_threshold: float = 2.0) -> Dict[str, Any]:
        """Analyze edit activity patterns and detect spikes using statistical methods.
        
        Args:
            title: The title of the Wikipedia article.
            start_datetime: Start datetime in ISO format (e.g., "2024-01-15T14:30:00Z").
            end_datetime: End datetime in ISO format. Defaults to now if not specified.
            window_size: Time window for grouping ("day", "week", "month").
            z_threshold: Z-score threshold for spike detection (default: 2.0 = top 2.5%).
            
        Returns:
            A dictionary containing activity analysis and detected spikes.
        """
        from datetime import datetime, timedelta
        from collections import defaultdict
        import statistics
        
        try:
            # Get comprehensive revision history
            all_revisions = []
            limit = 500  # Get a large sample for statistical analysis
            
            # Get revisions in batches if needed
            revisions_result = self.get_page_revisions(title, limit=limit)
            if not revisions_result.get('exists'):
                return {
                    'title': title,
                    'exists': False,
                    'error': revisions_result.get('error', 'Page does not exist')
                }
            
            all_revisions = revisions_result.get('revisions', [])
            
            # Parse timestamps and filter by date range
            filtered_revisions = []
            for rev in all_revisions:
                try:
                    rev_time = datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
                    
                    # Apply date filters
                    if start_datetime:
                        start_time = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                        if rev_time < start_time:
                            continue
                    
                    if end_datetime:
                        end_time = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
                        if rev_time > end_time:
                            continue
                    
                    rev['parsed_timestamp'] = rev_time
                    filtered_revisions.append(rev)
                    
                except Exception as e:
                    logger.warning(f"Error parsing timestamp {rev.get('timestamp')}: {e}")
                    continue
            
            # Group revisions by time window
            grouped_activity = defaultdict(lambda: {'edit_count': 0, 'editors': set(), 'revisions': []})
            
            for rev in filtered_revisions:
                timestamp = rev['parsed_timestamp']
                
                # Create time window key
                if window_size == "day":
                    window_key = timestamp.strftime('%Y-%m-%d')
                elif window_size == "week":
                    # Get Monday of the week
                    monday = timestamp - timedelta(days=timestamp.weekday())
                    window_key = monday.strftime('%Y-%m-%d-week')
                elif window_size == "month":
                    window_key = timestamp.strftime('%Y-%m')
                else:
                    window_key = timestamp.strftime('%Y-%m-%d')  # Default to day
                
                grouped_activity[window_key]['edit_count'] += 1
                grouped_activity[window_key]['editors'].add(rev.get('user', 'Unknown'))
                grouped_activity[window_key]['revisions'].append(rev)
            
            # Calculate statistics
            edit_counts = [data['edit_count'] for data in grouped_activity.values()]
            editor_counts = [len(data['editors']) for data in grouped_activity.values()]
            
            if len(edit_counts) < 3:  # Need at least 3 data points for meaningful statistics
                return {
                    'title': title,
                    'analysis_period': f"{start_datetime or 'beginning'} to {end_datetime or 'now'}",
                    'window_size': window_size,
                    'total_windows': len(grouped_activity),
                    'error': 'Insufficient data for statistical analysis (need at least 3 time windows)'
                }
            
            # Statistical calculations
            edit_mean = statistics.mean(edit_counts)
            edit_stdev = statistics.stdev(edit_counts) if len(edit_counts) > 1 else 0
            editor_mean = statistics.mean(editor_counts)
            editor_stdev = statistics.stdev(editor_counts) if len(editor_counts) > 1 else 0
            
            # Detect spikes
            spikes = []
            for window_key, data in grouped_activity.items():
                edit_z_score = (data['edit_count'] - edit_mean) / edit_stdev if edit_stdev > 0 else 0
                editor_z_score = (len(data['editors']) - editor_mean) / editor_stdev if editor_stdev > 0 else 0
                
                if edit_z_score >= z_threshold or editor_z_score >= z_threshold:
                    spikes.append({
                        'window': window_key,
                        'edit_count': data['edit_count'],
                        'editor_count': len(data['editors']),
                        'edit_z_score': round(edit_z_score, 2),
                        'editor_z_score': round(editor_z_score, 2),
                        'significance': 'high' if max(edit_z_score, editor_z_score) >= 3 else 'moderate',
                        'editors': list(data['editors']),
                        'sample_revisions': data['revisions'][:5]  # First 5 revisions as examples
                    })
            
            # Sort spikes by significance
            spikes.sort(key=lambda x: max(x['edit_z_score'], x['editor_z_score']), reverse=True)
            
            return {
                'title': title,
                'analysis_period': f"{start_datetime or 'beginning'} to {end_datetime or 'now'}",
                'window_size': window_size,
                'z_threshold': z_threshold,
                'statistics': {
                    'total_windows': len(grouped_activity),
                    'total_revisions_analyzed': len(filtered_revisions),
                    'edit_statistics': {
                        'mean': round(edit_mean, 2),
                        'stdev': round(edit_stdev, 2),
                        'min': min(edit_counts),
                        'max': max(edit_counts)
                    },
                    'editor_statistics': {
                        'mean': round(editor_mean, 2),
                        'stdev': round(editor_stdev, 2),
                        'min': min(editor_counts),
                        'max': max(editor_counts)
                    }
                },
                'spikes_detected': len(spikes),
                'spikes': spikes,
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing edit activity: {e}")
            return {
                'title': title,
                'exists': False,
                'error': str(e)
            }

    def get_significant_revisions(self, title: str, start_datetime: Optional[str] = None,
                                end_datetime: Optional[str] = None, limit: int = 50,
                                min_significance: float = 0.5) -> Dict[str, Any]:
        """Get the most significant revisions based on weighted scoring algorithm.
        
        Args:
            title: The title of the Wikipedia article.
            start_datetime: Start datetime in ISO format (e.g., "2024-01-15T14:30:00Z").
            end_datetime: End datetime in ISO format. Defaults to now if not specified.
            limit: Maximum number of significant revisions to return.
            min_significance: Minimum significance score (0.0-1.0) to include.
            
        Returns:
            A dictionary containing ranked significant revisions with scores.
        """
        from datetime import datetime, timedelta
        import re
        
        try:
            # Get comprehensive revision history
            revisions_result = self.get_page_revisions(title, limit=500)
            if not revisions_result.get('exists'):
                return {
                    'title': title,
                    'exists': False,
                    'error': revisions_result.get('error', 'Page does not exist')
                }
            
            all_revisions = revisions_result.get('revisions', [])
            
            # Filter by date range and add parsed timestamps
            filtered_revisions = []
            for rev in all_revisions:
                try:
                    rev_time = datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
                    
                    # Apply date filters
                    if start_datetime:
                        start_time = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                        if rev_time < start_time:
                            continue
                    
                    if end_datetime:
                        end_time = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
                        if rev_time > end_time:
                            continue
                    
                    rev['parsed_timestamp'] = rev_time
                    filtered_revisions.append(rev)
                    
                except Exception as e:
                    logger.warning(f"Error parsing timestamp {rev.get('timestamp')}: {e}")
                    continue
            
            if len(filtered_revisions) < 2:
                return {
                    'title': title,
                    'analysis_period': f"{start_datetime or 'beginning'} to {end_datetime or 'now'}",
                    'error': 'Insufficient revision data for significance analysis'
                }
            
            # Calculate significance scores
            scored_revisions = []
            
            # Get article size for normalization (from most recent revision)
            current_size = filtered_revisions[0].get('size', 1000)  # Default fallback
            
            # Get user edit counts for experience factor
            user_edit_counts = {}
            for rev in filtered_revisions:
                user = rev.get('user')
                if user:
                    user_edit_counts[user] = user_edit_counts.get(user, 0) + 1
            
            for i, rev in enumerate(filtered_revisions):
                significance_score = self._calculate_significance_score(
                    rev, filtered_revisions, i, current_size, user_edit_counts
                )
                
                if significance_score >= min_significance:
                    scored_revisions.append({
                        **rev,
                        'significance_score': round(significance_score, 3),
                        'significance_factors': self._get_significance_factors(
                            rev, filtered_revisions, i, current_size, user_edit_counts
                        )
                    })
            
            # Sort by significance score
            scored_revisions.sort(key=lambda x: x['significance_score'], reverse=True)
            
            # Limit results
            top_revisions = scored_revisions[:limit]
            
            return {
                'title': title,
                'analysis_period': f"{start_datetime or 'beginning'} to {end_datetime or 'now'}",
                'total_revisions_analyzed': len(filtered_revisions),
                'significant_revisions_found': len(scored_revisions),
                'min_significance_threshold': min_significance,
                'top_revisions': top_revisions,
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting significant revisions: {e}")
            return {
                'title': title,
                'exists': False,
                'error': str(e)
            }

    def _calculate_significance_score(self, revision: Dict[str, Any], all_revisions: List[Dict[str, Any]], 
                                    index: int, article_size: int, user_edit_counts: Dict[str, int]) -> float:
        """Calculate significance score using weighted algorithm."""
        import re
        from datetime import timedelta
        
        score = 0.0
        
        # 1. Normalized bytes change (30% weight)
        size_change = abs(revision.get('sizediff', 0))
        normalized_size_change = min(size_change / max(article_size * 0.1, 100), 1.0)  # Cap at reasonable %
        score += 0.30 * normalized_size_change
        
        # 2. Revert proximity score (25% weight)
        revert_score = self._calculate_revert_score(revision, all_revisions, index)
        score += 0.25 * revert_score
        
        # 3. Editor experience factor (20% weight)
        user = revision.get('user', '')
        user_edits = user_edit_counts.get(user, 1)
        # New editors (fewer edits) have higher impact potential
        experience_factor = min(1.0, 5.0 / max(user_edits, 1))
        score += 0.20 * experience_factor
        
        # 4. Discussion reference score (15% weight)
        comment = revision.get('comment', '').lower()
        discussion_patterns = [
            'talk page', 'discuss', 'see talk', 'talk:', 'consensus',
            'dispute', 'controversial', 'revert', 'vandalism', 'rv'
        ]
        discussion_score = min(sum(1 for pattern in discussion_patterns if pattern in comment) * 0.2, 1.0)
        score += 0.15 * discussion_score
        
        # 5. Edit war indicator (10% weight)
        edit_war_score = self._calculate_edit_war_score(revision, all_revisions, index)
        score += 0.10 * edit_war_score
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_revert_score(self, revision: Dict[str, Any], all_revisions: List[Dict[str, Any]], index: int) -> float:
        """Calculate score based on how quickly a revision was reverted."""
        from datetime import timedelta
        
        # Check if this revision was reverted in subsequent edits
        rev_time = revision.get('parsed_timestamp')
        rev_size = revision.get('size', 0)
        
        # Look at next few revisions for potential reverts
        for i in range(index - 5, index):  # Look at 5 previous revisions (more recent)
            if i < 0 or i >= len(all_revisions):
                continue
                
            next_rev = all_revisions[i]
            next_time = next_rev.get('parsed_timestamp')
            next_size = next_rev.get('size', 0)
            
            if not next_time or not rev_time:
                continue
            
            time_diff = abs((next_time - rev_time).total_seconds())
            size_diff = abs(next_size - rev_size)
            
            # If size returned close to original within short time, likely a revert
            if time_diff < 3600 and size_diff < 50:  # Within 1 hour, similar size
                # Faster reverts = higher significance
                revert_score = max(0, 1.0 - (time_diff / 3600))
                return revert_score
        
        return 0.0
    
    def _calculate_edit_war_score(self, revision: Dict[str, Any], all_revisions: List[Dict[str, Any]], index: int) -> float:
        """Calculate score based on edit war patterns."""
        # Look for rapid back-and-forth edits
        rev_time = revision.get('parsed_timestamp')
        if not rev_time:
            return 0.0
        
        # Count edits within 24 hours around this revision
        rapid_edits = 0
        for other_rev in all_revisions:
            other_time = other_rev.get('parsed_timestamp')
            if not other_time:
                continue
            
            time_diff = abs((other_time - rev_time).total_seconds())
            if time_diff <= 86400:  # Within 24 hours
                rapid_edits += 1
        
        # More rapid edits = higher edit war score
        return min(rapid_edits / 20.0, 1.0)  # Normalize to 20 edits = max score
    
    def _get_significance_factors(self, revision: Dict[str, Any], all_revisions: List[Dict[str, Any]], 
                                index: int, article_size: int, user_edit_counts: Dict[str, int]) -> Dict[str, Any]:
        """Get detailed breakdown of significance factors for transparency."""
        size_change = abs(revision.get('sizediff', 0))
        user = revision.get('user', '')
        comment = revision.get('comment', '')
        
        return {
            'size_change_bytes': revision.get('sizediff', 0),
            'normalized_size_impact': min(size_change / max(article_size * 0.1, 100), 1.0),
            'user_experience_level': user_edit_counts.get(user, 1),
            'has_discussion_keywords': any(keyword in comment.lower() 
                                         for keyword in ['talk', 'discuss', 'revert', 'dispute']),
            'edit_comment': comment,
            'timestamp': revision.get('timestamp'),
            'user': user
        } 