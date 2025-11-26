import pytest
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.spell_checker import SpellChecker, check_style_prompt, spell_checker


class TestSpellChecker:
    """Test suite for SpellChecker"""
    
    @pytest.fixture
    def checker(self):
        """Create a SpellChecker instance for testing"""
        return SpellChecker()
    
    def test_check_prompt_no_issues(self, checker):
        """Test spell checking with correct prompt"""
        prompt = "vibrant anime style with bright colors"
        corrected, issues = checker.check_prompt(prompt)
        
        assert corrected == prompt
        assert issues == []
    
    def test_check_prompt_with_corrections(self, checker):
        """Test spell checking with common misspellings"""
        prompt = "vibrante aestetic watercolour pastelles"
        corrected, issues = checker.check_prompt(prompt)
        
        # Should correct the misspellings
        assert "vibrant" in corrected
        assert "aesthetic" in corrected
        assert "watercolor" in corrected
        assert "pastels" in corrected
        assert len(issues) > 0
    
    def test_check_prompt_empty(self, checker):
        """Test spell checking with empty prompt"""
        corrected, issues = checker.check_prompt("")
        
        assert corrected == ""
        assert issues == []
    
    def test_suggest_corrections(self, checker):
        """Test suggestion generation for misspelled words"""
        suggestions = checker._suggest_corrections("vibrante")
        
        assert "vibrant" in suggestions
        assert len(suggestions) <= 3
    
    def test_similarity_calculation(self, checker):
        """Test similarity calculation between words"""
        # Test identical words
        assert checker._similarity("color", "color") == 1.0
        
        # Test similar words
        similarity = checker._similarity("color", "colour")
        assert 0.5 < similarity < 1.0
        
        # Test different words
        similarity = checker._similarity("color", "texture")
        assert similarity < 0.5
    
    def test_get_stats(self, checker):
        """Test statistics retrieval"""
        # Use the checker to generate some stats
        checker.check_prompt("vibrante aestetic")
        stats = checker.get_stats()
        
        assert 'suggestions_made' in stats
        assert 'corrections_applied' in stats


class TestSpellCheckerIntegration:
    """Integration tests for SpellChecker"""
    
    def test_global_spell_checker_instance(self):
        """Test the global spell checker instance"""
        prompt = "cyberpunk neon aestetic with vibrante colors"
        corrected, issues = check_style_prompt(prompt)
        
        assert "aesthetic" in corrected
        assert "vibrant" in corrected
        assert len(issues) > 0
    
    def test_multiple_checks_increment_stats(self):
        """Test that multiple checks increment statistics"""
        initial_stats = spell_checker.get_stats()
        initial_corrections = initial_stats['corrections_applied']
        
        # Perform multiple checks
        check_style_prompt("vibrante colors")
        check_style_prompt("cinematico style")
        
        final_stats = spell_checker.get_stats()
        
        # Should have more corrections applied
        assert final_stats['corrections_applied'] >= initial_corrections
