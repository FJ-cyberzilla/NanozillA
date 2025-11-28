import streamlit as st
from typing import List, Tuple, Dict
import re


class SpellChecker:
    """
    Basic spell checker for style prompts with artistic terminology support
    """

    # Common artistic and color-related words that might be misspelled
    ARTISTIC_TERMS = {
        'vibrant', 'aesthetic', 'cyberpunk', 'watercolor', 'pastels',
        'cinematic', 'dramatic', 'surreal', 'abstract', 'impressionist',
        'renaissance', 'baroque', 'contemporary', 'minimalist',
        'saturated', 'monochromatic', 'complementary', 'analogous',
        'warm', 'cool', 'neutral', 'vintage', 'retro', 'modern',
        'anime', 'manga', 'cartoon', 'realistic', 'photorealistic',
        'fantasy', 'sci-fi', 'steampunk', 'gothic', 'romantic'
    }

    # Common misspellings and corrections
    COMMON_CORRECTIONS = {
        'vibrante': 'vibrant',
        'aestetic': 'aesthetic',
        'watercolour': 'watercolor',
        'pastelles': 'pastels',
        'cinematico': 'cinematic',
        'surrealistic': 'surreal',
        'abstracto': 'abstract',
        'minimalistic': 'minimalist',
        'saturate': 'saturated',
        'monochrome': 'monochromatic',
        'complementory': 'complementary',
        'analogous': 'analogous',  # Common misspelling
        'vintaje': 'vintage',
        'retroo': 'retro',
        'moderne': 'modern',
        'animee': 'anime',
        'mangaa': 'manga',
        'cartoony': 'cartoon',
        'realist': 'realistic',
        'fantasyy': 'fantasy',
        'scifi': 'sci-fi',
        'steampunck': 'steampunk',
        'gothik': 'gothic',
        'romantik': 'romantic'
    }

    def __init__(self):
        self.suggestions_made = 0
        self.corrections_applied = 0

    def check_prompt(self, prompt: str) -> Tuple[str, List[Dict]]:
        """
        Check prompt for common spelling mistakes and provide suggestions

        Returns:
            Tuple of (corrected_prompt, list_of_issues)
        """
        if not prompt:
            return prompt, []

        issues = []
        words = re.findall(r'\b[a-zA-Z]+\b', prompt.lower())
        original_words = re.findall(r'\b[a-zA-Z]+\b', prompt)

        corrected_prompt = prompt
        corrections_made = []

        for i, (word, original_word) in enumerate(zip(words, original_words)):
            # Check for common corrections
            if word in self.COMMON_CORRECTIONS:
                correction = self.COMMON_CORRECTIONS[word]
                if original_word[0].isupper():
                    correction = correction.capitalize()

                # Replace in prompt (preserving case)
                corrected_prompt = corrected_prompt.replace(original_word, correction)
                corrections_made.append((original_word, correction))

                issues.append({
                    'type': 'spelling',
                    'original': original_word,
                    'suggestion': correction,
                    'severity': 'medium'
                })

            # Check for artistic terms with close matches
            elif len(word) > 4:  # Only check longer words
                suggestions = self._suggest_corrections(word)
                if suggestions:
                    issues.append({
                        'type': 'suggestion',
                        'original': original_word,
                        'suggestions': suggestions,
                        'severity': 'low'
                    })

        if corrections_made:
            self.corrections_applied += 1
            st.info(f"✏️ Auto-corrected {len(corrections_made)} words")

        return corrected_prompt, issues

    def _suggest_corrections(self, word: str) -> List[str]:
        """
        Suggest corrections for potentially misspelled words
        """
        suggestions = []

        for term in self.ARTISTIC_TERMS:
            if self._similarity(word, term) > 0.7:
                suggestions.append(term)

        return suggestions[:3]  # Return top 3 suggestions

    def _similarity(self, word1: str, word2: str) -> float:
        """
        Calculate simple similarity between two words
        """
        # Simple character-based similarity
        common_chars = set(word1) & set(word2)
        return len(common_chars) / max(len(set(word1)), len(set(word2)))

    def display_spelling_issues(self, issues: List[Dict]):
        """
        Display spelling issues to user
        """
        if not issues:
            return

        with st.expander("🔍 Spelling Suggestions", expanded=True):
            for issue in issues:
                if issue['type'] == 'spelling':
                    st.warning(
                        f"**Corrected**: '{issue['original']}' → '{issue['suggestion']}'"
                    )
                elif issue['type'] == 'suggestion':
                    suggestions = ", ".join(issue['suggestions'])
                    st.info(
                        f"**'{issue['original']}'** - Did you mean: {suggestions}?"
                    )

    def get_stats(self) -> Dict[str, int]:
        """
        Get spell checker statistics
        """
        return {
            'suggestions_made': self.suggestions_made,
            'corrections_applied': self.corrections_applied
        }


# Global instance
spell_checker = SpellChecker()


def check_style_prompt(prompt: str) -> Tuple[str, List[Dict]]:
    """
    Check style prompt for spelling issues

    Returns:
        Tuple of (corrected_prompt, issues_list)
    """
    return spell_checker.check_prompt(prompt)


def display_spelling_help():
    """
    Display spelling help section
    """
    with st.expander("💡 Writing Effective Prompts"):
        st.markdown("""
        **Tips for Better Results:**
        
        • **Be Specific**: "vibrant sunset with orange and purple hues" 
        • **Use Art Terms**: "watercolor", "oil painting", "digital art"
        • **Describe Colors**: "pastel colors", "bold primary colors"
        • **Mention Style**: "anime style", "film noir", "cyberpunk"
        • **Avoid Ambiguity**: Clear, direct descriptions work best
        
        **Common Artistic Terms:**
        - **Styles**: impressionist, surreal, abstract, minimalist
        - **Mediums**: watercolor, oil, acrylic, digital, charcoal
        - **Eras**: renaissance, baroque, contemporary, vintage
        - **Genres**: fantasy, sci-fi, cyberpunk, steampunk, gothic
        """)
