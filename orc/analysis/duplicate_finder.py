"""
Duplicate code detection for ORC.

Finds similar or identical code blocks across the codebase.
Uses simple token-based similarity for speed.
"""
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class DuplicateGroup:
    """Group of duplicate or similar code blocks"""
    similarity: float  # 0.0 to 1.0
    locations: List[str]  # file::function or file::class
    code_snippet: str
    size: int  # lines of code


class DuplicateFinder:
    """Finds duplicate code across the codebase"""
    
    def __init__(self, min_similarity: float = 0.8, min_size: int = 5):
        """
        Args:
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            min_size: Minimum number of lines to consider
        """
        self.min_similarity = min_similarity
        self.min_size = min_size
    
    def find_duplicates(self, index: Dict) -> List[DuplicateGroup]:
        """Find duplicate code in the index"""
        duplicates = []
        
        # Build code blocks map
        code_blocks = self._extract_code_blocks(index)
        
        # Find exact duplicates first (fast)
        exact_duplicates = self._find_exact_duplicates(code_blocks)
        duplicates.extend(exact_duplicates)
        
        # Find similar code (slower)
        if self.min_similarity < 1.0:
            similar_code = self._find_similar_code(code_blocks)
            duplicates.extend(similar_code)
        
        return duplicates
    
    def _extract_code_blocks(self, index: Dict) -> Dict[str, Tuple[str, int]]:
        """Extract code blocks with their locations"""
        blocks = {}
        
        # Functions
        for func_id, func_data in index.get('functions', {}).items():
            code = func_data.get('code', '')
            size = func_data.get('line_end', 0) - func_data.get('line_start', 0)
            
            if code and size >= self.min_size:
                blocks[func_id] = (code, size)
        
        # Could also add class methods here
        
        return blocks
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison (remove whitespace, comments)"""
        lines = []
        for line in code.split('\n'):
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _get_code_hash(self, code: str) -> str:
        """Get hash of normalized code"""
        normalized = self._normalize_code(code)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _find_exact_duplicates(self, code_blocks: Dict) -> List[DuplicateGroup]:
        """Find exact duplicate code blocks"""
        hash_to_locations = {}
        
        for location, (code, size) in code_blocks.items():
            code_hash = self._get_code_hash(code)
            hash_to_locations.setdefault(code_hash, []).append((location, code, size))
        
        # Create duplicate groups for hashes with multiple locations
        duplicates = []
        for locations_data in hash_to_locations.values():
            if len(locations_data) > 1:
                locations = [loc for loc, _, _ in locations_data]
                code = locations_data[0][1]
                size = locations_data[0][2]
                
                duplicates.append(DuplicateGroup(
                    similarity=1.0,
                    locations=locations,
                    code_snippet=code[:200] + "..." if len(code) > 200 else code,
                    size=size
                ))
        
        return duplicates
    
    def _find_similar_code(self, code_blocks: Dict) -> List[DuplicateGroup]:
        """Find similar (not exact) code blocks"""
        similar_groups = []
        
        # Convert code blocks to token sets
        token_sets = {}
        for location, (code, size) in code_blocks.items():
            tokens = self._tokenize(code)
            token_sets[location] = (tokens, code, size)
        
        # Compare all pairs
        compared = set()
        locations = list(token_sets.keys())
        
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i+1:]:
                pair = tuple(sorted([loc1, loc2]))
                if pair in compared:
                    continue
                compared.add(pair)
                
                tokens1, code1, size1 = token_sets[loc1]
                tokens2, code2, size2 = token_sets[loc2]
                
                # Calculate Jaccard similarity
                similarity = self._jaccard_similarity(tokens1, tokens2)
                
                if similarity >= self.min_similarity:
                    similar_groups.append(DuplicateGroup(
                        similarity=similarity,
                        locations=[loc1, loc2],
                        code_snippet=code1[:200] + "..." if len(code1) > 200 else code1,
                        size=size1
                    ))
        
        return similar_groups
    
    def _tokenize(self, code: str) -> Set[str]:
        """Tokenize code into a set of tokens"""
        # Simple token-based approach
        # In production, you'd use proper AST-based tokenization
        
        normalized = self._normalize_code(code)
        
        # Split on common delimiters
        tokens = set()
        for line in normalized.split('\n'):
            # Split on whitespace and common operators
            parts = line.replace('(', ' ').replace(')', ' ')\
                       .replace('{', ' ').replace('}', ' ')\
                       .replace('[', ' ').replace(']', ' ')\
                       .replace(',', ' ').replace(';', ' ')\
                       .split()
            
            tokens.update(parts)
        
        return tokens
    
    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """Calculate Jaccard similarity between two sets"""
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_summary(self, duplicates: List[DuplicateGroup]) -> Dict:
        """Generate summary of duplicate code findings"""
        if not duplicates:
            return {
                "total_groups": 0,
                "total_locations": 0,
                "exact_duplicates": 0,
                "similar_code": 0
            }
        
        exact = sum(1 for d in duplicates if d.similarity == 1.0)
        similar = len(duplicates) - exact
        total_locations = sum(len(d.locations) for d in duplicates)
        
        return {
            "total_groups": len(duplicates),
            "total_locations": total_locations,
            "exact_duplicates": exact,
            "similar_code": similar,
            "avg_similarity": sum(d.similarity for d in duplicates) / len(duplicates)
        }
