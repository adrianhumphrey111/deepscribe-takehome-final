"""
Real LLM Prompt Evaluation Framework

This evaluates the actual prompts used in our system by:
1. Testing current prompts against known good/bad cases
2. Comparing different prompt versions
3. Measuring extraction accuracy, consistency, and edge case handling
4. Providing prompt optimization recommendations

Run with: python -m evaluation.prompt_evaluator
"""

import asyncio
import json
import time
import statistics
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from config import Config
from services.llm_provider import OpenAIProvider, ClaudeProvider
from models.patient_data import PatientData

@dataclass
class PromptTestCase:
    """A test case for evaluating prompt performance"""
    name: str
    transcript: str
    expected_extraction: Dict[str, Any]
    expected_confidence_range: Tuple[float, float]  # (min, max) expected confidence
    difficulty_level: str  # "easy", "medium", "hard"
    test_category: str  # "extraction_accuracy", "edge_cases", "consistency"

@dataclass
class PromptEvaluationResult:
    """Result of a single prompt evaluation"""
    test_case_name: str
    provider: str
    prompt_version: str
    success: bool
    extraction_accuracy: float  # 0-1 score
    confidence_score: float
    execution_time_ms: int
    extracted_data: Dict[str, Any]
    expected_data: Dict[str, Any]
    errors: List[str]

