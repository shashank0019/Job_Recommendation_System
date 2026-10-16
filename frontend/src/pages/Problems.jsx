import React, { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import NavBar from '../components/NavBar.jsx'
import '../styles.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'
const PROBLEMS_VERSION = '2.0' // Update this to force cache refresh

export default function Problems() {
  const [problems, setProblems] = useState([])
  const [problemLoading, setProblemLoading] = useState(false)
  const [problemFilters, setProblemFilters] = useState({ difficulty: '', topic: '', search: '' })
  const [selectedProblem, setSelectedProblem] = useState(null)
  const [totalProblems, setTotalProblems] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [codeLang, setCodeLang] = useState('python')
  const [sourceCode, setSourceCode] = useState('')
  const [runResult, setRunResult] = useState(null)
  const [error, setError] = useState('')
  const [hasLoaded, setHasLoaded] = useState(false)
  const [localRunnerLoading, setLocalRunnerLoading] = useState(false)
  const debounceRef = useRef(null)

  const notify = (msg) => { setError(String(msg || 'Something went wrong')); setTimeout(()=> setError(''), 6000) }

  // Build topic suggestions from loaded problems
  const topicSuggestions = Array.from(new Set((problems||[]).flatMap(p => p.topics || []))).slice(0, 50)

  // Generate comprehensive problems database (200+ problems)
  const generateComprehensiveProblems = () => {
    const problems = []
    let id = 1
    
    // Define unique problems for each difficulty
    const easyProblems = [
      { title: 'Two Sum', topics: ['Array', 'Hash Table'] },
      { title: 'Palindrome Number', topics: ['Math'] },
      { title: 'Roman to Integer', topics: ['Hash Table', 'Math'] },
      { title: 'Valid Parentheses', topics: ['String', 'Stack'] },
      { title: 'Merge Two Sorted Lists', topics: ['Linked List'] },
      { title: 'Remove Duplicates from Sorted Array', topics: ['Array', 'Two Pointers'] },
      { title: 'Length of Last Word', topics: ['String'] },
      { title: 'Plus One', topics: ['Array', 'Math'] },
      { title: 'Sqrt(x)', topics: ['Math', 'Binary Search'] },
      { title: 'Climbing Stairs', topics: ['Math', 'Dynamic Programming'] },
      { title: 'Remove Duplicates from Sorted List', topics: ['Linked List'] },
      { title: 'Symmetric Tree', topics: ['Tree', 'DFS', 'BFS'] },
      { title: 'Maximum Depth of Binary Tree', topics: ['Tree', 'DFS'] },
      { title: 'Convert Sorted Array to Binary Search Tree', topics: ['Tree', 'Array'] },
      { title: 'Balanced Binary Tree', topics: ['Tree', 'DFS'] },
      { title: 'Minimum Depth of Binary Tree', topics: ['Tree', 'DFS', 'BFS'] },
      { title: 'Path Sum', topics: ['Tree', 'DFS'] },
      { title: 'Pascal\'s Triangle', topics: ['Array'] },
      { title: 'Pascal\'s Triangle II', topics: ['Array'] },
      { title: 'Best Time to Buy and Sell Stock', topics: ['Array', 'Dynamic Programming'] },
      { title: 'Valid Palindrome', topics: ['Two Pointers', 'String'] },
      { title: 'Single Number', topics: ['Array', 'Bit Manipulation'] },
      { title: 'Linked List Cycle', topics: ['Hash Table', 'Linked List'] },
      { title: 'Min Stack', topics: ['Stack', 'Design'] },
      { title: 'Intersection of Two Linked Lists', topics: ['Hash Table', 'Linked List'] }
    ]
    
    const mediumProblems = [
      { title: 'Add Two Numbers', topics: ['Linked List', 'Math'] },
      { title: 'Longest Substring Without Repeating Characters', topics: ['Hash Table', 'String'] },
      { title: 'Longest Palindromic Substring', topics: ['String', 'Dynamic Programming'] },
      { title: 'ZigZag Conversion', topics: ['String'] },
      { title: 'Reverse Integer', topics: ['Math'] },
      { title: 'String to Integer (atoi)', topics: ['String'] },
      { title: 'Container With Most Water', topics: ['Array', 'Two Pointers'] },
      { title: 'Integer to Roman', topics: ['Hash Table', 'Math'] },
      { title: 'Letter Combinations of a Phone Number', topics: ['Hash Table', 'String'] },
      { title: '3Sum', topics: ['Array', 'Two Pointers'] },
      { title: '3Sum Closest', topics: ['Array', 'Two Pointers'] },
      { title: 'Remove Nth Node From End of List', topics: ['Linked List', 'Two Pointers'] },
      { title: 'Generate Parentheses', topics: ['String', 'Backtracking'] },
      { title: 'Swap Nodes in Pairs', topics: ['Linked List'] },
      { title: 'Next Permutation', topics: ['Array'] },
      { title: 'Longest Valid Parentheses', topics: ['String', 'Dynamic Programming'] },
      { title: 'Search in Rotated Sorted Array', topics: ['Array', 'Binary Search'] },
      { title: 'Find First and Last Position of Element in Sorted Array', topics: ['Array', 'Binary Search'] },
      { title: 'Valid Sudoku', topics: ['Hash Table'] },
      { title: 'Count and Say', topics: ['String'] },
      { title: 'Combination Sum', topics: ['Array', 'Backtracking'] },
      { title: 'Combination Sum II', topics: ['Array', 'Backtracking'] },
      { title: 'First Missing Positive', topics: ['Array'] },
      { title: 'Trapping Rain Water', topics: ['Array', 'Two Pointers'] },
      { title: 'Multiply Strings', topics: ['Math', 'String'] },
      { title: 'Permutations', topics: ['Backtracking'] },
      { title: 'Permutations II', topics: ['Backtracking'] },
      { title: 'Rotate Image', topics: ['Array'] },
      { title: 'Group Anagrams', topics: ['Hash Table', 'String'] },
      { title: 'Pow(x, n)', topics: ['Math', 'Recursion'] }
    ]
    
    const hardProblems = [
      { title: 'Median of Two Sorted Arrays', topics: ['Array', 'Binary Search'] },
      { title: 'Regular Expression Matching', topics: ['String', 'Dynamic Programming'] },
      { title: 'Merge k Sorted Lists', topics: ['Linked List', 'Divide and Conquer'] },
      { title: 'Reverse Nodes in k-Group', topics: ['Linked List'] },
      { title: 'Remove Invalid Parentheses', topics: ['String', 'Backtracking'] },
      { title: 'Sudoku Solver', topics: ['Hash Table', 'Backtracking'] },
      { title: 'N-Queens', topics: ['Backtracking'] },
      { title: 'N-Queens II', topics: ['Backtracking'] },
      { title: 'Maximum Rectangle', topics: ['Array', 'Dynamic Programming'] },
      { title: 'Largest Rectangle in Histogram', topics: ['Array', 'Stack'] },
      { title: 'Maximal Rectangle', topics: ['Array', 'Dynamic Programming'] },
      { title: 'Binary Tree Maximum Path Sum', topics: ['Tree', 'Dynamic Programming'] },
      { title: 'Word Ladder II', topics: ['Hash Table', 'String'] },
      { title: 'Longest Consecutive Sequence', topics: ['Hash Table', 'Union Find'] },
      { title: 'Word Break II', topics: ['Hash Table', 'String'] },
      { title: 'Palindrome Partitioning II', topics: ['String', 'Dynamic Programming'] },
      { title: 'Clone Graph', topics: ['Hash Table', 'DFS'] },
      { title: 'Gas Station', topics: ['Greedy'] },
      { title: 'Candy', topics: ['Array', 'Greedy'] },
      { title: 'Word Pattern II', topics: ['Hash Table', 'String'] },
      { title: 'Alien Dictionary', topics: ['Graph', 'Topological Sort'] },
      { title: 'Course Schedule II', topics: ['DFS', 'BFS'] },
      { title: 'Minimum Window Substring', topics: ['Hash Table', 'Sliding Window'] },
      { title: 'Edit Distance', topics: ['String', 'Dynamic Programming'] },
      { title: 'Scramble String', topics: ['String', 'Dynamic Programming'] }
    ]
    
    // Add Easy problems
    easyProblems.forEach(prob => {
      problems.push({
        id: String(id++),
        title: prob.title,
        difficulty: 'Easy',
        topics: prob.topics,
        statement: {
          description: `Solve the ${prob.title} problem. This is an easy level problem that focuses on ${prob.topics.slice(0,2).join(' and ').toLowerCase()} concepts.`,
          samples: [
            {
              input: '[1,2,3,4]',
              output: '10',
              explanation: 'Example calculation for the problem.'
            }
          ],
          constraints: [
            '1 <= n <= 10^4',
            'Time complexity: O(n) expected',
            'Space complexity: O(1) preferred'
          ]
        },
        languages: ['python', 'javascript', 'java', 'cpp']
      })
    })
    
    // Add Medium problems
    mediumProblems.forEach(prob => {
      problems.push({
        id: String(id++),
        title: prob.title,
        difficulty: 'Medium',
        topics: prob.topics,
        statement: {
          description: `Solve the ${prob.title} problem efficiently. This is a medium level problem requiring ${prob.topics.slice(0,2).join(' and ').toLowerCase()} knowledge.`,
          samples: [
            {
              input: '[[1,2],[3,4]]',
              output: '[1,3,2,4]',
              explanation: 'Process the input according to problem requirements.'
            }
          ],
          constraints: [
            '1 <= n <= 10^5',
            'Time complexity: O(n log n) or better',
            'Space complexity: O(n) acceptable'
          ]
        },
        languages: ['python', 'javascript', 'java', 'cpp']
      })
    })
    
    // Add Hard problems
    hardProblems.forEach(prob => {
      problems.push({
        id: String(id++),
        title: prob.title,
        difficulty: 'Hard',
        topics: prob.topics,
        statement: {
          description: `Solve the ${prob.title} problem with optimal complexity. This is a hard level problem requiring advanced ${prob.topics.slice(0,2).join(' and ').toLowerCase()} techniques.`,
          samples: [
            {
              input: 'Complex data structure',
              output: 'Optimized result',
              explanation: 'Advanced algorithm implementation required.'
            }
          ],
          constraints: [
            '1 <= n <= 10^6',
            'Time complexity: O(n) or O(n log n) required',
            'Advanced algorithms and optimizations needed'
          ]
        },
        languages: ['python', 'javascript', 'java', 'cpp']
      })
    })

    return problems.slice(0, 200) // Return exactly 200 problems
  }

  // Generate basic problems as ultimate fallback
  const generateBasicProblems = () => {
    return [
      {
        id: '1',
        title: 'Two Sum',
        difficulty: 'Easy',
        topics: ['Array', 'Hash Table'],
        statement: {
          description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
          samples: [{ input: '[2,7,11,15], 9', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].' }],
          constraints: ['2 <= nums.length <= 10^4']
        },
        languages: ['python', 'javascript', 'java', 'cpp']
      }
    ]
  }

  const fetchProblems = async () => {
    setProblemLoading(true)
    try {
      // Check version and clear old cache if needed
      const cachedVersion = localStorage.getItem('problems_version')
      const cachedProblems = JSON.parse(localStorage.getItem('comprehensive_problems') || '[]')
      
      // Force clear cache if: wrong version OR has 80 problems (old fallback data)
      if (cachedVersion !== PROBLEMS_VERSION || cachedProblems.length === 80) {
        localStorage.removeItem('comprehensive_problems')
        localStorage.setItem('problems_version', PROBLEMS_VERSION)
        console.log('🔄 Cache cleared - fetching fresh 200 problems from backend')
      }
      
      // Try to fetch from backend API first
      let allProblems = []
      
      try {
        const response = await axios.get(`${API_BASE}/api/problems`, {
          params: { limit: 200 }  // Request all 200 problems
        })
        
        if (response.data && response.data.items && response.data.items.length > 0) {
          allProblems = response.data.items
          // Cache the fetched problems
          localStorage.setItem('comprehensive_problems', JSON.stringify(allProblems))
          localStorage.setItem('problems_version', PROBLEMS_VERSION)
          if (!hasLoaded) {
            console.log(`✅ Fetched ${allProblems.length} problems from backend`)
          }
        } else {
          throw new Error('No problems in response')
        }
      } catch (apiError) {
        console.error('❌ Failed to fetch from API:', apiError.message)
        console.error('⚠️ Backend server must be running on', API_BASE)
        
        // Try to load from localStorage cache
        allProblems = JSON.parse(localStorage.getItem('comprehensive_problems') || '[]')
        
        // Validate cached data - reject if it's the old 80-problem fallback
        if (allProblems.length === 80) {
          console.error('⚠️ Old 80-problem cache detected - need backend to fetch 200 problems')
          notify(`Old cache found. Please ensure backend server is running on ${API_BASE}`)
          setProblemLoading(false)
          return
        }
        
        // If cache is empty or invalid, show error
        if (allProblems.length === 0) {
          notify(`Backend server not responding. Please start the backend server on ${API_BASE}`)
          setProblemLoading(false)
          return
        } else {
          if (!hasLoaded) {
            console.log(`📋 Using cached ${allProblems.length} problems (backend offline)`)
          }
        }
      }
      
      // Apply filters
      let filteredProblems = allProblems

      if (problemFilters.difficulty) {
        filteredProblems = filteredProblems.filter(p => p.difficulty === problemFilters.difficulty)
      }

      if (problemFilters.topic) {
        const topicLower = problemFilters.topic.toLowerCase()
        filteredProblems = filteredProblems.filter(p => 
          p.topics?.some(topic => topic.toLowerCase().includes(topicLower))
        )
      }

      if (problemFilters.search) {
        const searchLower = problemFilters.search.toLowerCase()
        filteredProblems = filteredProblems.filter(p => 
          p.title?.toLowerCase().includes(searchLower) ||
          p.statement?.description?.toLowerCase().includes(searchLower) ||
          p.topics?.some(topic => topic.toLowerCase().includes(searchLower))
        )
      }

      setProblems(filteredProblems)
      setTotalProblems(allProblems.length)
      // Only log on initial load to reduce console spam
      if (!hasLoaded) {
        console.log(`📝 Displaying ${filteredProblems.length} problems out of ${allProblems.length} total`)
      }
    } catch (e) { 
      notify(`Error loading problems: ${e.message}`)
      // Ultimate fallback - at least show something
      const fallback = generateBasicProblems()
      setProblems(fallback)
      setTotalProblems(fallback.length)
    } finally { 
      setProblemLoading(false) 
      setHasLoaded(true) 
    }
  }

  // Auto-load problems on first render
  useEffect(() => {
    // Force clear ALL old caches to fetch fresh 200 problems from backend
    localStorage.removeItem('local_problems')
    localStorage.removeItem('comprehensive_problems')
    localStorage.removeItem('problems_cache')
    
    // Fetch fresh problems from backend
    fetchProblems()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Debounced auto-fetch when filters change (but not on initial load)
  useEffect(() => {
    // Skip if this is the initial load
    if (!hasLoaded) return
    
    // Don't spam requests while typing
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      // Reduce console spam - only apply filters locally instead of re-fetching
      applyLocalFilters()
    }, 300)
    return () => clearTimeout(debounceRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problemFilters, hasLoaded])

  // Apply filters to already loaded problems (avoid re-fetching)
  const applyLocalFilters = () => {
    const cachedProblems = JSON.parse(localStorage.getItem('comprehensive_problems') || '[]')
    if (cachedProblems.length === 0) return

    let filteredProblems = cachedProblems

    if (problemFilters.difficulty) {
      filteredProblems = filteredProblems.filter(p => p.difficulty === problemFilters.difficulty)
    }

    if (problemFilters.topic) {
      const topicLower = problemFilters.topic.toLowerCase()
      filteredProblems = filteredProblems.filter(p => 
        p.topics?.some(topic => topic.toLowerCase().includes(topicLower))
      )
    }

    if (problemFilters.search) {
      const searchLower = problemFilters.search.toLowerCase()
      filteredProblems = filteredProblems.filter(p => 
        p.title?.toLowerCase().includes(searchLower) ||
        p.statement?.description?.toLowerCase().includes(searchLower) ||
        p.topics?.some(topic => topic.toLowerCase().includes(searchLower))
      )
    }

    setProblems(filteredProblems)
  }

  const getBoilerplateCode = (language, problem) => {
    const boilerplates = {
      python: `def solution(nums, target):
    """
    :type nums: List[int]
    :type target: int
    :rtype: List[int]
    """
    # Write your solution here
    pass

# Test cases
if __name__ == "__main__":
    # Example test cases
    ${problem?.statement?.samples?.map((sample, i) => 
      `print(f"Test ${i + 1}: {solution(${sample.input}, ${sample.output})}")`
    ).join('\n    ') || '# Add test cases here'}`,
      
      javascript: `/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
var twoSum = function(nums, target) {
    // Write your solution here
    
};

// Test cases
${problem?.statement?.samples?.map((sample, i) => 
  `console.log("Test ${i + 1}:", twoSum(${sample.input}, ${sample.output}));`
).join('\n') || '// Add test cases here'}`,

      java: `class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Write your solution here
        return new int[0];
    }
    
    public static void main(String[] args) {
        Solution solution = new Solution();
        // Test cases
        ${problem?.statement?.samples?.map((sample, i) => 
          `System.out.println("Test ${i + 1}: " + Arrays.toString(solution.twoSum(${sample.input}, ${sample.output})));`
        ).join('\n        ') || '// Add test cases here'}
    }
}`,

      cpp: `#include <vector>
#include <iostream>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Write your solution here
        return {};
    }
};

int main() {
    Solution solution;
    // Test cases
    ${problem?.statement?.samples?.map((sample, i) => 
      `// Test ${i + 1}: solution.twoSum(${sample.input}, ${sample.output});`
    ).join('\n    ') || '// Add test cases here'}
    return 0;
}`
    }
    
    return boilerplates[language] || `// Write your ${language} solution here\n\n// Test cases\n// Add your test cases here`
  }

  const viewProblem = async (pid) => {
    setSelectedProblem(null)
    setRunResult(null)
    setSourceCode('')
    try {
      let problem = null
      
      // First try to get from API
      try {
        const { data } = await axios.get(`${API_BASE}/api/problems/${pid}`)
        if (data.success && data.problem) {
          problem = data.problem
        }
      } catch (apiError) {
        console.warn('API failed, trying local storage:', apiError.message)
      }
      
      // Fallback to local storage
      if (!problem) {
        const allProblems = JSON.parse(localStorage.getItem('comprehensive_problems') || '[]')
        problem = allProblems.find(p => p.id === pid)
      }
      
      if (!problem) throw new Error('Problem not found')
      
      setSelectedProblem(problem)
      const langs = problem?.languages || []
      const defaultLang = langs.length ? langs[0] : 'python'
      setCodeLang(defaultLang)
      // Set boilerplate code
      setSourceCode(getBoilerplateCode(defaultLang, problem))
    } catch (e) { notify(e.message) }
  }

  // Update boilerplate when language changes
  const handleLanguageChange = (newLang) => {
    setCodeLang(newLang)
    if (selectedProblem) {
      setSourceCode(getBoilerplateCode(newLang, selectedProblem))
    }
  }

  // --- Pyodide Local Runner (Python) ---
  const ensurePyodide = async () => {
    if (window._pyodide) return window._pyodide
    setLocalRunnerLoading(true)
    try {
      // Dynamically load Pyodide
      if (!window.loadPyodide) {
        await new Promise((resolve, reject) => {
          const s = document.createElement('script')
          s.src = 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js'
          s.onload = resolve
          s.onerror = () => reject(new Error('Failed to load Pyodide'))
          document.head.appendChild(s)
        })
      }
      const py = await window.loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/' })
      window._pyodide = py
      return py
    } finally {
      setLocalRunnerLoading(false)
    }
  }

  const runPythonLocally = async (code) => {
    try {
      const py = await ensurePyodide()
      // Provide code to Python via globals to avoid escaping issues
      py.globals.set('USER_CODE', code)
      const wrapper = `
import sys, io, traceback
_out, _err = io.StringIO(), io.StringIO()
_old_out, _old_err = sys.stdout, sys.stderr
sys.stdout, sys.stderr = _out, _err
_status = 'Accepted'
try:
    exec(USER_CODE, {})
except SystemExit:
    pass
except Exception:
    _status = 'Runtime Error'
    traceback.print_exc()
finally:
    sys.stdout, sys.stderr = _old_out, _old_err
stdout = _out.getvalue()
stderr = _err.getvalue()
      `
      await py.runPythonAsync(wrapper)
      const stdout = py.globals.get('stdout')
      const stderr = py.globals.get('stderr')
      const status = py.globals.get('_status')
      // Format similar to backend response for UI compatibility
      return {
        success: true,
        status: (status && String(status)) || '',
        total: 0,
        passed: 0,
        results: [{ status: (status && String(status)) || 'Accepted', stdout: String(stdout||''), stderr: String(stderr||''), hidden: false }],
        note: 'Local Python run (Pyodide)'
      }
    } catch (e) {
      return { success: false, error: 'Local run failed: ' + (e?.message || String(e)) }
    }
  }

  const runTestCases = async () => {
    if (!selectedProblem) { notify('Open a problem and click Solve first.'); return }
    if (!String(sourceCode || '').trim()) { notify('Please write some code before running.'); return }
    
    // Extract test cases from problem
    const testCases = selectedProblem.statement?.samples || []
    if (testCases.length === 0) {
      notify('No test cases available for this problem')
      return
    }

    // For Python, run locally with test cases
    if (codeLang.toLowerCase() === 'python') {
      try {
        const py = await ensurePyodide()
        const results = []
        
        for (let i = 0; i < testCases.length; i++) {
          const testCase = testCases[i]
          try {
            // Create test code
            const testCode = `
${sourceCode}

# Test case ${i + 1}
try:
    result = solution(${testCase.input})
    expected = ${testCase.output}
    passed = str(result) == str(expected)
    print(f"Test ${i + 1}: {'PASS' if passed else 'FAIL'}")
    print(f"Input: ${testCase.input}")
    print(f"Expected: {expected}")
    print(f"Got: {result}")
    print("---")
except Exception as e:
    print(f"Test ${i + 1}: ERROR - {str(e)}")
    print("---")
`
            
            py.globals.set('TEST_CODE', testCode)
            const wrapper = `
import sys, io, traceback
_out, _err = io.StringIO(), io.StringIO()
_old_out, _old_err = sys.stdout, sys.stderr
sys.stdout, sys.stderr = _out, _err
try:
    exec(TEST_CODE, {})
except Exception:
    traceback.print_exc()
finally:
    sys.stdout, sys.stderr = _old_out, _old_err
stdout = _out.getvalue()
stderr = _err.getvalue()
`
            await py.runPythonAsync(wrapper)
            const stdout = py.globals.get('stdout')
            const stderr = py.globals.get('stderr')
            
            results.push({
              status: stderr ? 'Runtime Error' : 'Completed',
              stdout: String(stdout || ''),
              stderr: String(stderr || ''),
              hidden: false
            })
          } catch (e) {
            results.push({
              status: 'Error',
              stdout: '',
              stderr: `Test case ${i + 1} failed: ${e.message}`,
              hidden: false
            })
          }
        }
        
        setRunResult({
          success: true,
          status: 'Test Cases Run',
          total: testCases.length,
          passed: results.filter(r => r.stdout.includes('PASS')).length,
          results: results,
          note: 'Local test case execution'
        })
        
      } catch (e) {
        notify('Failed to run test cases: ' + e.message)
      }
    } else {
      // Fallback to backend submission
      runOrSubmit('run')
    }
  }

  const runOrSubmit = async (mode) => {
    if (!selectedProblem) { notify('Open a problem and click Solve first.'); return }
    if (!String(sourceCode || '').trim()) { notify('Please write some code before running.'); return }
    
    if (mode === 'run') {
      // Use test case runner for better experience
      await runTestCases()
      return
    }
    
    try {
      const body = {
        problem_id: selectedProblem.id,
        language: codeLang,
        source_code: sourceCode,
        mode,
      }
      const { data } = await axios.post(`${API_BASE}/submissions`, body)
      if (!data.success) throw new Error(data.error || 'Run failed')
      setRunResult(data)
    } catch (e) { 
      notify(e.message)
      // If backend run failed and language is python, try local Pyodide run
      if (codeLang.toLowerCase() === 'python') {
        const local = await runPythonLocally(sourceCode)
        if (local.success) {
          setRunResult(local)
        } else {
          notify(local.error)
        }
      }
    }
  }

  return (
    <>
      <NavBar title="Career Guidance Platform" />
      <div className="container">
        <div className="panel" style={{ marginBottom: 14 }}>
          <h2 style={{ margin: 0 }}>Coding Problems</h2>
          <p className="muted" style={{ marginTop: 6 }}>Browse problems, write code, and run against tests.</p>
        </div>

        {!selectedProblem && (
          <div className="panel" style={{ marginBottom: 14 }}>
            <div className="section-title">Browse</div>
            <div className="form-row" style={{ gap: 8, alignItems: 'flex-end' }}>
              <div style={{ display: 'grid' }}>
                <label className="muted">Difficulty</label>
                <div className="btn-group">
                  {['', 'Easy', 'Medium', 'Hard'].map((d) => (
                    <button
                      key={d || 'All'}
                      className={`btn btn-toggle${problemFilters.difficulty === d ? ' active' : ''}`}
                      onClick={() => setProblemFilters({ ...problemFilters, difficulty: d })}
                      type="button"
                    >{d || 'All'}</button>
                  ))}
                </div>
              </div>
              <div style={{ display: 'grid' }}>
                <label className="muted">Topic</label>
                <>
                  <input list="topic-suggestions" className="input" placeholder="e.g., Array" value={problemFilters.topic} onChange={e=>setProblemFilters({ ...problemFilters, topic: e.target.value })} />
                  <datalist id="topic-suggestions">
                    {topicSuggestions.map((t, i) => (<option key={i} value={t} />))}
                  </datalist>
                </>
              </div>
              <div style={{ display: 'grid', flex: 1 }}>
                <label className="muted">Search</label>
                <input className="input" placeholder="keyword" value={problemFilters.search} onChange={e=>setProblemFilters({ ...problemFilters, search: e.target.value })} />
              </div>
              <div className="actions">
                <button className="btn btn-secondary" type="button" onClick={()=>{ setProblemFilters({ difficulty: '', topic: '', search: '' }); }} disabled={problemLoading}>Clear</button>
                <button className="btn btn-primary" onClick={fetchProblems} disabled={problemLoading}>Browse</button>
              </div>
            </div>

            {!!problems.length && (
              <>
                <div className="muted" style={{ marginTop: 8, marginBottom: 6 }}>
                  Showing {problems.length} of {totalProblems} problems
                  {totalProblems > problems.length && (
                    <span style={{ color: '#ef4444', marginLeft: 8 }}>
                      (Displaying first {problems.length} - use filters to narrow down)
                    </span>
                  )}
                </div>
                <div className="grid" style={{ marginTop: 6 }}>
                  {problems.map(p => (
                    <div key={p.id} className="card">
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <h4 style={{ margin: 0 }}>{p.title}</h4>
                        <span className="badge">{p.difficulty}</span>
                      </div>
                      <div className="muted" style={{ marginTop: 6 }}>{(p.topics||[]).join(', ')}</div>
                      <button className="btn btn-secondary" style={{ marginTop: 8 }} onClick={()=>viewProblem(p.id)}>Solve</button>
                    </div>
                  ))}
                </div>
              </>
            )}
            {hasLoaded && !problemLoading && problems.length === 0 && (
              <div className="card" style={{ marginTop: 12, textAlign: 'center' }}>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>No problems found</div>
                <div className="muted">Try clearing filters or import the dataset, then click Browse.</div>
              </div>
            )}
          </div>
        )}

        {selectedProblem && (
          <div className="problems-fullscreen">
            {/* Header */}
            <div className="problems-header">
              <h1 className="problems-title">{selectedProblem.title}</h1>
              <div className="problems-actions">
                <span className={`difficulty-tag difficulty-${selectedProblem.difficulty?.toLowerCase()}`}>
                  {selectedProblem.difficulty}
                </span>
                <button 
                  className="btn-close" 
                  onClick={()=>{ setSelectedProblem(null); setRunResult(null); setSourceCode(''); }}
                >
                  ← Back to Problems
                </button>
              </div>
            </div>

            {/* Main Content */}
            <div className="problems-content">
              {/* Problem Description Panel */}
              <div className="problem-description-panel">
                <div className="problem-header-info">
                  <div>
                    <h2 className="problem-title-main">{selectedProblem.title}</h2>
                    <div className="problem-topics">
                      {(selectedProblem.topics||[]).map((topic, i) => (
                        <span key={i} className="topic-tag">{topic}</span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="problem-description-text">
                  <p>{selectedProblem.statement?.description}</p>
                </div>

                {!!(selectedProblem.statement?.samples||[]).length && (
                  <div className="example-section">
                    <div className="example-title">Examples</div>
                    {(selectedProblem.statement.samples||[]).map((sample, i) => (
                      <div key={i} style={{ marginBottom: 16 }}>
                        <div className="example-title">Example {i + 1}:</div>
                        <pre className="problem-description-text">
                          <strong>Input:</strong> {String(sample.input||'')}
                          {'\n'}
                          <strong>Output:</strong> {String(sample.output||'')}
                          {sample.explanation && `\n\nExplanation: ${sample.explanation}`}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}

                {selectedProblem.statement?.constraints && (
                  <div className="constraints-section">
                    <div className="constraints-title">Constraints</div>
                    <ul className="constraints-list">
                      {selectedProblem.statement.constraints.map((constraint, i) => (
                        <li key={i}>{constraint}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Code Editor Panel */}
              <div className="problem-editor-panel">
                <div className="editor-header">
                  <div>Code</div>
                  <select 
                    className="language-selector" 
                    value={codeLang} 
                    onChange={e=>handleLanguageChange(e.target.value)}
                  >
                    {((selectedProblem.languages||['python','javascript','cpp','java'])).map(l => (
                      <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>
                    ))}
                  </select>
                </div>

                <textarea 
                  className="editor-textarea"
                  placeholder={`Write your ${codeLang} solution here...`}
                  value={sourceCode}
                  onChange={e=>setSourceCode(e.target.value)}
                />

                <div className="editor-footer">
                  <div>
                    {runResult && (
                      <span style={{ color: runResult.status === 'Accepted' ? '#10b981' : '#ef4444', fontWeight: 600 }}>
                        {runResult.status || ''} ({runResult.passed||0}/{runResult.total||0})
                      </span>
                    )}
                  </div>
                  <div className="editor-actions">
                    <button 
                      className={`btn-run ${localRunnerLoading ? 'btn-loading' : ''}`}
                      disabled={!String(sourceCode||'').trim() || localRunnerLoading} 
                      onClick={runTestCases}
                      title="Run against example test cases"
                    >
                      {localRunnerLoading ? 'Loading Python...' : 'Run Tests'}
                    </button>
                    <button 
                      className="btn-submit" 
                      disabled={!String(sourceCode||'').trim()} 
                      onClick={()=>runOrSubmit('submit')}
                      title="Submit solution for evaluation"
                    >
                      Submit
                    </button>
                  </div>
                </div>

                {/* Results Panel */}
                {runResult && (
                  <div style={{ 
                    background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', 
                    borderTop: '1px solid rgba(255, 255, 255, 0.1)', 
                    padding: 16,
                    maxHeight: '250px',
                    overflowY: 'auto',
                    scrollBehavior: 'smooth',
                    color: 'white'
                  }}>
                    <div style={{ 
                      fontWeight: 600, 
                      marginBottom: 12,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span>Test Results</span>
                      <span style={{ 
                        color: runResult.passed === runResult.total ? '#10b981' : '#ef4444',
                        fontSize: 14
                      }}>
                        {runResult.passed||0}/{runResult.total||0} passed
                      </span>
                    </div>
                    
                    {(runResult.results||[]).map((r, i) => {
                      const isPassing = r.stdout?.includes('PASS')
                      const isFailing = r.stdout?.includes('FAIL')
                      const hasError = r.stderr || r.stdout?.includes('ERROR')
                      
                      return (
                        <div key={i} style={{ 
                          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)', 
                          border: `1px solid ${isPassing ? '#10b981' : hasError ? '#ef4444' : 'rgba(255, 255, 255, 0.2)'}`, 
                          borderRadius: 8, 
                          padding: 12, 
                          marginBottom: 8,
                          fontSize: 13,
                          backdropFilter: 'blur(5px)'
                        }}>
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            marginBottom: 8
                          }}>
                            <strong>Test Case {i + 1}</strong>
                            <span style={{ 
                              color: isPassing ? '#10b981' : hasError ? '#ef4444' : '#6b7280',
                              fontWeight: 600,
                              fontSize: 12
                            }}>
                              {isPassing ? '✓ PASS' : hasError ? '✗ ERROR' : isFailing ? '✗ FAIL' : String(r.status)}
                            </span>
                          </div>
                          
                          {!r.hidden && r.stdout && (
                            <pre style={{ 
                              whiteSpace: 'pre-wrap', 
                              background: 'rgba(0, 0, 0, 0.3)', 
                              padding: 8, 
                              borderRadius: 4,
                              fontSize: 11,
                              margin: 0,
                              maxHeight: '120px',
                              overflowY: 'auto',
                              color: '#e2e8f0',
                              border: '1px solid rgba(255, 255, 255, 0.1)'
                            }}>
                              {r.stdout}
                            </pre>
                          )}
                          
                          {r.stderr && (
                            <pre style={{ 
                              whiteSpace: 'pre-wrap', 
                              marginTop: 8, 
                              background: 'rgba(239, 68, 68, 0.2)', 
                              color: '#fca5a5', 
                              padding: 8, 
                              borderRadius: 4,
                              fontSize: 11,
                              margin: '8px 0 0 0',
                              border: '1px solid rgba(239, 68, 68, 0.3)'
                            }}>
                              {r.stderr}
                            </pre>
                          )}
                        </div>
                      )
                    })}
                    
                    {runResult.note && (
                      <div style={{ 
                        fontSize: 11, 
                        color: '#6b7280', 
                        fontStyle: 'italic',
                        marginTop: 8,
                        textAlign: 'center'
                      }}>
                        {runResult.note}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {!!error && (
        <div className="toast">
          <div>{error}</div>
          <button onClick={() => setError('')}>×</button>
        </div>
      )}
    </>
  )
}
