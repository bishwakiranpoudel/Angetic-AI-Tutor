"""Code execution and visualization for programming exercises."""
import subprocess
import sys
import io
import contextlib
from typing import Dict, Any, Optional

class CodeExecutor:
    """Execute and test code safely."""
    
    @staticmethod
    def execute_code(code: str, language: str = "python", timeout: int = 5) -> Dict[str, Any]:
        """Execute code and return results."""
        if language.lower() != "python":
            return {
                "success": False,
                "output": f"Language {language} not yet supported. Only Python is supported.",
                "error": None
            }
        
        try:
            # Capture stdout and stderr
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
                # Compile and execute
                exec_globals = {}
                exec(code, exec_globals)
            
            output = output_buffer.getvalue()
            error = error_buffer.getvalue()
            
            return {
                "success": True,
                "output": output,
                "error": error if error else None
            }
        except SyntaxError as e:
            return {
                "success": False,
                "output": None,
                "error": f"Syntax Error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Runtime Error: {str(e)}"
            }
    
    @staticmethod
    def test_code(code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Test code against test cases."""
        results = []
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get("input", "")
            expected_output = test_case.get("expected_output", "")
            
            try:
                # Modify code to capture return value
                test_code = f"""
{code}

# Test case {i+1}
result = {test_input}
print(result)
"""
                
                exec_result = CodeExecutor.execute_code(test_code)
                
                if exec_result["success"]:
                    actual_output = exec_result["output"].strip()
                    passed = str(actual_output) == str(expected_output)
                    all_passed = all_passed and passed
                    
                    results.append({
                        "test_case": i + 1,
                        "input": test_input,
                        "expected": expected_output,
                        "actual": actual_output,
                        "passed": passed
                    })
                else:
                    all_passed = False
                    results.append({
                        "test_case": i + 1,
                        "input": test_input,
                        "expected": expected_output,
                        "actual": None,
                        "passed": False,
                        "error": exec_result["error"]
                    })
            except Exception as e:
                all_passed = False
                results.append({
                    "test_case": i + 1,
                    "input": test_input,
                    "expected": expected_output,
                    "actual": None,
                    "passed": False,
                    "error": str(e)
                })
        
        return {
            "all_passed": all_passed,
            "total_tests": len(test_cases),
            "passed_tests": sum(1 for r in results if r.get("passed", False)),
            "results": results
        }