class PromptEvaluator:
    """Evaluates the actual prompts used in our LLM providers"""
    
    def __init__(self):
        self.config = Config()
        self.openai_provider = OpenAIProvider(self.config) if self.config.OPENAI_API_KEY else None
        self.claude_provider = ClaudeProvider(self.config) if self.config.ANTHROPIC_API_KEY else None
        
    def get_prompt_test_cases(self) -> List[PromptTestCase]:
        """Test cases specifically designed to evaluate prompt effectiveness"""
        return [
            # Test 1: Perfect extraction case
            PromptTestCase(
                name="Perfect_Extraction_Oncology",
                transcript="""
                58-year-old female diagnosed with invasive ductal carcinoma, ER positive, PR positive, HER2 negative. 
                She lives in Boston, Massachusetts. Current medications include tamoxifen 20mg daily. 
                No known allergies. Stage IIIA breast cancer with recent progression to metastatic disease.
                """,
                expected_extraction={
                    "age": 58,
                    "gender": "FEMALE",
                    "primary_diagnosis": "breast cancer",
                    "cancer_stage": "Stage IIIA",
                    "tumor_markers": {"ER": "positive", "PR": "positive", "HER2": "negative"},
                    "location": {"city": "Boston", "state": "Massachusetts"},
                    "medications": ["tamoxifen"]
                },
                expected_confidence_range=(0.85, 1.0),
                difficulty_level="easy",
                test_category="extraction_accuracy"
            ),
            
            # Test 2: Edge case - minimal information
            PromptTestCase(
                name="Minimal_Information_Edge_Case",
                transcript="42-year-old reports fatigue. Lives in Miami.",
                expected_extraction={
                    "age": 42,
                    "primary_diagnosis": None,  # Should be null due to lack of specific diagnosis
                    "conditions": ["fatigue"],
                    "location": {"city": "Miami"}
                },
                expected_confidence_range=(0.3, 0.6),  # Low confidence expected
                difficulty_level="hard",
                test_category="edge_cases"
            ),
            
            # Test 3: Consistency test - same info, different wording
            PromptTestCase(
                name="Consistency_Test_A",
                transcript="""
                Patient is a 45-year-old male with Type 1 diabetes mellitus. 
                He resides in Denver, Colorado. Takes insulin daily. Allergic to penicillin.
                """,
                expected_extraction={
                    "age": 45,
                    "gender": "MALE",
                    "primary_diagnosis": "Type 1 diabetes mellitus",
                    "location": {"city": "Denver", "state": "Colorado"},
                    "medications": ["insulin"],
                    "allergies": ["penicillin"]
                },
                expected_confidence_range=(0.8, 1.0),
                difficulty_level="medium",
                test_category="consistency"
            ),
            
            # Test 4: Same info as Test 3, different phrasing
            PromptTestCase(
                name="Consistency_Test_B",
                transcript="""
                45-year-old male patient diagnosed with T1DM. 
                Lives in Denver, CO. On daily insulin therapy. Has penicillin allergy.
                """,
                expected_extraction={
                    "age": 45,
                    "gender": "MALE", 
                    "primary_diagnosis": "Type 1 diabetes mellitus",  # Should normalize T1DM
                    "location": {"city": "Denver", "state": "Colorado"},  # Should normalize CO
                    "medications": ["insulin"],
                    "allergies": ["penicillin"]
                },
                expected_confidence_range=(0.8, 1.0),
                difficulty_level="medium", 
                test_category="consistency"
            ),
            
            # Test 5: Complex case with multiple conditions
            PromptTestCase(
                name="Complex_Multi_Condition",
                transcript="""
                67-year-old female with stage IIIA non-small cell lung cancer, EGFR wild-type, PD-L1 65%. 
                Also has COPD, hypertension, type 2 diabetes, and history of MI with stent 3 years ago.
                Lives in Phoenix, Arizona. Current meds: durvalumab infusions, metformin, lisinopril, metoprolol.
                Allergic to penicillin. Recent scans show stable disease but interested in trials if progression occurs.
                """,
                expected_extraction={
                    "age": 67,
                    "gender": "FEMALE",
                    "primary_diagnosis": "non-small cell lung cancer",
                    "cancer_stage": "Stage IIIA",
                    "tumor_markers": {"EGFR": "wild-type", "PD-L1": "65%"},
                    "location": {"city": "Phoenix", "state": "Arizona"},
                    "medications": ["durvalumab", "metformin", "lisinopril", "metoprolol"],
                    "comorbidities": ["COPD", "hypertension", "type 2 diabetes", "myocardial infarction"],
                    "allergies": ["penicillin"]
                },
                expected_confidence_range=(0.75, 0.95),
                difficulty_level="hard",
                test_category="extraction_accuracy"
            ),
            
            # Test 6: Ambiguous diagnosis test
            PromptTestCase(
                name="Ambiguous_Diagnosis_Test",
                transcript="""
                55-year-old woman with suspicious breast lump, family history of breast cancer.
                Recent mammogram shows BIRADS 4 lesion. Scheduled for biopsy next week.
                Lives in Chicago, Illinois. Takes vitamins daily.
                """,
                expected_extraction={
                    "age": 55,
                    "gender": "FEMALE",
                    "primary_diagnosis": None,  # Should be null - no confirmed diagnosis yet
                    "conditions": ["suspicious breast lump"],
                    "location": {"city": "Chicago", "state": "Illinois"},
                    "medications": ["vitamins"],
                    "comorbidities": ["family history of breast cancer"]
                },
                expected_confidence_range=(0.4, 0.7),  # Medium confidence
                difficulty_level="medium",
                test_category="edge_cases"
            ),
            
            # Test 7: Medication extraction challenge
            PromptTestCase(
                name="Medication_Extraction_Challenge",
                transcript="""
                62-year-old male on multiple medications: Metoprolol XL 50mg twice daily, 
                Lisinopril 10mg once daily, Atorvastatin 40mg at bedtime, 
                Metformin 1000mg BID, baby aspirin 81mg daily, and Jardiance 10mg in the morning.
                Lives in Dallas, Texas. History of diabetes and hypertension.
                """,
                expected_extraction={
                    "age": 62,
                    "gender": "MALE",
                    "location": {"city": "Dallas", "state": "Texas"},
                    "medications": ["Metoprolol", "Lisinopril", "Atorvastatin", "Metformin", "aspirin", "Jardiance"],
                    "comorbidities": ["diabetes", "hypertension"]
                },
                expected_confidence_range=(0.8, 1.0),
                difficulty_level="medium",
                test_category="extraction_accuracy"
            ),
            
            # Test 8: Creative interpretation test (should show differences)
            PromptTestCase(
                name="Creative_Interpretation_Test",
                transcript="""
                Patient presents with unusual symptoms. Has been experiencing intermittent episodes 
                of confusion and memory lapses over the past 6 months. Family reports personality 
                changes. 72-year-old female from rural Montana. Takes various supplements.
                """,
                expected_extraction={
                    "age": 72,
                    "gender": "FEMALE",
                    "primary_diagnosis": None,  # Should be ambiguous
                    "conditions": ["confusion", "memory lapses", "personality changes"],
                    "location": {"state": "Montana"},
                    "medications": ["supplements"]
                },
                expected_confidence_range=(0.3, 0.6),
                difficulty_level="hard",
                test_category="edge_cases"
            )
        ]
    
    async def evaluate_current_prompts(self) -> Dict[str, Any]:
        """Evaluate the current prompts used in production"""
        print("🧪 Evaluating Current Production Prompts...")
        print("=" * 60)
        
        test_cases = self.get_prompt_test_cases()
        all_results = []
        
        for test_case in test_cases:
            print(f"\n🔬 Testing: {test_case.name}")
            print(f"📝 Category: {test_case.test_category} | Difficulty: {test_case.difficulty_level}")
            
            # Test with OpenAI if available
            if self.openai_provider:
                result = await self._evaluate_prompt_with_provider(
                    test_case, self.openai_provider, "current_openai"
                )
                all_results.append(result)
                print(f"   OpenAI: {'✅' if result.success else '❌'} Score: {result.extraction_accuracy:.3f} | Confidence: {result.confidence_score:.3f}")
                if result.success:
                    print(f"     Primary diagnosis: {result.extracted_data.get('primary_diagnosis', 'None')}")
            
            # Test with Claude if available  
            if self.claude_provider:
                result = await self._evaluate_prompt_with_provider(
                    test_case, self.claude_provider, "current_claude"
                )
                all_results.append(result)
                print(f"   Claude: {'✅' if result.success else '❌'} Score: {result.extraction_accuracy:.3f} | Confidence: {result.confidence_score:.3f}")
                if result.success:
                    print(f"     Primary diagnosis: {result.extracted_data.get('primary_diagnosis', 'None')}")
        
        # Analyze results
        analysis = self._analyze_prompt_performance(all_results)
        self._print_prompt_analysis(analysis)
        
        return {
            "prompt_analysis": analysis,
            "detailed_results": [self._result_to_dict(r) for r in all_results]
        }
    
    async def _evaluate_prompt_with_provider(
        self, 
        test_case: PromptTestCase, 
        provider, 
        prompt_version: str
    ) -> PromptEvaluationResult:
        """Evaluate a single test case with a specific provider"""
        start_time = time.time()
        errors = []
        
        try:
            # Call the provider directly to bypass router and test actual prompts
            extraction_result = await provider.extract_patient_data(test_case.transcript)
            execution_time = int((time.time() - start_time) * 1000)
            
            if not extraction_result.success:
                return PromptEvaluationResult(
                    test_case_name=test_case.name,
                    provider=provider.provider_name,
                    prompt_version=prompt_version,
                    success=False,
                    extraction_accuracy=0.0,
                    confidence_score=0.0,
                    execution_time_ms=execution_time,
                    extracted_data={},
                    expected_data=test_case.expected_extraction,
                    errors=[extraction_result.error_message or "Unknown error"]
                )
            
            # Calculate accuracy score
            accuracy = self._calculate_extraction_accuracy(
                test_case.expected_extraction,
                extraction_result.patient_data.dict()
            )
            
            # Validate confidence score is in expected range
            confidence_in_range = (
                test_case.expected_confidence_range[0] <= 
                extraction_result.confidence_scores.overall <= 
                test_case.expected_confidence_range[1]
            )
            
            if not confidence_in_range:
                errors.append(
                    f"Confidence {extraction_result.confidence_scores.overall:.3f} "
                    f"outside expected range {test_case.expected_confidence_range}"
                )
            
            return PromptEvaluationResult(
                test_case_name=test_case.name,
                provider=provider.provider_name,
                prompt_version=prompt_version,
                success=True,
                extraction_accuracy=accuracy,
                confidence_score=extraction_result.confidence_scores.overall,
                execution_time_ms=execution_time,
                extracted_data=extraction_result.patient_data.dict(),
                expected_data=test_case.expected_extraction,
                errors=errors
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return PromptEvaluationResult(
                test_case_name=test_case.name,
                provider=provider.provider_name if hasattr(provider, 'provider_name') else "unknown",
                prompt_version=prompt_version,
                success=False,
                extraction_accuracy=0.0,
                confidence_score=0.0,
                execution_time_ms=execution_time,
                extracted_data={},
                expected_data=test_case.expected_extraction,
                errors=[str(e)]
            )
    
    def _calculate_extraction_accuracy(self, expected: Dict, actual: Dict) -> float:
        """Calculate how accurately the prompt extracted the expected information"""
        if not expected:
            return 1.0
        
        total_score = 0
        total_weight = 0
        
        # Field weights for importance
        field_weights = {
            "age": 0.15,
            "gender": 0.10,
            "primary_diagnosis": 0.30,  # Most important
            "cancer_stage": 0.15,
            "location": 0.10,
            "medications": 0.10,
            "allergies": 0.05,
            "comorbidities": 0.05
        }
        
        for field, weight in field_weights.items():
            if field in expected:
                total_weight += weight
                
                if field not in actual:
                    continue  # Miss = 0 points
                
                expected_val = expected[field]
                actual_val = actual[field]
                
                if expected_val is None:
                    # Expected None - check if actual is also None/empty
                    if actual_val is None or actual_val == "" or actual_val == []:
                        total_score += weight
                elif field == "location":
                    # Special location comparison
                    if self._compare_locations(expected_val, actual_val):
                        total_score += weight
                elif field in ["medications", "allergies", "comorbidities", "conditions"]:
                    # List comparison with partial credit
                    overlap = self._calculate_list_overlap(expected_val, actual_val)
                    total_score += weight * overlap
                elif field == "tumor_markers":
                    # Dictionary comparison
                    overlap = self._compare_tumor_markers(expected_val, actual_val)
                    total_score += weight * overlap
                else:
                    # String comparison (case-insensitive, normalized)
                    if self._normalize_text(expected_val) == self._normalize_text(actual_val):
                        total_score += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _compare_locations(self, expected: Dict, actual: Dict) -> bool:
        """Compare location dictionaries"""
        if not expected or not actual:
            return expected == actual
        
        city_match = (
            self._normalize_text(expected.get("city", "")) == 
            self._normalize_text(actual.get("city", ""))
        )
        
        state_match = (
            self._normalize_text(expected.get("state", "")) == 
            self._normalize_text(actual.get("state", ""))
        )
        
        return city_match and state_match
    
    def _calculate_list_overlap(self, expected: List, actual: List) -> float:
        """Calculate overlap between two lists"""
        if not expected:
            return 1.0 if not actual else 0.5
        if not actual:
            return 0.0
        
        expected_norm = [self._normalize_text(str(item)) for item in expected]
        actual_norm = [self._normalize_text(str(item)) for item in actual]
        
        matches = 0
        for exp_item in expected_norm:
            if any(exp_item in act_item or act_item in exp_item for act_item in actual_norm):
                matches += 1
        
        return matches / len(expected_norm)
    
    def _compare_tumor_markers(self, expected: Dict, actual: Dict) -> float:
        """Compare tumor marker dictionaries"""
        if not expected:
            return 1.0 if not actual else 0.5
        if not actual:
            return 0.0
        
        matches = 0
        for key, expected_val in expected.items():
            if key in actual:
                if self._normalize_text(expected_val) == self._normalize_text(actual[key]):
                    matches += 1
        
        return matches / len(expected)
    
    def _normalize_text(self, text: Any) -> str:
        """Normalize text for comparison"""
        if text is None:
            return ""
        return str(text).lower().strip()
    
    def _analyze_prompt_performance(self, results: List[PromptEvaluationResult]) -> Dict[str, Any]:
        """Analyze overall prompt performance"""
        if not results:
            return {}
        
        successful_results = [r for r in results if r.success]
        
        # Overall metrics
        overall_success_rate = len(successful_results) / len(results)
        avg_accuracy = statistics.mean([r.extraction_accuracy for r in successful_results]) if successful_results else 0
        avg_execution_time = statistics.mean([r.execution_time_ms for r in results])
        
        # Provider comparison
        provider_stats = {}
        for result in results:
            provider = result.provider
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "total": 0, "successful": 0, "accuracy_scores": [], "confidence_scores": []
                }
            
            provider_stats[provider]["total"] += 1
            if result.success:
                provider_stats[provider]["successful"] += 1
                provider_stats[provider]["accuracy_scores"].append(result.extraction_accuracy)
                provider_stats[provider]["confidence_scores"].append(result.confidence_score)
        
        # Calculate provider averages
        for provider in provider_stats:
            stats = provider_stats[provider]
            stats["success_rate"] = stats["successful"] / stats["total"]
            stats["avg_accuracy"] = statistics.mean(stats["accuracy_scores"]) if stats["accuracy_scores"] else 0
            stats["avg_confidence"] = statistics.mean(stats["confidence_scores"]) if stats["confidence_scores"] else 0
        
        # Category analysis
        category_stats = {}
        for result in results:
            # Extract category from test case name
            test_case = next(tc for tc in self.get_prompt_test_cases() if tc.name == result.test_case_name)
            category = test_case.test_category
            
            if category not in category_stats:
                category_stats[category] = {"total": 0, "successful": 0, "accuracy_scores": []}
            
            category_stats[category]["total"] += 1
            if result.success:
                category_stats[category]["successful"] += 1
                category_stats[category]["accuracy_scores"].append(result.extraction_accuracy)
        
        # Consistency analysis (compare Test A vs Test B)
        consistency_score = self._analyze_consistency(results)
        
        # Identify worst performing cases
        worst_cases = sorted(
            [r for r in results if r.success], 
            key=lambda x: x.extraction_accuracy
        )[:3]
        
        return {
            "overall_metrics": {
                "success_rate": overall_success_rate,
                "average_accuracy": avg_accuracy,
                "average_execution_time_ms": avg_execution_time,
                "total_tests": len(results)
            },
            "provider_comparison": provider_stats,
            "category_performance": category_stats,
            "consistency_score": consistency_score,
            "improvement_opportunities": [
                {
                    "test_case": r.test_case_name,
                    "accuracy": r.extraction_accuracy,
                    "errors": r.errors
                }
                for r in worst_cases
            ]
        }
    
    def _analyze_consistency(self, results: List[PromptEvaluationResult]) -> float:
        """Analyze consistency between similar test cases"""
        consistency_a = next((r for r in results if r.test_case_name == "Consistency_Test_A"), None)
        consistency_b = next((r for r in results if r.test_case_name == "Consistency_Test_B"), None)
        
        if not (consistency_a and consistency_b and consistency_a.success and consistency_b.success):
            return 0.0
        
        # Compare the extraction accuracy difference
        accuracy_diff = abs(consistency_a.extraction_accuracy - consistency_b.extraction_accuracy)
        consistency_score = max(0, 1.0 - accuracy_diff)
        
        return consistency_score
    
    def _print_prompt_analysis(self, analysis: Dict[str, Any]):
        """Print detailed prompt analysis"""
        print("\n" + "=" * 60)
        print("📊 PROMPT EVALUATION ANALYSIS")
        print("=" * 60)
        
        overall = analysis["overall_metrics"]
        print(f"📈 Overall Performance:")
        print(f"   • Success Rate: {overall['success_rate']:.1%}")
        print(f"   • Average Accuracy: {overall['average_accuracy']:.3f}")
        print(f"   • Avg Execution Time: {overall['average_execution_time_ms']:.0f}ms")
        
        print(f"\n🤖 Provider Comparison:")
        for provider, stats in analysis["provider_comparison"].items():
            print(f"   • {provider.upper()}:")
            print(f"     - Success Rate: {stats['success_rate']:.1%}")
            print(f"     - Avg Accuracy: {stats['avg_accuracy']:.3f}")
            print(f"     - Avg Confidence: {stats['avg_confidence']:.3f}")
        
        print(f"\n📋 Category Performance:")
        for category, stats in analysis["category_performance"].items():
            success_rate = stats["successful"] / stats["total"]
            avg_accuracy = statistics.mean(stats["accuracy_scores"]) if stats["accuracy_scores"] else 0
            print(f"   • {category}: {success_rate:.1%} success, {avg_accuracy:.3f} accuracy")
        
        print(f"\n🔄 Consistency Score: {analysis['consistency_score']:.3f}")
        
        if analysis["improvement_opportunities"]:
            print(f"\n💡 Improvement Opportunities:")
            for opp in analysis["improvement_opportunities"]:
                print(f"   • {opp['test_case']}: {opp['accuracy']:.3f} accuracy")
                if opp["errors"]:
                    print(f"     Errors: {', '.join(opp['errors'])}")
    
    def _result_to_dict(self, result: PromptEvaluationResult) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization"""
        return {
            "test_case_name": result.test_case_name,
            "provider": result.provider,
            "prompt_version": result.prompt_version,
            "success": result.success,
            "extraction_accuracy": result.extraction_accuracy,
            "confidence_score": result.confidence_score,
            "execution_time_ms": result.execution_time_ms,
            "errors": result.errors
        }
    
    def _generate_html_report(self, results: Dict[str, Any], timestamp: int) -> str:
        """Generate an interactive HTML report"""
        analysis = results["prompt_analysis"]
        detailed_results = results["detailed_results"]
        
        # Group results by test case for easier visualization
        test_cases = {}
        for result in detailed_results:
            test_name = result["test_case_name"]
            if test_name not in test_cases:
                test_cases[test_name] = []
            test_cases[test_name].append(result)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Prompt Evaluation Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .test-case {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .test-case h3 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        .provider-results {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        .provider-result {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #28a745;
        }}
        .provider-result.failed {{
            border-left-color: #dc3545;
        }}
        .score-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            color: white;
        }}
        .score-excellent {{ background-color: #28a745; }}
        .score-good {{ background-color: #17a2b8; }}
        .score-fair {{ background-color: #ffc107; color: #333; }}
        .score-poor {{ background-color: #dc3545; }}
        .recommendations {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
        }}
        .recommendations h3 {{
            color: #856404;
            margin-top: 0;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 10px;
        }}
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .comparison-table th,
        .comparison-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .comparison-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .comparison-table tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 LLM Prompt Evaluation Report</h1>
            <p>Generated on {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}</p>
        </div>
        
        <div class="content">
            <!-- Overall Metrics -->
            <div class="section">
                <h2>📊 Overall Performance</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{analysis['overall_metrics']['success_rate']:.1%}</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{analysis['overall_metrics']['average_accuracy']:.3f}</div>
                        <div class="metric-label">Average Accuracy</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{analysis['overall_metrics']['average_execution_time_ms']:.0f}ms</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{analysis['overall_metrics']['total_tests']}</div>
                        <div class="metric-label">Total Tests</div>
                    </div>
                </div>
            </div>
            
            <!-- Provider Comparison Chart -->
            <div class="section">
                <h2>🤖 Provider Comparison</h2>
                <div class="chart-container">
                    <canvas id="providerChart"></canvas>
                </div>
                
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Provider</th>
                            <th>Success Rate</th>
                            <th>Avg Accuracy</th>
                            <th>Avg Confidence</th>
                            <th>Tests Run</th>
                        </tr>
                    </thead>
                    <tbody>"""
        
        # Add provider comparison rows
        for provider, stats in analysis["provider_comparison"].items():
            html += f"""
                        <tr>
                            <td><strong>{provider.upper()}</strong></td>
                            <td>{stats['success_rate']:.1%}</td>
                            <td>{stats['avg_accuracy']:.3f}</td>
                            <td>{stats['avg_confidence']:.3f}</td>
                            <td>{stats['total']}</td>
                        </tr>"""
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <!-- Category Performance Chart -->
            <div class="section">
                <h2>📋 Performance by Category</h2>
                <div class="chart-container">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>
            
            <!-- Detailed Test Results -->
            <div class="section">
                <h2>🔬 Detailed Test Results</h2>"""
        
        # Add detailed test results
        for test_name, test_results in test_cases.items():
            # Get test case details
            test_case = next(tc for tc in self.get_prompt_test_cases() if tc.name == test_name)
            
            html += f"""
                <div class="test-case">
                    <h3>{test_name}</h3>
                    <p><strong>Category:</strong> {test_case.test_category} | <strong>Difficulty:</strong> {test_case.difficulty_level}</p>
                    <p><strong>Transcript:</strong> {test_case.transcript[:200]}...</p>
                    
                    <div class="provider-results">"""
            
            for result in test_results:
                success_class = "" if result["success"] else "failed"
                score_class = self._get_score_class(result["extraction_accuracy"])
                
                html += f"""
                        <div class="provider-result {success_class}">
                            <h4>{result['provider'].upper()}</h4>
                            <p><strong>Score:</strong> <span class="score-badge {score_class}">{result['extraction_accuracy']:.3f}</span></p>
                            <p><strong>Confidence:</strong> {result['confidence_score']:.3f}</p>
                            <p><strong>Time:</strong> {result['execution_time_ms']}ms</p>
                            {f'<p><strong>Errors:</strong> {", ".join(result["errors"])}</p>' if result["errors"] else ''}
                        </div>"""
            
            html += """
                    </div>
                </div>"""
        
        # Add recommendations
        html += f"""
            </div>
            
            <!-- Recommendations -->
            <div class="section">
                <div class="recommendations">
                    <h3>💡 Recommendations</h3>
                    <ul>"""
        
        if analysis["consistency_score"] < 0.8:
            html += f"""
                        <li><strong>Improve Consistency:</strong> Consistency score is {analysis['consistency_score']:.3f}. Consider refining prompts for more consistent results across similar inputs.</li>"""
        
        if analysis["overall_metrics"]["average_accuracy"] < 0.8:
            html += f"""
                        <li><strong>Enhance Accuracy:</strong> Average accuracy is {analysis['overall_metrics']['average_accuracy']:.3f}. Review prompt engineering for better extraction performance.</li>"""
        
        for opp in analysis["improvement_opportunities"]:
            if opp["accuracy"] < 0.7:
                html += f"""
                        <li><strong>Address {opp['test_case']}:</strong> Low accuracy ({opp['accuracy']:.3f}). {opp['errors'][0] if opp['errors'] else 'Consider prompt refinement for this scenario.'}</li>"""
        
        html += """
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Provider Comparison Chart
        const providerCtx = document.getElementById('providerChart').getContext('2d');
        new Chart(providerCtx, {
            type: 'bar',
            data: {
                labels: ['Success Rate', 'Avg Accuracy', 'Avg Confidence'],
                datasets: ["""
        
        # Add provider datasets for chart
        colors = ['#667eea', '#764ba2', '#f093fb']
        for i, (provider, stats) in enumerate(analysis["provider_comparison"].items()):
            html += f"""
                    {{
                        label: '{provider.upper()}',
                        data: [{stats['success_rate']:.3f}, {stats['avg_accuracy']:.3f}, {stats['avg_confidence']:.3f}],
                        backgroundColor: '{colors[i % len(colors)]}',
                        borderColor: '{colors[i % len(colors)]}',
                        borderWidth: 1
                    }}{',' if i < len(analysis['provider_comparison']) - 1 else ''}"""
        
        html += """
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
        
        // Category Performance Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: ["""
        
        # Add category labels and data
        categories = list(analysis["category_performance"].keys())
        html += "'" + "', '".join(categories) + "'"
        
        html += """],
                datasets: [{
                    data: ["""
        
        category_scores = []
        for category in categories:
            stats = analysis["category_performance"][category]
            avg_score = statistics.mean(stats["accuracy_scores"]) if stats["accuracy_scores"] else 0
            category_scores.append(f"{avg_score:.3f}")
        
        html += ", ".join(category_scores)
        
        html += f"""],
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0'],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score badge based on score value"""
        if score >= 0.9:
            return "score-excellent"
        elif score >= 0.75:
            return "score-good"
        elif score >= 0.5:
            return "score-fair"
        else:
            return "score-poor"

async def main():
    """Run prompt evaluation"""
    evaluator = PromptEvaluator()
    results = await evaluator.evaluate_current_prompts()
    
    # Save results
    timestamp = int(time.time())
    results_file = f"prompt_evaluation_{timestamp}.json"
    html_file = f"prompt_evaluation_{timestamp}.html"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate HTML report
    html_content = evaluator._generate_html_report(results, timestamp)
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print(f"🌐 Visual report saved to: {html_file}")
    print(f"📋 Open {html_file} in your browser to view the interactive report")
    return results

if __name__ == "__main__":
    asyncio.run(main())